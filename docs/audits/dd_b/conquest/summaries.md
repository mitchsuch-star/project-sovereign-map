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
   controls: [Begin the 1805 Campaign]  [The School of War — a guided campaign]  [Continue](disabled: No saved campaign yet)  [Load a Campaign…](disabled: No saved campaign yet)  [Settings]  [Quit to Desktop]
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
   Ernest Meissonier — 1807, Friedland  ·  public domain
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
   Antoine-Jean Gros — Napoleon on the Field of Eylau  ·  public domain
── VersionLine (layer 0): unchanged
── MenuColumn (layer 0): unchanged
```

```
#0003  click Begin the 1805 Campaign  ->  ok
  (clicked at (456, 439))
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
   Britain + Austria + Russia
   0
   T:0
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   800
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) ──
   controls: [icon: Zoomed out as far as the map goes — the whole theatre is in  @(1794,992)](disabled: Zoomed out as far as the map goes — the whole theatre is in view)  [icon: The whole theatre is already in view @(1828,992)](disabled: The whole theatre is already in view)  [icon: Zoom in  (+) @(1862,992)]
── command window, new lines ──
   - Soult — Lorraine — 30,000 — Awaiting orders.
   - Davout — Rhineland — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Lorraine — 10,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Brunswick — Berlin — large force [partial]
   Mack — Swabia — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
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
   ─────────────────────────────────────
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: 100(1396,395)  45(1374,592)  30(1416,737)  20(1971,161)  18(1948,118)  15(2234,635)  12(1593,294)  10(1111,753)  10(1927,239)  5(1804,784)  Bernadotte(1930,451)  Deroy(1955,425)  ?(1959,325)  Brunswick(1958,287)  Mack(1853,430)  Ney(1814,397)  Davout(1839,371)  ?(1965,579)  Archduke John(1948,540)  Soult(1741,436)  Napoleon(1764,462)  Lannes(1800,497)  Murat(1838,471)  Massena(1910,589)  ?(2068,435)  ?(1959,376)  ?(1860,560)  ?(1893,372)  25k(1595,494)  12k(1551,454)  ?(1769,580)  12k(1693,420)  10k(1910,645)
```

```
#0004  type what can I do  ->  ok
  (typed and Enter)
view: <run>\frames\0004_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
── BottomLeftUI (layer 0): unchanged
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
#0005  type how strong is Mack and where is Vienna?  ->  ok
  (typed and Enter)
view: <run>\frames\0005_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok No, Sire — Mack stands at Swabia, not Vienna — large force; his works and stance are not in view.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► how strong is Mack and where is Vienna?
   No, Sire — Mack stands at Swabia, not Vienna — large force; his works and stance are not in view.
map: unchanged (53 labels)
```

```
#0006  type where is Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0006_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Vienna (held by Austria) adjoins Dresden, Bohemia, Moravia, Hungary.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► where is Vienna
   Vienna (held by Austria) adjoins Dresden, Bohemia, Moravia, Hungary.
map: unchanged (53 labels)
```

```
#0007  scroll 1950 480 up 3  ->  ok
  (scrolled up 3 at (1950, 480))
view: <run>\frames\0007_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0) ──
   controls: [icon: Zoom out  (−) @(1794,992)]  [icon: Fit Europe — the whole theatre  (Home re-centres) @(1828,992)]  [icon: Zoom in  (+) @(1862,992)]
── command window, last lines ──
   ► how strong is Mack and where is Vienna?
   No, Sire — Mack stands at Swabia, not Vienna — large force; his works and stance are not in view.
   ► where is Vienna
   Vienna (held by Austria) adjoins Dresden, Bohemia, Moravia, Hungary.
map names: Russia(2580,190)  Ottoman Empire(2362,783)  Prussia(2149,280)  Spain(1185,875)  Sweden(1905,27)  Saxony(2108,391)  Austria(2120,591)  France(1556,532)  Bavaria(1923,501)  Kingdom of Italy(1766,671)  Denmark(1738,68)  Papal States(1876,773)  Portugal(1112,811)  Britain(1397,286)  Hanover(1726,328)  Naples(1802,899)  Sardinia(1642,795)  Hesse(1904,389)  Holland(1738,373)  Switzerland(1759,560)
map pieces: 100(1323,382)  45(1298,612)  30(1347,781)  20(1995,108)  18(1965,58)  15(2303,663)  12(1553,264)  10(990,800)  10(1943,200)  5(1799,836)  Bernadotte(1948,446)  Deroy(1976,420)  ?(1980,297)  Brunswick(1981,258)  ?(1876,465)  Mack(1865,425)  Ney(1811,382)  Davout(1840,354)  ?(1980,594)  Archduke John(1968,554)  Soult(1726,428)  Napoleon(1754,455)  Lannes(1796,499)  Murat(1831,473)  Massena(1923,607)  ?(2108,425)  ?(1981,358)  ?(1884,637)  ?(1904,355)  25k(1556,499)  12k(1504,448)  ?(1759,594)  12k(1675,407)  10k(1923,671)
```

```
#0008  scroll 1950 480 up 8  ->  ok
  (scrolled up 8 at (1950, 480))
view: <run>\frames\0008_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► how strong is Mack and where is Vienna?
   No, Sire — Mack stands at Swabia, not Vienna — large force; his works and stance are not in view.
   ► where is Vienna
   Vienna (held by Austria) adjoins Dresden, Bohemia, Moravia, Hungary.
map names: Russia(2849,84)  Ottoman Empire(2553,890)  Prussia(2264,208)  Saxony(2208,357)  Austria(2225,630)  France(1459,549)  Bavaria(1956,508)  Kingdom of Italy(1743,739)  Denmark(1705,-80)  Papal States(1893,876)  Britain(1244,216)  Hanover(1689,272)  Naples(1793,1047)  Sardinia(1575,907)  Hesse(1931,355)  Holland(1706,333)  Switzerland(1734,588)
map pieces: 100(1143,353)  45(1107,666)  30(1174,895)  15(2472,734)  12(1454,193)  10(689,921)  10(1984,105)  5(1789,970)  Bernadotte(1990,437)  Deroy(2029,410)  ?(2035,232)  Brunswick(2035,196)  ?(1877,460)  Mack(1877,424)  Ney(1806,350)  Davout(1845,323)  ?(2018,635)  Archduke John(2018,599)  Soult(1689,413)  Napoleon(1727,386)  Lannes(1785,509)  Murat(1823,482)  Massena(1958,656)  ?(2208,397)  ?(2035,313)  ?(1943,629)  ?(1930,395)  25k(1458,505)  12k(1388,436)  ?(1733,627)  12k(1650,376)  10k(1957,739)
```

```
#0009  scroll 1950 480 up 10  ->  ok
  (scrolled up 10 at (1950, 480))
view: <run>\frames\0009_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► how strong is Mack and where is Vienna?
   No, Sire — Mack stands at Swabia, not Vienna — large force; his works and stance are not in view.
   ► where is Vienna
   Vienna (held by Austria) adjoins Dresden, Bohemia, Moravia, Hungary.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,299)  45(789,751)  15(2757,849)  12(1289,69)  Bernadotte(2062,426)  Deroy(2118,392)  ?(2127,138)  Brunswick(2126,103)  ?(1899,458)  Mack(1899,424)  Ney(1796,301)  Davout(1855,289)  ?(2102,711)  Archduke John(2101,677)  Soult(1627,391)  Napoleon(1704,369)  Lannes(1765,530)  Murat(1821,496)  Massena(2015,742)  ?(2376,360)  ?(2126,239)  ?(1994,711)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)  10k(2014,854)
```

```
#0010  type Ney and Davout, attack Mack together  ->  ok
  (typed and Enter)
view: <run>\frames\0010_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Ney (24,000; expect about 108,125 with the corps likely to arrive, up to 114,642 if all march) vs Mack (large force) at Swabia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10)
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
  What Swabia can feed is not known — the province is unscouted.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
  (Standing orders decide who marches: 'Sou
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Napoleon
   10,000 → 9,457
   Lannes
   18,000 → 16,777
   Davout
   26,000 → 24,586
   ⚔
   Ney ◆
   Mack ◆
   marched to the guns
   24,000 → 21,823 → 21,526 after the advance
   52,000 → 34,139
   marched to the guns
   marched to the guns
   +2 corps in reserve
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
   Britain + Austria + Russia
   +18
   T:0
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   533
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+6%)
   Ney delivers an effective strike. Ney gains the advantage over Mack. Casualties: Ney's army 5,357, Mack 17,861. Both armies remain in the field. Ney advances into Swabia. (297 lost to march)
   [Materiel] Guns, horses and stores lost with the fallen: France -267g, Austria -893g.
   Berthier: "You named Davout beside Ney, Sire — Ney takes the order; Davout marches with Ney already — the muster counts him."
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
   Murat could not reach the battlefield in time.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 24,000 (lead) + 70,017 committed (Davout, Lannes, Napoleon) = 94,017.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,180 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 2,177 | Mack 17,861
   Strength: Ney 24,000 → 21,823 → 21,526 after the advance | Mack 52,000 → 34,139
   Berthier: "Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arrived, Sire."
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Bernadotte(2062,426)  Deroy(2118,392)  ?(2127,138)  Brunswick(2126,103)  Mack(1918,369)  Ney +3(1899,408)  ?(2102,711)  Archduke John(2101,677)  Soult(1655,391)  Murat(1793,530)  Massena(2015,742)  ?(2376,360)  ?(2126,239)  ?(1994,711)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)  10k(2014,854)
```

```
#0011  click skip  ->  ERROR: no visible control's text holds "skip"
view: <run>\frames\0011_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A FIELD OF LEGEND IS WON
   FRANCE LOSSES
   AUSTRIA LOSSES
   5,357
   17,861
   Napoleon
   10,000 → 9,457
   Lannes
   18,000 → 16,777
   Davout
   26,000 → 24,586
   ⚔
   Ney ◆
   Mack ◆
   marched to the guns
   24,000 → 21,823 → 21,526 after the advance
   52,000 → 34,139
   marched to the guns
   marched to the guns
   +2 corps in reserve
   Soult — awaits explicit orders
   Berthier: “The Emperor watched this field. Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arrived, Sire.” / Mack: "A temporary derangement of the arithmetic. Vienna will understand."
   THE GREAT BATTLE OF SWABIA
   SWABIA · TURN 1
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 2,177 | Mack 17,861
   Strength: Ney 24,000 → 21,823 → 21,526 after the advance | Mack 52,000 → 34,139
   Berthier: "Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arrived, Sire."
map: unchanged (106 labels)
```

```
#0012  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0012_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 2,177 | Mack 17,861
   Strength: Ney 24,000 → 21,823 → 21,526 after the advance | Mack 52,000 → 34,139
   Berthier: "Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arrived, Sire."
map: unchanged (106 labels)
```

```
#0013  type where is Mack now?  ->  ok
  (typed and Enter)
view: <run>\frames\0013_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Mack of Austria is at Swabia — 34,139 men, confirmed.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► where is Mack now?
   Mack of Austria is at Swabia — 34,139 men, confirmed.
map: unchanged (106 labels)
```

```
#0014  type Davout, attack Mack and finish him  ->  ok
  (typed and Enter)
view: <run>\frames\0014_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Davout (24,586; expect about 111,136 with the corps likely to arrive, up to 114,738 if all march) vs Mack (34,139 men) at Swabia — the balance of force looks favorable.
  WILL JOIN — Ney: stands on the field and will fight beside him
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Davout' and he will march
  WILL JOIN — Lannes: stands on the field and will fight beside him
  WILL JOIN — Murat: will march to the sound of the guns — but he and Davout are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Davout' and it rises to about 100% (The corps system lowers the bar by 10)
  WILL NOT — Bernadotte: will not lift a finger for Marshal Davout
  WILL JOIN — Napoleon: stands on the field and will fight beside him
  The Emperor commands in person — every corps on this field fights +10% harder.
  The band weighs more than the men: all told, Davout's own modifiers weigh 10% against the attack.
  Swabia feeds 60,000 — the whole muster standing there would lose ~4,581 men a turn to short supply.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
  Napoleon shares the field at Swabia — his men will absorb part of any losses.


Davout holds them at Swabia while allies attack from Rhineland! (+1 coordination)

[Combat] Davout attacks cautiously at unfavorable odds on his 
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   16,777 → 16,430
   Ney
   21,526 → 21,080
   Murat
   22,000 → 21,818
   ⚔
   Davout ◆
   Mack ◆
   24,586 → 23,905
   34,139 → 6,793
   marched to the guns
   +1 corps in reserve — 196 lost
   Soult — awaits explicit orders
   THE GREAT SECOND BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 1
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 86 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Russia
   +36
   T:0
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   441
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   The Emperor commands in person — every corps on this field fights +10% harder.
   The band weighs more than the men: all told, Davout's own modifiers weigh 10% against the attack.
   Swabia feeds 60,000 — the whole muster standing there would lose ~4,581 men a turn to short supply.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Napoleon shares the field at Swabia — his men will absorb part of any losses.
   Davout holds them at Swabia while allies attack from Rhineland! (+1 coordination)
   [Combat] Davout attacks cautiously at unfavorable odds on his own numbers. (Cautious: -10% attack)
   [Combat] Davout's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Davout's attack! (+4%)
   Davout's forces press forward aggressively. Davout gains the advantage over Mack. Casualties: Davout's army 1,852, Mack 27,346. Both armies remain in the field. Swabia remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Materiel] Guns, horses and stores lost with the fallen: France -92g, Austria -1367g.
   [!] Mack's broken army flees to Munich! (67 lost to march) (recovering for 3 turns)
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 24,586 (lead) + 90,152 committed (Murat, Ney, Lannes, Napoleon) = 114,738.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 1,171 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Davout: "Precision carried it. It usually does."
   The corps system brought Murat in.
   Attack: Davout (Personality (cautious) -10%, Flanking +1%, The Emperor commands in person +10%)
   Casualties: Davout's own corps 681 | Mack 27,346
   Strength: Davout 24,586 → 23,905 | Mack 34,139 → 6,793
   Berthier: "Reinforcements from Murat bolstered Davout's position — though Soult never arrived, Sire."
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Bernadotte(2062,426)  Deroy(2118,392)  ?(2127,138)  Brunswick(2126,103)  Ney +4(1899,408)  ?(2102,711)  Archduke John(2101,677)  Soult(1655,391)  ?(1994,621)  Mack(1995,587)  Massena(2015,742)  ?(2376,360)  ?(2126,239)  ?(1994,711)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)  10k(2014,854)
```

```
#0015  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0015_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A FIELD OF LEGEND IS WON
   FRANCE LOSSES
   AUSTRIA LOSSES
   1,852
   27,346
   Lannes
   16,777 → 16,430
   Ney
   21,526 → 21,080
   Murat
   22,000 → 21,818
   ⚔
   Davout ◆
   Mack ◆
   24,586 → 23,905
   34,139 → 6,793
   marched to the guns
   +1 corps in reserve — 196 lost
   ROUTED
   Soult — awaits explicit orders
   Berthier: “Reinforcements from Murat bolstered Davout's position — though Soult never arrived, Sire.” / Mack: "I withdraw in perfect conformity with a plan I have just completed."
   THE GREAT SECOND BATTLE OF SWABIA
   SWABIA · TURN 1
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (107 labels)
```

```
#0016  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0016_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (107 labels)
```

```
#0017  type Murat, ride down Mack at Munich  ->  ok
  (typed and Enter)
view: <run>\frames\0017_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Murat (21,818; expect about 84,250 with the corps likely to arrive, up to 86,946 if all march) vs Mack (strength unknown) at Munich — the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 100%) (The corps system lowers the bar by 10)
  WILL NOT — Davout: has already marched this turn
  WILL NOT — Lannes: has already marched this turn
  WILL NOT — Bernadotte: will not lift a finger for Marshal Murat
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  WILL NOT — Napoleon: has already marched this turn
  Mack does not stand alone: at least 1 enemy corps within reach of Munich would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  The band weighs more than the men: the ground favors the defender (+25%, mountains).
  What Munich can feed is not known — the province is unscouted.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.

[!] Mack is EXPOSED! (Just retreated, no ally to cover)


[Combat] Murat leads the charge! (Aggressive: +15% attack)
[Terrain] Mack benefits from Mountains terrain (+25% defense)
[Combat] Murat's combined arms coordination! (+10% attack)
[Combat] Adjacent allies bolster Mur
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Ney
   21,080 → 21,058
   Massena
   42,000 → 41,910
   ⚔
   Murat ◆
   Mack ◆
   21,818 → 21,741 → 21,155 after the advance
   6,726 → 0
   marched to the guns
   marched to the guns
   THE GREAT BATTLE OF MUNICH
   click anywhere to skip ▸
   MUNICH · TURN 1
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 89 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Russia
   +39
   T:0
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   432
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   WILL JOIN — Ney: will march to the sound of the guns — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 100%) (The corps system lowers the bar by 10)
   WILL NOT — Davout: has already marched this turn
   WILL NOT — Lannes: has already marched this turn
   WILL NOT — Bernadotte: will not lift a finger for Marshal Murat
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   WILL NOT — Napoleon: has already marched this turn
   Mack does not stand alone: at least 1 enemy corps within reach of Munich would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
   The band weighs more than the men: the ground favors the defender (+25%, mountains).
   What Munich can feed is not known — the province is unscouted.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [!] Mack is EXPOSED! (Just retreated, no ally to cover)
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Terrain] Mack benefits from Mountains terrain (+25% defense)
   [Combat] Murat's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Murat's attack! (+8%)
   Murat engages in solid combat. Murat decisively defeats Mack! Mack's army is destroyed. Murat's army suffered 189 casualties. Mack's army is destroyed! Murat advances into Munich. (586 lost to march) Munich remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Materiel] Guns, horses and stores lost with the fallen: France -9g, Austria -367g.
   ★ Enemy army destroyed! ★
   ⚔ View the field
   [1/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 21,818 (lead) + 65,128 committed (Ney, Massena) = 86,946.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 112 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Murat: "Their squares were a suggestion. My cavalry declined it."
   Berthier: the corps marched apart and arrived together.
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 77 | Mack 6,726
   Strength: Murat 21,818 → 21,741 → 21,155 after the advance | Mack 6,726 → 0
   Berthier: "Reinforcements! Ney and Massena marched onto the field beside Murat. The enemy's advantage melted away."
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Bernadotte(2062,426)  Deroy(2118,392)  ?(2127,138)  Brunswick(2126,103)  Davout(1870,455)  Lannes(1899,421)  Napoleon(1897,389)  ?(2102,711)  Archduke John(2101,677)  Soult(1655,391)  Ney(1966,618)  Murat(1994,584)  Massena(2022,550)  ?(2376,360)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)  10k(2014,854)
```

```
#0018  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Murat ◆' (Control, layer 121))
view: <run>\frames\0018_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A FIELD OF LEGEND IS WON
   FRANCE LOSSES
   AUSTRIA LOSSES
   189
   6,726
   Ney
   21,080 → 21,058
   Massena
   42,000 → 41,910
   ⚔
   Murat ◆
   Mack ◆
   21,818 → 21,741 → 21,155 after the advance
   6,726 → 0
   marched to the guns
   marched to the guns
   DESTROYED
   Berthier: “Reinforcements! Ney and Massena marched onto the field beside Murat. The enemy's advantage melted away.”
   THE GREAT BATTLE OF MUNICH
   MUNICH · TURN 1
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 77 | Mack 6,726
   Strength: Murat 21,818 → 21,741 → 21,155 after the advance | Mack 6,726 → 0
   Berthier: "Reinforcements! Ney and Massena marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (109 labels)
```

```
#0019  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0019_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 77 | Mack 6,726
   Strength: Murat 21,818 → 21,741 → 21,155 after the advance | Mack 6,726 → 0
   Berthier: "Reinforcements! Ney and Massena marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (109 labels)
```

```
#0020  type Soult, march to Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0020_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult begins march to Swabia. Moves to Swabia. "Soult, march to Swabia." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   432
   Inf:
   80,000
   Cav:
   15,000
   Art:
   10,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, march to Swabia
   Soult begins march to Swabia. Moves to Swabia. "Soult, march to Swabia." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
   [0/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Bernadotte(2062,426)  Deroy(2118,392)  ?(2127,138)  Brunswick(2126,103)  Davout +3(1899,432)  ?(2102,711)  Archduke John(2101,677)  Ney(1966,618)  Murat(1994,584)  Massena(2022,550)  ?(2376,360)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)  ?(2015,854)
```

```
#0021  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0021_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 1
   AUSTRIA / ──────────────────────────── / - Archduke Charles moves to Tyrol / - Archduke John attacks Bernadotte /     Battle of Franconia /     Archduke John: 2,304 casualties, 17,696 remaining /     Bernadotte: 2,230 casualties, 14,770 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Bernadotte (Outnumbered (cautious) +10%) /     Archd …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 88 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   -54
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 112 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Murat: "Their squares were a suggestion. My cavalry declined it."
   Berthier: the corps marched apart and arrived together.
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Mack (Terrain (Mountains) +25%)
   Casualties: Murat's own corps 77 | Mack 6,726
   Strength: Murat 21,818 → 21,741 → 21,155 after the advance | Mack 6,726 → 0
   Berthier: "Reinforcements! Ney and Massena marched onto the field beside Murat. The enemy's advantage melted away."
   ► Soult, march to Swabia
   Soult begins march to Swabia. Moves to Swabia. "Soult, march to Swabia." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -442g | Other: +1319g | Upkeep: -3644g | Net: -486g
   Treasury: -54g
   WARNING: Treasury in deficit! Upkeep costs halved as mercy.
   Actions refreshed: 4/4
   Bernadotte's army is recovering. Effectiveness penalty: -30%.
   Supply shortage at Franconia: Archduke Charles loses 205 troops
   Supply shortage at Swabia: Davout loses 1,116 troops
   Supply shortage at Swabia: Soult loses 1,358 troops
   Supply shortage at Swabia: Lannes loses 767 troops
   Supply shortage at Swabia: Bernadotte loses 378 troops
   Supply shortage at Swabia: Napoleon loses 432 troops
   Supply shortage at Munich: Ney loses 1,209 troops
   Supply shortage at Munich: Murat loses 1,215 troops
   Supply shortage at Munich: Massena loses 2,407 troops
   Supply shortage at Munich: Deroy loses 1,263 troops
   Soult holds at Swabia, per your orders — the guns at Munich did not move him.
   Garrison at Milan reinforced: 5,000 -> 7,000
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Swabia. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Munich. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Archduke Charles(2090,426)  ?(2127,138)  Brunswick(2126,103)  Davout +4(1899,408)  ?(2102,711)  Archduke John(2101,677)  Ney(1966,618)  Murat(1966,584)  Massena(2022,550)  Deroy(2023,516)  Dumonceau(1660,203)  Teulie(2015,742)  ?(2376,360)  ?(2126,239)  10k(1994,711)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  7k(2015,854)
```

```
#0022  scroll 1280 400 down 5  ->  ok
  (scrolled down 5 at (1280, 400))
view: <run>\frames\0022_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Swabia. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Munich. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map: unchanged (108 labels)
```

```
#0023  scroll 1430 420 down 10  ->  ok
  (scrolled down 10 at (1430, 420))
view: <run>\frames\0023_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Swabia. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Munich. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map: unchanged (108 labels)
```

```
#0024  click_at 1683 490  ->  ok
  (clicked at (1683, 490) on ContentLabel 'AUSTRIA
────────────────────────────
- A' (RichTextLabel, layer 118))
view: <run>\frames\0024_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Swabia. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Munich. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map: unchanged (108 labels)
```

```
#0025  scroll 1828 548 down 5  ->  ok
  (scrolled down 5 at (1828, 548))
view: <run>\frames\0025_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Swabia. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Munich. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map: unchanged (108 labels)
```

```
#0026  scroll 1828 548 down 10  ->  ok
  (scrolled down 10 at (1828, 548))
view: <run>\frames\0026_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Swabia. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Munich. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map: unchanged (108 labels)
```

```
#0027  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0027_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Bernadotte ◆
   Archduke Charles ◆
   14,770 → 8,135
   54,000 → 52,350 → 50,780 after the advance
   Soult — awaits explicit orders
   SECOND BATTLE OF FRANCONIA
   click anywhere to skip ▸
   FRANCONIA · TURN 1
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   INTELLIGENCE
   Archduke Charles — Franconia — 50,575 [confirmed]
   Deroy — Munich — 20,737 [confirmed]
   Brunswick — Berlin — large force [partial]
   Archduke John — Tyrol — small force [partial]
   TURN EVENTS
   Bernadotte's army is recovering. Effectiveness penalty: -30%.
   Supply cost you 8,882 men, at Swabia and Munich.
   Soult holds at Swabia, per your orders — the guns at Munich did not move him.
   DIPLOMATIC EVENTS
   War exhaustion grows — Austria nears breaking point (exhaustion: 37).
   War exhaustion grows — Austria nears breaking point (exhaustion: 44).
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Swabia. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Munich. The Kingdom of Italy pays them; their dead will be its grief.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders
   - Ottoman — Open Borders
   - Portugal — Open Borders
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms (+36)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 88/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (108 labels)
```

```
#0028  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Bernadotte ◆' (Control, layer 121))
view: <run>\frames\0028_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS LOST
   FRANCE LOSSES
   AUSTRIA LOSSES
   6,635
   1,650
   ⚔
   Bernadotte ◆
   Archduke Charles ◆
   14,770 → 8,135
   54,000 → 52,350 → 50,780 after the advance
   ROUTED
   Soult — awaits explicit orders
   Berthier: “Bernadotte stood alone, Sire. Soult never came.” / Archduke Charles: "Your marshals are bold. Boldness is not a plan."
   SECOND BATTLE OF FRANCONIA
   FRANCONIA · TURN 1
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 88/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (108 labels)
```

```
#0029  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0029_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   -54
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 88/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (108 labels)
```

```
#0030  click Envoys  ->  ok
  (clicked at (3387, 18))
view: <run>\frames\0030_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
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
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 88/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (108 labels)
```

```
#0031  click#2 Accept  ->  ok
  (clicked at (1433, 721))
view: <run>\frames\0031_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Open ▸
   Turn 1
   Incoming proposal: Open Borders Agreement
   A COURT WRITES (1)
   Ottoman Empire writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Ottoman Empire
   Proposal
   Open ▸
   Turn 1
   Incoming proposal: Open Borders Agreement
   Reis Efendi, serene and unhurried: "The Porte has outlasted a hundred ascendancies by keeping its counsel with each at its noon; France's noon has come, and the Sublime Porte observes it without haste. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders
   or click the letter to reply in full
   controls: {ACTIVE}  {WAITING}  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 88 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
map: unchanged (108 labels)
```

```
#0032  click Accept  ->  ok
  (clicked at (1433, 525))
view: <run>\frames\0032_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (1)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   ACTIVE
   Prussia
   Proposal
   Open ▸
   Turn 1
   Incoming proposal: Open Borders Agreement
   controls: {ACTIVE}  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 88 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
map: unchanged (108 labels)
```

```
#0033  click ACTIVE  ->  ok
  (clicked at (1829, 283))
view: <run>\frames\0033_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Open Borders Agreement / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders /  / Hardenberg, stiffly: "Prussia's interest is the Rhine at peace and the army at home; Berlin signs where those two meet. Open the borders." /  / An unexpected overture. There may be hidden motives worth examining. /  / This offer will  …
   controls: [Accept]  [Counter]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   -54
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
map: unchanged (108 labels)
```

```
#0034  click Accept  ->  ok
  (clicked at (1604, 687))
view: <run>\frames\0034_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 88 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3445,62)]  [icon: Treaty with Portugal @(3487,62)]  [icon: Treaty with Ottoman @(3529,62)]  [icon: Treaty with Prussia @(3571,62)]  [icon: Diplomatic Action Accepted @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   +36
   T:1
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Archduke John — Tyrol — small force [partial]
   TURN EVENTS
   Bernadotte's army is recovering. Effectiveness penalty: -30%.
   Supply cost you 8,882 men, at Swabia and Munich.
   Soult holds at Swabia, per your orders — the guns at Munich did not move him.
   DIPLOMATIC EVENTS
   War exhaustion grows — Austria nears breaking point (exhaustion: 37).
   War exhaustion grows — Austria nears breaking point (exhaustion: 44).
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
   An envoy from Prussia has arrived with a proposal.
   An envoy from the Ottoman Empire has arrived with a proposal.
   An envoy from Portugal has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Swabia. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Massena at Munich. The Kingdom of Italy pays them; their dead will be its grief.
   BLOCKADE: Britain closes France's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Holland's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Prussia — Open Borders
   - Ottoman — Open Borders
   - Portugal — Open Borders
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms (+36)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 88/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
map: unchanged (108 labels)
```

```
#0035  click_at 3445 62  ->  ok
  (clicked at (3445, 62) on @Button@1322  (Button, layer 75))
view: <run>\frames\0035_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 88 / 100
   Turn 2 — Early October 1805
   Imperial Box
   Bernadotte — free attack!
   T1
   Bernadotte earned a free attack from his defensive victory — Archduke Charles stands within reach at Franconia. Use it THIS turn or the opportunity expires.
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3445,62)]  [icon: Treaty with Portugal @(3487,62)]  [icon: Treaty with Ottoman @(3529,62)]  [icon: Treaty with Prussia @(3571,62)]  [icon: Diplomatic Action Accepted @(3613,62)]  [Strike Archduke Charles — free]  [Keep]  [Acknowledge]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
map: unchanged (108 labels)
```

```
#0036  type Soult, support Ney  ->  ok
  (typed and Enter)
view: <run>\frames\0036_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult moves to support Ney (at Munich). Moves to Munich. Soult holds your written order: when Ney leads a battle within reach, he will march to the guns. The order lapses of itself once Ney is out of danger — name a duration to hold him to it. "Soult, support Ney." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
── TopBar (layer 75) ──
   DP: 7/7
   Threat 88 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3445,62)]  [icon: Treaty with Portugal @(3487,62)]  [icon: Treaty with Ottoman @(3529,62)]  [icon: Treaty with Prussia @(3571,62)]  [icon: Diplomatic Action Accepted @(3613,62)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   6
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, support Ney
   Soult moves to support Ney (at Munich). Moves to Munich. Soult holds your written order: when Ney leads a battle within reach, he will march to the guns. The order lapses of itself once Ney is out of danger — name a duration to hold him to it. "Soult, support Ney." Understood to the letter. (1 AP — Soult executes precise orders with fewer couriers.)
   [3/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Archduke Charles(2090,426)  ?(2127,138)  Brunswick(2126,103)  Davout +3(1899,432)  ?(2102,711)  Archduke John(2101,677)  Deroy(2023,532)  Ney +3(1994,571)  Dumonceau(1660,203)  Teulie(2015,742)  ?(2376,360)  ?(2126,239)  10k(1994,711)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  7k(2015,854)
```

```
#0037  type Ney, attack Archduke Charles in Franconia  ->  ok
  (typed and Enter)
view: <run>\frames\0037_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Ney (19,849; expect about 147,126 with the corps likely to arrive, up to 165,645 if all march) vs Archduke Charles (50,575 men) at Franconia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  WILL JOIN — Soult: marches under your written support order — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 100%) (The corps system lowers the bar by 10)
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — he will NOT make it from the mountains at Munich in time; order 'Murat, support Ney' and it rises to about 47% (The corps system lowers the bar by 10)
  WILL NOT — Bernadotte: is in no condition to fight
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 96%) (The corps system lowers the bar by 10)
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  Archduke Charles does not stand alone: at least 1 enemy corps within reach of Franconia would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  The Emperor commands in 
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Davout
   22,789 → 21,999
   Soult
   26,329 → 25,873
   Massena
   39,503 → 38,130
   ⚔
   Ney ◆
   Archduke Charles ◆
   marched to the guns
   19,849 → 18,702 → 18,515 after the advance
   50,575 → 29,942
   marched to the guns
   marched to the guns
   +2 corps in reserve — 1,061 lost
   Murat — could not reach the field
   THE GREAT THIRD BATTLE OF FRANCONIA
   click anywhere to skip ▸
   FRANCONIA · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 96 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3445,62)]  [icon: Treaty with Portugal @(3487,62)]  [icon: Treaty with Ottoman @(3529,62)]  [icon: Treaty with Prussia @(3571,62)]  [icon: Diplomatic Action Accepted @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Russia
   +39
   T:1
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   -235
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+2%)
   Ney attacks with overwhelming force. Ney gains the advantage over Archduke Charles. Casualties: Ney's army 4,827, Archduke Charles 20,633. Both armies remain in the field.
   ArchdukeCharles's regiments close ranks — they will not break. (Habsburg Resolve: holds to 15% morale) Ney advances into Franconia. (187 lost to march)
   [Materiel] Guns, horses and stores lost with the fallen: France -241g, Austria -1031g.
   Soult answered the guns and stands at Franconia; his support order stands and resumes next turn.
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Soult's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat could not reach the battlefield in time.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 19,849 (lead) + 130,160 committed (Davout, Soult, Lannes, Massena, Napoleon) = 150,009.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,680 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They broke like green wood, Sire. I want the pursuit."
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Ney's own corps 1,147 | Archduke Charles 20,633
   Strength: Ney 19,849 → 18,702 → 18,515 after the advance | Archduke Charles 50,575 → 29,942
   Berthier: "Davout, Soult, Lannes, Massena and Napoleon's timely arrival aided Ney. Murat, however, was conspicuously absent."
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Archduke Charles(2145,297)  Ney +5(2090,379)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  ?(2102,711)  Archduke John(2101,677)  Murat(1966,618)  Deroy(2023,584)  Dumonceau(1660,203)  Teulie(2015,742)  ?(2376,360)  ?(2126,239)  10k(1994,711)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  7k(2015,854)
```

```
#0038  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Ney ◆' (Control, layer 121))
view: <run>\frames\0038_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A FIELD OF LEGEND IS WON
   FRANCE LOSSES
   AUSTRIA LOSSES
   4,827
   20,633
   Davout
   22,789 → 21,999
   Soult
   26,329 → 25,873
   Massena
   39,503 → 38,130
   ⚔
   Ney ◆
   Archduke Charles ◆
   marched to the guns
   19,849 → 18,702 → 18,515 after the advance
   50,575 → 29,942
   marched to the guns
   marched to the guns
   +2 corps in reserve — 1,061 lost
   Murat — could not reach the field
   Berthier: “Davout, Soult, Lannes, Massena and Napoleon's timely arrival aided Ney. Murat, however, was conspicuously absent.” / Archduke Charles: "Austria endures. It is the thing we do best."
   THE GREAT THIRD BATTLE OF FRANCONIA
   FRANCONIA · TURN 2
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Ney's own corps 1,147 | Archduke Charles 20,633
   Strength: Ney 19,849 → 18,702 → 18,515 after the advance | Archduke Charles 50,575 → 29,942
   Berthier: "Davout, Soult, Lannes, Massena and Napoleon's timely arrival aided Ney. Murat, however, was conspicuously absent."
map: unchanged (107 labels)
```

```
#0039  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0039_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Ney's own corps 1,147 | Archduke Charles 20,633
   Strength: Ney 19,849 → 18,702 → 18,515 after the advance | Archduke Charles 50,575 → 29,942
   Berthier: "Davout, Soult, Lannes, Massena and Napoleon's timely arrival aided Ney. Murat, however, was conspicuously absent."
map: unchanged (107 labels)
```

```
#0040  type Davout, attack Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0040_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Davout (21,999; expect about 160,932 with the corps likely to arrive, up to 187,587 if all march) vs Archduke Charles (29,942 men) at Franconia — the balance of force looks favorable.
  WILL JOIN — Ney: stands on the field and will fight beside him
  WILL JOIN — Soult: stands on the field and will fight beside him
  WILL JOIN — Lannes: stands on the field and will fight beside him
  WILL JOIN — Murat: will march to the sound of the guns — he will NOT make it from the mountains at Munich in time; order 'Murat, support Davout' and it rises to about 47% (The corps system lowers the bar by 10)
  WILL NOT — Bernadotte: is in no condition to fight
  WILL JOIN — Massena: stands on the field and will fight beside him
  WILL JOIN — Napoleon: stands on the field and will fight beside him
  Archduke Charles does not stand alone: at least 1 enemy corps within reach of Franconia would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  The Emperor commands in person — every corps on this field fights +10% harder.
  The band weighs more than the men: all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +3% on the defense (his stance, his character and his works).
  Franconia feeds 60,000 — the whole muster standing there would lose ~8,869 men a turn to short supply.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart 
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Ney
   18,515 → 18,319
   Soult
   25,873 → 25,654
   Massena
   38,130 → 37,805
   ⚔
   Davout ◆
   Archduke Charles ◆
   21,999 → 21,689
   29,942 → 11,071
   +2 corps in reserve — 247 lost
   Murat — could not reach the field
   FOURTH BATTLE OF FRANCONIA
   click anywhere to skip ▸
   FRANCONIA · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 100 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3445,62)]  [icon: Treaty with Portugal @(3487,62)]  [icon: Treaty with Ottoman @(3529,62)]  [icon: Treaty with Prussia @(3571,62)]  [icon: Diplomatic Action Accepted @(3613,62)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Russia
   +42
   T:1
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   -299
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Davout, attack Archduke Charles
   ⚔ Fourth Battle of Franconia ⚔
   MUSTER — Davout (21,999; expect about 160,932 with the corps likely to arrive, up to 187,587 if all march) vs Archduke Charles (29,942 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: stands on the field and will fight beside him
   WILL JOIN — Soult: stands on the field and will fight beside him
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL JOIN — Murat: will march to the sound of the guns — he will NOT make it from the mountains at Munich in time; order 'Murat, support Davout' and it rises to about 47% (The corps system lowers the bar by 10)
   WILL NOT — Bernadotte: is in no condition to fight
   WILL JOIN — Massena: stands on the field and will fight beside him
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   Archduke Charles does not stand alone: at least 1 enemy corps within reach of Franconia would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
   The Emperor commands in person — every corps on this field fights +10% harder.
   The band weighs more than the men: all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~8,869 men a turn to short supply.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Napoleon shares the field at Franconia — his men will absorb part of any losses.
   Davout holds them at Franconia while allies attack from Munich! (+1 coordination)
   [Combat] Davout attacks cautiously at unfavorable odds on his own numbers. (Cautious: -10% attack)
   [Combat] Adjacent allies bolster Davout's attack! (+2%)
   Davout's forces press forward aggressively. Davout gains the advantage over Archduke Charles. Casualties: Davout's army 1,297, Archduke Charles 18,871. Both armies remain in the field. Franconia remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Materiel] Guns, horses and stores lost with the fallen: France -64g, Austria -943g.
   [!] Archduke Charles's broken army flees to Tyrol! (recovering for 2 turns)
   ⚔ View the field
   [1/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Murat could not reach the battlefield in time.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout fought with Ney, Soult, Lannes, Massena and Napoleon beside him — massed effective strength: 21,999 (lead) + 132,302 committed (Ney, Soult, Lannes, Massena, Napoleon) = 154,301.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's supporting allies lost 987 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Davout: "Victory, at an acceptable price. The pickets are already posted."
   Attack: Davout (Personality (cautious) -10%, Flanking +1%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Davout's own corps 310 | Archduke Charles 18,871
   Strength: Davout 21,999 → 21,689 | Archduke Charles 29,942 → 11,071
   Berthier: "Davout fought without Murat's support. The roads, or the will, proved insufficient."
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney +5(2090,379)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  ?(2084,711)  Archduke Charles(2084,677)  ?(2119,711)  Archduke John(2119,642)  Murat(1966,618)  Deroy(2023,584)  Dumonceau(1660,203)  Teulie(2015,742)  ?(2376,360)  ?(2126,239)  10k(1994,711)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  7k(2015,854)
```

```
#0041  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Davout ◆' (Control, layer 121))
view: <run>\frames\0041_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS OURS
   FRANCE LOSSES
   AUSTRIA LOSSES
   1,297
   18,871
   Ney
   18,515 → 18,319
   Soult
   25,873 → 25,654
   Massena
   38,130 → 37,805
   ⚔
   Davout ◆
   Archduke Charles ◆
   21,999 → 21,689
   29,942 → 11,071
   +2 corps in reserve — 247 lost
   ROUTED
   Murat — could not reach the field
   Berthier: “Davout fought without Murat's support. The roads, or the will, proved insufficient.” / Archduke Charles: "An army preserved is a battle not yet lost."
   FOURTH BATTLE OF FRANCONIA
   FRANCONIA · TURN 2
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Davout's own corps 310 | Archduke Charles 18,871
   Strength: Davout 21,999 → 21,689 | Archduke Charles 29,942 → 11,071
   Berthier: "Davout fought without Murat's support. The roads, or the will, proved insufficient."
map: unchanged (108 labels)
```

```
#0042  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0042_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Davout's own corps 310 | Archduke Charles 18,871
   Strength: Davout 21,999 → 21,689 | Archduke Charles 29,942 → 11,071
   Berthier: "Davout fought without Murat's support. The roads, or the will, proved insufficient."
map: unchanged (108 labels)
```

```
#0043  type Lannes, march into Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0043_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Not enough actions! Need 2, have 1 — Lannes cannot march to Bohemia today.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, march into Bohemia
   Not enough actions! Need 2, have 1 — Lannes cannot march to Bohemia today.
map: unchanged (108 labels)
```

```
#0044  type Lannes, move to Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0044_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok Lannes moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) (148 lost to march)
Carniola, Hungary lie undefended — an attack takes any of them.
Your forces have taken Bohemia. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Lannes has taken Bohemia
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+800 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 100 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   -299
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   WILL JOIN — Massena: stands on the field and will fight beside him
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   Archduke Charles does not stand alone: at least 1 enemy corps within reach of Franconia would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
   The Emperor commands in person — every corps on this field fights +10% harder.
   The band weighs more than the men: all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~8,869 men a turn to short supply.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Napoleon shares the field at Franconia — his men will absorb part of any losses.
   Davout holds them at Franconia while allies attack from Munich! (+1 coordination)
   [Combat] Davout attacks cautiously at unfavorable odds on his own numbers. (Cautious: -10% attack)
   [Combat] Adjacent allies bolster Davout's attack! (+2%)
   Davout's forces press forward aggressively. Davout gains the advantage over Archduke Charles. Casualties: Davout's army 1,297, Archduke Charles 18,871. Both armies remain in the field. Franconia remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Materiel] Guns, horses and stores lost with the fallen: France -64g, Austria -943g.
   [!] Archduke Charles's broken army flees to Tyrol! (recovering for 2 turns)
   ⚔ View the field
   [1/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Murat could not reach the battlefield in time.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout fought with Ney, Soult, Lannes, Massena and Napoleon beside him — massed effective strength: 21,999 (lead) + 132,302 committed (Ney, Soult, Lannes, Massena, Napoleon) = 154,301.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's supporting allies lost 987 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Davout: "Victory, at an acceptable price. The pickets are already posted."
   Attack: Davout (Personality (cautious) -10%, Flanking +1%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Davout's own corps 310 | Archduke Charles 18,871
   Strength: Davout 21,999 → 21,689 | Archduke Charles 29,942 → 11,071
   Berthier: "Davout fought without Murat's support. The roads, or the will, proved insufficient."
   ► Lannes, march into Bohemia
   Not enough actions! Need 2, have 1 — Lannes cannot march to Bohemia today.
   ► Lannes, move to Bohemia
   → Lannes moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) (148 lost to march)
   Carniola, Hungary lie undefended — an attack takes any of them.
   Your forces have taken Bohemia. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [0/4 actions remaining]
   Your forces await orders: Plunder or Secure?
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Lannes(2277,485)  Ney +4(2090,379)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  ?(2084,711)  Archduke Charles(2084,677)  ?(2119,711)  Archduke John(2119,642)  Murat(1966,618)  Deroy(2023,584)  Dumonceau(1660,203)  Teulie(2015,742)  ?(2376,360)  ?(2470,651)  ?(2126,239)  10k(1994,711)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  7k(2015,854)
```

```
#0045  click PLUNDER  ->  ok
  (clicked at (1653, 598))
view: <run>\frames\0045_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 100 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bernadotte — free attack! @(3445,62)]  [icon: Treaty with Portugal @(3487,62)]  [icon: Treaty with Ottoman @(3529,62)]  [icon: Treaty with Prussia @(3571,62)]  [icon: Diplomatic Action Accepted @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   +49
   T:1
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   501
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   You order your troops to plunder the region!
   Lannes's troops plunder Bohemia! Gained 800 gold. Buildings destroyed. Stability set to 10.
map: unchanged (109 labels)
```

```
#0046  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0046_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 2
   BAVARIA / ──────────────────────────── / - Deroy moves to Franconia / - Deroy holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 97 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,654
   Inf:
   84,550
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Davout: "Victory, at an acceptable price. The pickets are already posted."
   Attack: Davout (Personality (cautious) -10%, Flanking +1%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Davout's own corps 310 | Archduke Charles 18,871
   Strength: Davout 21,999 → 21,689 | Archduke Charles 29,942 → 11,071
   Berthier: "Davout fought without Murat's support. The roads, or the will, proved insufficient."
   ► Lannes, march into Bohemia
   Not enough actions! Need 2, have 1 — Lannes cannot march to Bohemia today.
   ► Lannes, move to Bohemia
   → Lannes moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) (148 lost to march)
   Carniola, Hungary lie undefended — an attack takes any of them.
   Your forces have taken Bohemia. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [0/4 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to plunder the region!
   Lannes's troops plunder Bohemia! Gained 800 gold. Buildings destroyed. Stability set to 10.
   ► end turn
   ═══════════════════════════════════════
   TURN 3 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Occupation: -50g | Admiralty: -90g | Blockade: -281g | Other: +1423g | Upkeep: -1439g | Net: +2153g
   Treasury: 2,654g
   Actions refreshed: 4/4
   Bernadotte's army is recovering. Effectiveness penalty: -15%.
   [!] Bernadotte's Counter-Punch opportunity has expired! (Must use immediately after defending)
   Bavaria completes a market at Franconia.
   Bavaria completes a market at Munich.
   Supply shortage at Franconia: Ney loses 1,063 troops
   Supply shortage at Franconia: Davout loses 1,259 troops
   Supply shortage at Franconia: Soult loses 1,490 troops
   Supply shortage at Franconia: Massena loses 2,195 troops
   Supply shortage at Franconia: Napoleon loses 485 troops
   Supply shortage at Franconia: Deroy loses 1,190 troops
   Soult's quarry has shifted to Franconia, Sire — he follows the letter of your order, not his instincts.
   Garrison at Milan reinforced: 7,000 -> 9,000
   Britain subsidizes Austria with 200 gold.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Murat is eyeing Archduke Charles's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Lannes(2277,485)  Deroy(2118,318)  Ney +4(2090,379)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  ?(2084,711)  Archduke Charles(2084,677)  ?(2119,711)  Archduke John(2119,642)  Murat(1994,618)  Dumonceau(1660,203)  Teulie(2015,742)  ?(2376,360)  ?(2470,651)  ?(2126,239)  10k(1994,711)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  9k(2015,854)
```

```
#0047  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0047_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,654
   Inf:
   84,550
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Brunswick — Berlin — large force [partial]
   Archduke Charles — Tyrol — small force [partial]
   Archduke John — Tyrol — small force [partial]
   Vienna garrison — Vienna — garrison — substantial force [partial]
   TURN EVENTS
   Bernadotte's army is recovering. Effectiveness penalty: -15%.
   [!] Bernadotte's Counter-Punch opportunity has expired! (Must use immediately after defending)
   Supply cost you 6,492 men, at Franconia.
   Soult's quarry has shifted to Franconia, Sire — he follows the letter of your order, not his instincts.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Murat is eyeing Archduke Charles's position at Tyrol. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   Sire — Portugal and France have signed the Open Borders Agreement.
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Prussia and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 74).
   War exhaustion grows — Austria nears breaking point (exhaustion: 92).
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Denmark — Non Aggression
   - Saxony — Open Borders
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Bohemia) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Dictated Terms (+48)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
map: unchanged (109 labels)
```

```
#0048  click Envoys  ->  ok
  (clicked at (3391, 18))
view: <run>\frames\0048_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
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
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
map: unchanged (109 labels)
```

```
#0049  click#1 Accept  ->  ok
  (clicked at (1433, 421))
view: <run>\frames\0049_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
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
   Threat 97 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
map: unchanged (109 labels)
```

```
#0050  click Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0050_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 97 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (109 labels)
```

```
#0051  click Generals  ->  ok
  (clicked at (228, 18))
view: <run>\frames\0051_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 97 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Treasury in deficit @(3358,64)]  [icon: Envoy from Denmark @(3400,64)]  [icon: Envoy from Saxony @(3442,64)]  [icon: Marshal Murat seeks an audience @(3484,64)]  [icon: Treaty with Portugal @(3526,64)]  [icon: Treaty with Ottoman @(3568,64)]  [+2]
── MarshalManagement (layer 50) ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Press G to close. /  / SEEKS AN AUDIENCE — Murat /   / [5] Murat    [Cavalry]  France / The Cavalry Reserve - screening the Black Forest feint while the army wheels north of the Danube. / Aggressive: +15% attack, +5% more in aggressive stance. Fortify capped at 10%. Grows restless if idle too long. / Cava …
   controls: [Pin]  [icon @(2213,236)]  <Hear him — he seeks an audience>  <Fortify>  <Fortify>  <Commission a Marshal…>  <Fortify>  <Fortify>  <Fortify>  <Fortify>  <Fortify>  <Fortify>  <Drill>  <Fortify>
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (109 labels)
```

```
#0052  click Hear him  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0052_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=['generals'], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114) ──
   MURAT — Marshal Murat seeks an audience
   Give him a command is closed — Tyrol is held in force — sending him there needs an order of its own.
   "Sire — I have earned better than to watch Ney take the field while I hold a road." /  / Sire, Murat has expressed... displeasure about Ney's recent recognition. He requests a command worthy of his talents.
   Free, and it fixes nothing. For 2 more turns he brings NONE of his 19,940 men to any battle Ney leads, and the quarrel may harden further.
   His patience is bought — the grievance shortens by 2 turns, and for 6 turns the quarrel cannot harden further.
   controls: [Let it stand   [Free]]  [Promise Glory   [1 AP]]  [Later (he will return)]
── TopBar (layer 75) [under a modal]: unchanged
── MarshalManagement (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,654
   Inf:
   84,550
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (109 labels)
```

```
#0053  click Later  ->  ok
  (clicked at (1829, 716))
view: <run>\frames\0053_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50): unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,654
   Inf:
   84,550
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (109 labels)
```

```
#0054  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0054_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50): unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (109 labels)
```

```
#0055  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0055_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   +49
   T:1
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (109 labels)
```

```
#0056  type Murat, attack Archduke Charles in Tyrol  ->  ok
  (typed and Enter)
view: <run>\frames\0056_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok MUSTER — Murat (19,940; expect about 100,253 with the corps likely to arrive, up to 103,878 if all march) vs Archduke Charles (small force) at Tyrol — the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns — but Murat resents him, and will make no use of him: NOTHING of his weight reaches the fighting — likely to make it in time (about 100%) (The corps system lowers the bar by 10)
  WILL JOIN — Davout: is willing to march if the roads allow — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Murat' and he will march
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
  Archduke Charles does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him. Their columns gath
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Murat has taken Tyrol
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+600 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 100 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   2,626
   Inf:
   84,550
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Teulie's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 19,940 (lead) + 83,938 committed (Ney, Davout, Lannes, Massena, Napoleon, Teulie) = 103,878.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 1,507 men combined.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Archduke Charles fought with Archduke John beside him — massed effective strength: 11,071 (lead) + 16,844 committed (Archduke John) = 27,915.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Archduke Charles's supporting ally lost 6,503 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Murat: "The field is ours! Give me leave and I will take the next one before dusk."
   Murat fought with particular ferocity — though one wonders if it was for France or for himself.
   Berthier: the corps marched apart and arrived together.
   Attack: Murat (Personality (aggressive) +15%, Recklessness +5%, Cavalry terrain (mountains) -70%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Defensive stance +15%, Personality (cautious) +5%, Outnumbered (cautious) +10%, Terrain (Mountains) +25%, Habsburg Resolve +3%)
   Casualties: Murat's own corps 709 | Archduke Charles's own corps 10,071
   Strength: Murat 19,940 → 19,231 → 18,847 after the advance | Archduke Charles 11,071 → 1,000
   Berthier: "Reinforcements from Ney, Davout, Lannes, Massena, Napoleon and Teulie bolstered Murat's position — though Soult never arrived, Sire. And Archduke Charles was taken on that field — France holds him."
   Your forces await orders: Plunder or Secure?
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Soult(2062,426)  Deroy(2122,404)  ?(2257,819)  Archduke John(2257,785)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  Ney +6(2101,661)  Dumonceau(1660,203)  ?(2376,360)  ?(2470,651)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  9k(2015,854)
```

```
#0057  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0057_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Ney
   17,256 → 17,256
   Davout
   20,430 → 20,212
   Archduke John
   Massena
   14,973 → 8,470
   35,610 → 34,847
   ⚔
   Murat ◆
   Archduke Charles ◆
   marched to the guns
   19,940 → 19,231 → 18,847 after the advance
   11,071 → 1,000
   marched to the guns
   marched to the guns
   +3 corps in reserve — 526 lost
   Soult — awaits explicit orders
   THE GREAT BATTLE OF TYROL
   click anywhere to skip ▸
   TYROL · TURN 3
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 100 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Treasury in deficit @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: Treaty with Denmark @(3442,64)]  [icon: Treaty with Saxony @(3484,64)]  [icon: Treaty with Portugal @(3526,64)]  [icon: Treaty with Ottoman @(3568,64)]  [+2]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Russia
   +57
   T:2
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You order your troops to secure the region.
   Murat secures Tyrol. Stability set to 25. Order is maintained.
map: unchanged (107 labels)
```

```
#0058  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Murat ◆' (Control, layer 121))
view: <run>\frames\0058_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A FIELD OF LEGEND IS WON
   FRANCE LOSSES
   AUSTRIA LOSSES
   2,216
   16,574
   Tyrol falls to France.
   Ney
   17,256 → 17,256
   Davout
   20,430 → 20,212
   Archduke John
   Massena
   14,973 → 8,470
   35,610 → 34,847
   ⚔
   Murat ◆
   Archduke Charles ◆
   marched to the guns
   19,940 → 19,231 → 18,847 after the advance
   11,071 → 1,000
   marched to the guns
   marched to the guns
   +3 corps in reserve — 526 lost
   ROUTED
   Soult — awaits explicit orders
   Berthier: “Reinforcements from Ney, Davout, Lannes, Massena, Napoleon and Teulie bolstered Murat's position — though Soult never arrived, Sire. And Archduke Charles was taken on that field — France holds him.” / Archduke Charles: "I trade ground for time. Time is on my side."
   THE GREAT BATTLE OF TYROL
   TYROL · TURN 3
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Reinforcements from Ney, Davout, Lannes, Massena, Napoleon and Teulie bolstered Murat's position — though Soult never arrived, Sire. And Archduke Charles was taken on that field — France holds him."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Murat secures Tyrol. Stability set to 25. Order is maintained.
map: unchanged (107 labels)
```

```
#0059  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0059_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   2,626
   Inf:
   84,550
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "Reinforcements from Ney, Davout, Lannes, Massena, Napoleon and Teulie bolstered Murat's position — though Soult never arrived, Sire. And Archduke Charles was taken on that field — France holds him."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Murat secures Tyrol. Stability set to 25. Order is maintained.
map: unchanged (107 labels)
```

```
#0060  type where is Lannes and who holds Bohemia?  ->  ok
  (typed and Enter)
view: <run>\frames\0060_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."

What I CAN do today:
  Ney, attack Archduke John
  Davout, march to Bohemia
  build supply depot in Paris — 300g
  build fortification in Paris — 400g

For any matter of state, press F1 for the Cabinet.
Type 'help' for the full command reference.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► where is Lannes and who holds Bohemia?
   Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
   What I CAN do today:
   Ney, attack Archduke John
   Davout, march to Bohemia
   build supply depot in Paris — 300g
   build fortification in Paris — 400g
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
map: unchanged (107 labels)
```

```
#0061  type where is Lannes  ->  ok
  (typed and Enter)
view: <run>\frames\0061_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Marshal Lannes stands at Tyrol with 14,522 men (morale 75).
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► where is Lannes
   Marshal Lannes stands at Tyrol with 14,522 men (morale 75).
map: unchanged (107 labels)
```

```
#0062  type Davout, move to Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0062_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Tyrol to Bohemia (210 lost to march)
Hungary lies undefended — an attack takes it.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   2,626
   Inf:
   84,550
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, move to Bohemia
   → Davout moves from Tyrol to Bohemia (210 lost to march)
   Hungary lies undefended — an attack takes it.
   [2/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2276,485)  Soult(2062,426)  Deroy(2122,404)  ?(2257,819)  Archduke John(2257,785)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  Ney +5(2101,661)  Dumonceau(1660,203)  ?(2376,360)  ?(2470,651)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  9k(2015,854)
```

```
#0063  type Ney, move to Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0063_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney moves from Tyrol to Bohemia (172 lost to march)
Hungary lies undefended — an attack takes it.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   2,626
   Inf:
   84,550
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, move to Bohemia
   → Ney moves from Tyrol to Bohemia (172 lost to march)
   Hungary lies undefended — an attack takes it.
   [1/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney(2249,485)  Davout(2308,463)  Soult(2062,426)  Deroy(2122,404)  ?(2257,819)  Archduke John(2257,785)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  Lannes +4(2102,661)  Dumonceau(1660,203)  ?(2376,360)  ?(2470,651)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  9k(2015,854)
```

```
#0064  type Massena, move to Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0064_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Massena moves from Tyrol to Bohemia (1,045 lost to march)
Hungary lies undefended — an attack takes it.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   2,626
   Inf:
   84,550
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   Archduke Charles fought with Archduke John beside him — massed effective strength: 11,071 (lead) + 16,844 committed (Archduke John) = 27,915.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Archduke Charles's supporting ally lost 6,503 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Murat: "The field is ours! Give me leave and I will take the next one before dusk."
   Murat fought with particular ferocity — though one wonders if it was for France or for himself.
   Berthier: the corps marched apart and arrived together.
   Attack: Murat (Personality (aggressive) +15%, Recklessness +5%, Cavalry terrain (mountains) -70%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Defensive stance +15%, Personality (cautious) +5%, Outnumbered (cautious) +10%, Terrain (Mountains) +25%, Habsburg Resolve +3%)
   Casualties: Murat's own corps 709 | Archduke Charles's own corps 10,071
   Strength: Murat 19,940 → 19,231 → 18,847 after the advance | Archduke Charles 11,071 → 1,000
   Berthier: "Reinforcements from Ney, Davout, Lannes, Massena, Napoleon and Teulie bolstered Murat's position — though Soult never arrived, Sire. And Archduke Charles was taken on that field — France holds him."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Murat secures Tyrol. Stability set to 25. Order is maintained.
   ► where is Lannes and who holds Bohemia?
   Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
   What I CAN do today:
   Ney, attack Archduke John
   Davout, march to Bohemia
   build supply depot in Paris — 300g
   build fortification in Paris — 400g
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
   ► where is Lannes
   Marshal Lannes stands at Tyrol with 14,522 men (morale 75).
   ► Davout, move to Bohemia
   → Davout moves from Tyrol to Bohemia (210 lost to march)
   Hungary lies undefended — an attack takes it.
   [2/4 actions remaining]
   ► Ney, move to Bohemia
   → Ney moves from Tyrol to Bohemia (172 lost to march)
   Hungary lies undefended — an attack takes it.
   [1/4 actions remaining]
   ► Massena, move to Bohemia
   → Massena moves from Tyrol to Bohemia (1,045 lost to march)
   Hungary lies undefended — an attack takes it.
   [0/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney(2249,485)  Davout(2276,451)  Massena(2305,416)  Soult(2062,426)  Deroy(2122,404)  ?(2257,819)  Archduke John(2257,785)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  Lannes +3(2102,685)  Dumonceau(1660,203)  ?(2376,360)  ?(2470,651)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  9k(2015,854)
```

```
#0065  type recruit infantry in Paris  ->  ok
  (typed and Enter)
view: <run>\frames\0065_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Dumonceau commands our foot at Amsterdam — march him within reach. Nothing was spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry in Paris
   Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Dumonceau commands our foot at Amsterdam — march him within reach. Nothing was spent.
map: unchanged (109 labels)
```

```
#0066  type recruit infantry for Davout  ->  ok
  (typed and Enter)
view: <run>\frames\0066_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Berthier advises caution. 'Bohemia is in Hostile (stability 20/100). The populace will not answer our call until stability exceeds 50.'
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry for Davout
   Berthier advises caution. 'Bohemia is in Hostile (stability 20/100). The populace will not answer our call until stability exceeds 50.'
map: unchanged (109 labels)
```

```
#0067  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0067_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 3
   BAVARIA / ──────────────────────────── / - Deroy holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 97 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,024
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Marshal Lannes stands at Tyrol with 14,522 men (morale 75).
   ► Davout, move to Bohemia
   → Davout moves from Tyrol to Bohemia (210 lost to march)
   Hungary lies undefended — an attack takes it.
   [2/4 actions remaining]
   ► Ney, move to Bohemia
   → Ney moves from Tyrol to Bohemia (172 lost to march)
   Hungary lies undefended — an attack takes it.
   [1/4 actions remaining]
   ► Massena, move to Bohemia
   → Massena moves from Tyrol to Bohemia (1,045 lost to march)
   Hungary lies undefended — an attack takes it.
   [0/4 actions remaining]
   ► recruit infantry in Paris
   Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Dumonceau commands our foot at Amsterdam — march him within reach. Nothing was spent.
   ► recruit infantry for Davout
   Berthier advises caution. 'Bohemia is in Hostile (stability 20/100). The populace will not answer our call until stability exceeds 50.'
   ► end turn
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2658g | Occupation: -122g | Charges of Empire: -54g | Admiralty: -90g | Blockade: -329g | Other: +1503g | Upkeep: -1168g | Net: +2398g
   Treasury: 5,024g
   Actions refreshed: 4/4
   Bernadotte's army has fully recovered and is combat ready.
   Bavaria completes a market at Swabia.
   Supply shortage at Bohemia: Ney loses 590 troops — 101 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Bohemia: Davout loses 691 troops — 118 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Bohemia: Soult loses 819 troops — 140 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Bohemia: Massena loses 1,168 troops — 200 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Tyrol: Lannes loses 569 troops
   Supply shortage at Tyrol: Murat loses 738 troops
   Supply shortage at Tyrol: Napoleon loses 300 troops
   Supply shortage at Tyrol: Teulie loses 287 troops
   Soult holds at Bohemia, per your orders — the guns at Tyrol did not move him.
   Garrison at Milan reinforced: 9,000 -> 10,000
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Murat is eyeing Archduke John's position at Carniola. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Ney no longer wears the army's laurels alone — Ney and Murat now stand level at its head, and no one wears them.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney +3(2276,461)  Deroy(2090,426)  ?(2257,819)  Archduke John(2257,785)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  ?(1079,763)  Castanos(1078,729)  Lannes +3(2102,685)  Dumonceau(1660,203)  ?(2376,360)  ?(2470,651)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0068  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0068_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,024
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 19,310 [confirmed]
   Archduke John — Carniola — small force [partial]
   Brunswick — Berlin — large force [partial]
   Castanos — Gascony — small force [partial]
   Vienna garrison — Vienna — garrison — substantial force [partial]
   TURN EVENTS
   Bernadotte's army has fully recovered and is combat ready.
   Supply cost you 5,162 men, at Bohemia and Tyrol.
   Soult holds at Bohemia, per your orders — the guns at Tyrol did not move him.
   Murat is eyeing Archduke John's position at Carniola. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Ney no longer wears the army's laurels alone — Ney and Murat now stand level at its head, and no one wears them.
   DIPLOMATIC EVENTS
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   An envoy from Austria has arrived with a proposal.
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
   The court of Austria takes up a new design: Revanche.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Austria — Armistice Losing
   - Hesse — Non Aggression
   - Papal States — Open Borders
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (2 held, unsettled: Bohemia, Tyrol) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Dictated Terms (+56)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (108 labels)
```

```
#0069  click Envoys  ->  ok
  (clicked at (3375, 18))
view: <run>\frames\0069_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (3)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   ACTIVE
   Austria
   Proposal
   Open ▸
   Turn 3
   Incoming proposal: Armistice
   THE SMALL COURTS WRITE (2)
   Hesse and Papal States write. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
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
   controls: {ACTIVE}  {WAITING}  [Accept]  [Decline]  {WAITING}  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (108 labels)
```

```
#0070  click#1 Accept  ->  ok
  (clicked at (1433, 525))
view: <run>\frames\0070_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   ACTIVE
   Austria
   Proposal
   Open ▸
   Turn 3
   Incoming proposal: Armistice
   A SMALL COURT WRITES (1)
   Papal States writes. Answer them here. Unanswered letters lapse when the turn ends, and a court left waiting will not raise the matter again for some seasons.
   WAITING
   Papal States
   Proposal
   Open ▸
   Turn 3
   Incoming proposal: Open Borders Agreement
   Cardinal Consalvi, serenely: "Rome measures powers in centuries and finds it profitable to be patient with all of them; an understanding with France costs the Church nothing that time will not repay. Open the borders."
   Terms: Proposal: Open Borders Agreement · Clause: Open borders · Offer: Gold payment - 105
   or click the letter to reply in full
   controls: {ACTIVE}  {WAITING}  [Accept]  [Decline]  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 97 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
map: unchanged (108 labels)
```

```
#0071  click Accept  ->  ok
  (clicked at (1433, 525))
view: <run>\frames\0071_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (1)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   ACTIVE
   Austria
   Proposal
   Open ▸
   Turn 3
   Incoming proposal: Armistice
   controls: {ACTIVE}  [Close]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 97 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (108 labels)
```

```
#0072  click ACTIVE  ->  ok
  (clicked at (1829, 283))
view: <run>\frames\0072_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Metternich (Schemer) of Austria /  / Proposes: Armistice / Terms: /   - Proposal: Armistice / Assessment: GENEROUS /  / War Summary / War score: 58 ^ (Territory +10, Battle +15, Decisive Battle +15, Ticking -1) / Settlement: Dictated Terms / Objective: Defense - the homeland — 28 of 28 provinces held (inactive) / Ticking: +0 / Duration: 2 turns   Battles: 6W / 1L / Casualties: o …
   controls: [Accept]  [Counter]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,024
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (108 labels)
```

```
#0073  click Not Now  ->  ok
  (clicked at (2054, 687))
view: <run>\frames\0073_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,024
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Setting aside Austria's proposal. Click the envoy badge to revisit.
map: unchanged (108 labels)
```

```
#0074  type Napoleon, move to Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0074_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon moves from Tyrol to Bohemia (73 lost to march)
Hungary lies undefended — an attack takes it.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 97 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Treasury in deficit @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: The Marshalate awaits @(3442,64)]  [icon: Treaty with Hesse @(3484,64)]  [icon: Treaty with Papal States @(3526,64)]  [icon: Treaty with Denmark @(3568,64)]  [+5]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   +55
   T:3
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   5,129
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, move to Bohemia
   → Napoleon moves from Tyrol to Bohemia (73 lost to march)
   Hungary lies undefended — an attack takes it.
   [3/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney +4(2276,438)  Deroy(2090,426)  ?(2257,819)  Archduke John(2257,785)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  ?(1079,763)  Castanos(1078,729)  Lannes(2074,708)  Murat(2101,674)  Teulie(2130,640)  Dumonceau(1660,203)  ?(2376,360)  ?(2470,651)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0075  type Ney, attack Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0075_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok ASSAULT — Ney storms the works at Vienna alone: 16,494 men, 25,663 in the assault's reckoning (+23% from the corps at his side), against a garrison of 25,000. Davout, Soult, Massena and Napoleon do not join an assault on the works; the garrison breaks below 5,000.
Ney assaults the Vienna garrison! Garrison: 25,000 -> 16,018 (-8,982). Ney loses 4,016 troops. Garrison holds — 16,018 defenders remain. It regains up to 2,000 a turn (to 25,000).
[Materiel] Guns, horses and stores lost with the fallen: France -200g, Austria -449g.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   +52
   T:3
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,929
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   Ney no longer wears the army's laurels alone — Ney and Murat now stand level at its head, and no one wears them.
   DIPLOMATIC EVENTS
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   An envoy from Austria has arrived with a proposal.
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
   The court of Austria takes up a new design: Revanche.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 3 envoys await your reply this turn. Open Envoys before ending the turn.
   - Austria — Armistice Losing
   - Hesse — Non Aggression
   - Papal States — Open Borders
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (2 held, unsettled: Bohemia, Tyrol) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Dictated Terms (+56)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
   Setting aside Austria's proposal. Click the envoy badge to revisit.
   ► Napoleon, move to Bohemia
   → Napoleon moves from Tyrol to Bohemia (73 lost to march)
   Hungary lies undefended — an attack takes it.
   [3/4 actions remaining]
   ► Ney, attack Vienna
   ASSAULT — Ney storms the works at Vienna alone: 16,494 men, 25,663 in the assault's reckoning (+23% from the corps at his side), against a garrison of 25,000. Davout, Soult, Massena and Napoleon do not join an assault on the works; the garrison breaks below 5,000.
   Ney assaults the Vienna garrison! Garrison: 25,000 -> 16,018 (-8,982). Ney loses 4,016 troops. Garrison holds — 16,018 defenders remain. It regains up to 2,000 a turn (to 25,000).
   [Materiel] Guns, horses and stores lost with the fallen: France -200g, Austria -449g.
   [2/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney +4(2276,438)  Deroy(2090,426)  ?(2257,819)  Archduke John(2257,785)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  ?(1079,763)  Castanos(1078,729)  Lannes(2074,708)  Murat(2101,674)  Teulie(2130,640)  Dumonceau(1660,203)  ?(2376,360)  16k(2470,651)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0076  type Massena, storm Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0076_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok ASSAULT — Massena storms the works at Vienna alone: 32,634 men, 51,396 in the assault's reckoning (+24% from the corps at his side), against a garrison of 16,018. Ney, Davout, Soult and Napoleon do not join an assault on the works; the garrison breaks below 5,000.
Massena assaults the Vienna garrison! Garrison: 16,018 -> 8,009 (-8,009). Massena loses 2,542 troops. Garrison holds — 8,009 defenders remain. It regains up to 2,000 a turn (to 25,000).
[Materiel] Guns, horses and stores lost with the fallen: France -127g, Austria -400g.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   +49
   T:3
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   4,802
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, storm Vienna
   ASSAULT — Massena storms the works at Vienna alone: 32,634 men, 51,396 in the assault's reckoning (+24% from the corps at his side), against a garrison of 16,018. Ney, Davout, Soult and Napoleon do not join an assault on the works; the garrison breaks below 5,000.
   Massena assaults the Vienna garrison! Garrison: 16,018 -> 8,009 (-8,009). Massena loses 2,542 troops. Garrison holds — 8,009 defenders remain. It regains up to 2,000 a turn (to 25,000).
   [Materiel] Guns, horses and stores lost with the fallen: France -127g, Austria -400g.
   [1/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney +4(2276,438)  Deroy(2090,426)  ?(2257,819)  Archduke John(2257,785)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  ?(1079,763)  Castanos(1078,729)  Lannes(2074,708)  Murat(2101,674)  Teulie(2130,640)  Dumonceau(1660,203)  ?(2376,360)  8k(2470,651)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0077  type Soult, attack Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0077_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok ASSAULT — Soult storms the works at Vienna alone: 22,903 men, 35,853 in the assault's reckoning (+24% from the corps at his side), against a garrison of 8,009. Ney, Davout, Massena and Napoleon do not join an assault on the works; the garrison breaks below 5,000.
Soult assaults the Vienna garrison! Garrison collapses (8,009 -> 0). Soult loses 1,279 troops in the assault. Soult marches into Vienna! (286 lost to march)
[Materiel] Guns, horses and stores lost with the fallen: France -63g, Austria -200g. Captured: Austria → France
Your forces have taken Vienna. Plunder it for 1,200 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure') Soult's support of Ney is set aside.
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Soult has taken Vienna
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+1,200 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 100 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   4,739
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Soult, attack Vienna
   ⚑ ASSAULT — Soult storms the works at Vienna alone: 22,903 men, 35,853 in the assault's reckoning (+24% from the corps at his side), against a garrison of 8,009. Ney, Davout, Massena and Napoleon do not join an assault on the works; the garrison breaks below 5,000.
   Soult assaults the Vienna garrison! Garrison collapses (8,009 -> 0). Soult loses 1,279 troops in the assault. Soult marches into Vienna! (286 lost to march)
   [Materiel] Guns, horses and stores lost with the fallen: France -63g, Austria -200g. Captured: Austria → France
   Your forces have taken Vienna. Plunder it for 1,200 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure') Soult's support of Ney is set aside.
   [0/4 actions remaining]
   Your forces await orders: Plunder or Secure?
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney +3(2276,461)  Deroy(2090,426)  ?(2257,819)  Archduke John(2257,785)  Soult(2471,539)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  ?(1079,763)  Castanos(1078,729)  Lannes(2074,708)  Murat(2101,674)  Teulie(2130,640)  Dumonceau(1660,203)  ?(2376,360)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0078  click SECURE  ->  ok
  (clicked at (2000, 598))
view: <run>\frames\0078_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 100 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Treasury in deficit @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: The Marshalate awaits @(3442,64)]  [icon: Treaty with Hesse @(3484,64)]  [icon: Treaty with Papal States @(3526,64)]  [icon: Treaty with Denmark @(3568,64)]  [+5]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   +79
   T:3
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   4,739
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   You order your troops to secure the region.
   Soult secures Vienna. Stability set to 25. Order is maintained.
map: unchanged (109 labels)
```

```
#0079  click THIRD COALITION  ->  ok
  (clicked at (3429, 965))
view: <run>\frames\0079_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) ──
   THIRD COALITION
   Britain
   BR
   −1
   FR
   Austria
   AU
   +80
   FR
   Russia
   RU
   0
   FR
   Leader: Britain   Posture: Defensive /  /   Britain  Unknown  — leads the coalition /   Austria  WE:128  ~10,000 men /   Russia  Unknown /  / Coordination /   Britain-Austria: Good /   Britain-Russia: Good /   Austria-Russia: Good /  / Weak link: Austria (highest WE)
   controls: [icon @(3139,276)]  [Open Whole-War Settlement]  [Target Austria]  [Target Russia]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Soult secures Vienna. Stability set to 25. Order is maintained.
map: unchanged (109 labels)
```

```
#0080  click Target Austria  ->  ok
  (clicked at (2900, 784))
view: <run>\frames\0080_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY — Austria
   DP: 7
   Loading assessment...
   An unanswered envoy awaits your reply. Reopen Envoys before starting a new diplomatic action.
   controls: [icon: Close (Esc) @(2075,284)]  [Open Envoys (1)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Soult secures Vienna. Stability set to 25. Order is maintained.
map: unchanged (109 labels)
```

```
#0081  click Open Envoys  ->  ok
  (clicked at (1829, 514))
view: <run>\frames\0081_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Metternich (Schemer) of Austria /  / Proposes: Armistice / Terms: /   - Proposal: Armistice / Assessment: GENEROUS /  / War Summary / War score: 58 ^ (Territory +10, Battle +15, Decisive Battle +15, Ticking -1) / Settlement: Dictated Terms / Objective: Defense - the homeland — 28 of 28 provinces held (inactive) / Ticking: +0 / Duration: 2 turns   Battles: 6W / 1L / Casualties: o …
   controls: [Accept]  [Counter]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   4,739
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Soult secures Vienna. Stability set to 25. Order is maintained.
map: unchanged (109 labels)
```

```
#0082  scroll 1828 512 down 10  ->  ok
  (scrolled down 10 at (1828, 512))
view: <run>\frames\0082_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal', 'war_status_panel (not modal)'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/4 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Soult secures Vienna. Stability set to 25. Order is maintained.
map: unchanged (109 labels)
```

```
#0083  click Counter  ->  ok
  (clicked at (1754, 687))
view: <run>\frames\0083_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 100 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Treasury in deficit @(3358,64)]  [icon: Marshal Murat seeks an audience @(3400,64)]  [icon: The Marshalate awaits @(3442,64)]  [icon: Treaty with Hesse @(3484,64)]  [icon: Treaty with Papal States @(3526,64)]  [icon: Diplomatic Action Rejected @(3568,64)]  [+6]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   4,739
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Austria's proposal: countered
   Talleyrand attempted to negotiate, but Austria found our counter-terms unacceptable. The proposal is rejected. (1 DP spent)
map: unchanged (109 labels)
```

```
#0084  click THIRD COALITION  ->  ok
  (clicked at (3429, 965))
view: <run>\frames\0084_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) ──
   THIRD COALITION
   Britain
   BR
   −1
   FR
   Austria
   AU
   +80
   FR
   Russia
   RU
   0
   FR
   Leader: Britain   Posture: Defensive /  /   Britain  Unknown  — leads the coalition /   Austria  WE:128  ~10,000 men /   Russia  Unknown /  / Coordination /   Britain-Austria: Good /   Britain-Russia: Good /   Austria-Russia: Good /  / Weak link: Austria (highest WE)
   controls: [icon @(3139,276)]  [Open Whole-War Settlement]  [Target Austria]  [Target Russia]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You order your troops to secure the region.
   Soult secures Vienna. Stability set to 25. Order is maintained.
   Responding to Austria's proposal: countered
   Talleyrand attempted to negotiate, but Austria found our counter-terms unacceptable. The proposal is rejected. (1 DP spent)
map: unchanged (109 labels)
```

```
#0085  click Target Austria  ->  ok
  (clicked at (2900, 784))
view: <run>\frames\0085_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY — Austria
   DP: 6
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War   Relation: -80 (Hostile) /  / "Austria falters, Your Excellency. Our armies press the advantage — we may dictate the terms, though a court not yet broken will be slow to sign them." / Recommendation: Talleyrand recommends: Propose Armistice /  / KEY FACTORS /   + Base willingness (+20) /   + Our military dominance (+17) /   + Battlefield diplomac …
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Uncertain — a counter is likely]  [Open Settlement]  [Propose White Peace]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5]  [Undermine Alliances (2 DP)  —  -4 relation between targets/turn]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You order your troops to secure the region.
   Soult secures Vienna. Stability set to 25. Order is maintained.
   Responding to Austria's proposal: countered
   Talleyrand attempted to negotiate, but Austria found our counter-terms unacceptable. The proposal is rejected. (1 DP spent)
map: unchanged (109 labels)
```

```
#0086  click Open Settlement  ->  ok
  (clicked at (1825, 491))
view: <run>\frames\0086_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   This settlement cannot be ratified now. / France vs Austria + Britain + Russia - Whole-war settlement / Covered enemies: Austria, Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 12/50, Britain 20/50, Russia 20/50. / Treasury 4,739 gold: committed 0 / reserve 500 / remaining 4,239 / Sire, this settlement of France vs Austria + Britain + Russia seats 3 c …
   The table /   * Austria ▸ - Holding out (12/50) White peace /       Blocker: Leader's own losses /       Metternich regrets that Austria must remain… unconvinced — their crown is asked to sign away too much of its own. /       + Add demand /   * Britain ▸ - Holding out (20/50) White peace /       Blocker: Settlement legitimacy /       Castlereagh declines for Britain: it claims no victory, but a w …
   Austria:
   Britain:
   Russia:
   Sire, a white peace for France vs Austria + Britain + Russia cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. Author terms or hold until the field shifts. London and Vilna are unbeaten — a whole-war peace needs their consent (Austria 12/50, Britain 20/50, Russia 20/50). Press Austria alone: the separ …
   controls: <Austria ▸>  <+ Add demand>  <Britain ▸>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Drop Austria]  [Press Britain]  [Ease Britain]  [Drop Britain]  [Press Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 100 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   4,739
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (2 held, unsettled: Bohemia, Tyrol) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Dictated Terms (+56)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
   Setting aside Austria's proposal. Click the envoy badge to revisit.
   ► Napoleon, move to Bohemia
   → Napoleon moves from Tyrol to Bohemia (73 lost to march)
   Hungary lies undefended — an attack takes it.
   [3/4 actions remaining]
   ► Ney, attack Vienna
   ASSAULT — Ney storms the works at Vienna alone: 16,494 men, 25,663 in the assault's reckoning (+23% from the corps at his side), against a garrison of 25,000. Davout, Soult, Massena and Napoleon do not join an assault on the works; the garrison breaks below 5,000.
   Ney assaults the Vienna garrison! Garrison: 25,000 -> 16,018 (-8,982). Ney loses 4,016 troops. Garrison holds — 16,018 defenders remain. It regains up to 2,000 a turn (to 25,000).
   [Materiel] Guns, horses and stores lost with the fallen: France -200g, Austria -449g.
   [2/4 actions remaining]
   ► Massena, storm Vienna
   ASSAULT — Massena storms the works at Vienna alone: 32,634 men, 51,396 in the assault's reckoning (+24% from the corps at his side), against a garrison of 16,018. Ney, Davout, Soult and Napoleon do not join an assault on the works; the garrison breaks below 5,000.
   Massena assaults the Vienna garrison! Garrison: 16,018 -> 8,009 (-8,009). Massena loses 2,542 troops. Garrison holds — 8,009 defenders remain. It regains up to 2,000 a turn (to 25,000).
   [Materiel] Guns, horses and stores lost with the fallen: France -127g, Austria -400g.
   [1/4 actions remaining]
   ► Soult, attack Vienna
   ⚑ ASSAULT — Soult storms the works at Vienna alone: 22,903 men, 35,853 in the assault's reckoning (+24% from the corps at his side), against a garrison of 8,009. Ney, Davout, Massena and Napoleon do not join an assault on the works; the garrison breaks below 5,000.
   Soult assaults the Vienna garrison! Garrison collapses (8,009 -> 0). Soult loses 1,279 troops in the assault. Soult marches into Vienna! (286 lost to march)
   [Materiel] Guns, horses and stores lost with the fallen: France -63g, Austria -200g. Captured: Austria → France
   Your forces have taken Vienna. Plunder it for 1,200 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure') Soult's support of Ney is set aside.
   [0/4 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Soult secures Vienna. Stability set to 25. Order is maintained.
   Responding to Austria's proposal: countered
   Talleyrand attempted to negotiate, but Austria found our counter-terms unacceptable. The proposal is rejected. (1 DP spent)
   ► propose common peace with Austria
map: unchanged (109 labels)
```

```
#0087  click Press Austria  ->  ok
  (clicked at (1466, 571))
view: <run>\frames\0087_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   This settlement cannot be ratified now. / France vs Austria + Britain + Russia - Whole-war settlement / Covered enemies: Austria, Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria -17/50, Britain -24/50, Russia -24/50. / Treasury 4,739 gold: committed 0 / reserve 500 / remaining 4,239 / Sire, this settlement of France vs Austria + Britain + Russia seats  …
   The table /   * Austria ▸ - Holding out (-17/50) Demanded: Carniola /       Blocker: Leader's own losses /       Metternich regrets that Austria must remain… unconvinced — their crown is asked to sign away too much of its own. /       Demanded · Cede Carniola  Remove /       + Add demand /   * Britain ▸ - Holding out (-24/50) White peace /       Blocker: Settlement legitimacy /       Castlereagh d …
   Austria:
   Britain:
   Russia:
   Sire, the settlement of France vs Austria + Britain + Russia cannot be ratified now: the terms claim a victory the field has not delivered. Revise terms or stand down before pressing further. London and Vilna are unbeaten — a whole-war peace needs their consent (Austria -17/50, Britain -24/50, Russia -24/50). Press Austria alone: the separate peace. It costs 3 diplomatic points; you have 6. Recogn …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  <Britain ▸>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Drop Austria]  [Press Britain]  [Ease Britain]  [Drop Britain]  [Press Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial harsher
map: unchanged (109 labels)
```

```
#0088  click Remove  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0088_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   This settlement cannot be ratified now. / France vs Austria + Britain + Russia - Whole-war settlement / Covered enemies: Austria, Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 12/50, Britain 20/50, Russia 20/50. / Treasury 4,739 gold: committed 0 / reserve 500 / remaining 4,239 / Sire, this settlement of France vs Austria + Britain + Russia seats 3 c …
   The table /   * Austria ▸ - Holding out (12/50) White peace /       Blocker: Leader's own losses /       Metternich regrets that Austria must remain… unconvinced — their crown is asked to sign away too much of its own. /       + Add demand /   * Britain ▸ - Holding out (20/50) White peace /       Blocker: Settlement legitimacy /       Castlereagh declines for Britain: it claims no victory, but a w …
   Austria:
   Britain:
   Russia:
   Sire, a white peace for France vs Austria + Britain + Russia cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. Author terms or hold until the field shifts. London and Vilna are unbeaten — a whole-war peace needs their consent (Austria 12/50, Britain 20/50, Russia 20/50). Press Austria alone: the separ …
   controls: <Austria ▸>  <+ Add demand>  <Britain ▸>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Drop Austria]  [Press Britain]  [Ease Britain]  [Drop Britain]  [Press Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement demand remove
map: unchanged (109 labels)
```

```
#0089  click Drop Britain  ->  ok
  (clicked at (1782, 613))
view: <run>\frames\0089_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   This settlement cannot be ratified now. / France vs Austria + Russia - Separate settlement / Covered enemies: Austria, Russia / Still at war: Britain / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 28/50, Russia 36/50. / Treasury 4,739 gold: committed 0 / reserve 500 / remaining 4,239 / Sire, this settlement of France vs Austria + Russia seats 2 courts at the table. A …
   The table /   * Austria ▸ - Holding out (28/50) White peace /       Blocker: Leader's own losses /       Metternich regrets that Austria must remain… unconvinced — their crown is asked to sign away too much of its own. /       + Add demand /   * Russia ▸ - Holding out (close) (36/50) White peace /       Blocker: National design /       Russia Holding out → Holding out (close) /       Czartoryski c …
   Austria:
   Russia:
   Coverage:
   Sire, a white peace for France vs Austria + Russia cannot be sealed as it stands: their crown is asked to sign away too much of its own. Author terms or hold until the field shifts. Vilna is unbeaten — a whole-war peace needs its consent (Austria 28/50, Russia 36/50). Press Austria alone: the separate peace. It costs 3 diplomatic points; you have 6. Recognition: Austria will recognize the order at …
   controls: <Austria ▸>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Drop Austria]  [Press Russia]  [Ease Russia]  [Drop Russia]  [Bring Britain to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement cover drop
map: unchanged (109 labels)
```

```
#0090  click Drop Russia  ->  ok
  (clicked at (1782, 619))
view: <run>\frames\0090_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   Settlement of France vs Austria — ready for ratification / France vs Austria - Separate settlement / Covered enemies: Austria / Still at war: Britain, Russia / Will carry as drafted — every court at or above 50. / Treasury 4,739 gold: committed 0 / reserve 500 / remaining 4,239 / Sire, this settlement of France vs Austria seats 1 courts at the table. Every court at the table will sign; the settlem …
   The table /   * Austria ▸ - Will sign (51/50) White peace /       Austria Holding out → Will sign /       Metternich signals that Austria will sign the settlement of France vs Austria. /       + Add demand / This peace carries.
   Austria:
   Coverage:
   Sire, the white peace for France vs Austria is ready: no terms exchanged, no map redrawn — only the war ends. Ratify and the field falls quiet. Recognition: Austria will recognize the order at the Congress — Vienna stays ours by this treaty. /  / Allies and Standing /   * Austria - Seat at settlement (Defenders) /   * France - Seat at settlement (Attackers, war leader) /   * Bavaria - Named benefi …
   controls: <Austria ▸>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Separate peace with Austria]  [Bring Britain to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement cover drop
map: unchanged (109 labels)
```

```
#0091  click Add demand  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0091_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   Settlement of France vs Austria — ready for ratification / France vs Austria - Separate settlement / Covered enemies: Austria / Still at war: Britain, Russia / Will carry as drafted — every court at or above 50. / Treasury 4,739 gold: committed 0 / reserve 500 / remaining 4,239 / Sire, this settlement of France vs Austria seats 1 courts at the table. Every court at the table will sign; the settlem …
   The table /   * Austria ▸ - Will sign (51/50) White peace /       Austria Holding out → Will sign /       Metternich signals that Austria will sign the settlement of France vs Austria. /       − Add demand /         Demands of Austria /           Take Carniola from Austria ▾ /             — Carniola sits beside what we already hold; Austria would keep it only on paper. /           Demand 31 gold a …
   Austria:
   Coverage:
   Sire, the white peace for France vs Austria is ready: no terms exchanged, no map redrawn — only the war ends. Ratify and the field falls quiet. Recognition: Austria will recognize the order at the Congress — Vienna stays ours by this treaty. /  / Allies and Standing /   * Austria - Seat at settlement (Defenders) /   * France - Seat at settlement (Attackers, war leader) /   * Bavaria - Named benefi …
   controls: <Austria ▸>  <− Add demand>  <Take Carniola from Austria>  <▾>  <Demand 31 gold a turn from Austria for 3 turns>  <Vassalize Austria>  <Subjugate Austria>  <Force Austria into alliance>  <Austria joins the Continental System>  <▸ Offers to Austria (3)>  [Press Austria]  [Ease Austria]  [Separate peace with Austria]  [Bring Britain to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial harsher
   Directing Talleyrand: settlement demand remove
   Directing Talleyrand: settlement cover drop
   Directing Talleyrand: settlement cover drop
map: unchanged (109 labels)
```

```
#0092  click Submit for Review  ->  ok
  (clicked at (2203, 884))
view: <run>\frames\0092_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   Settlement of France vs Austria — ready for ratification / France vs Austria - Separate settlement / STAGED FOR REVIEW — the terms are frozen. Ratify, revise, or return to shaping. / Covered enemies: Austria / Still at war: Britain, Russia / Will carry as drafted — every court at or above 50. / Sire, this settlement of France vs Austria seats 1 courts at the table. Every court at the table will si …
   The table /   * Austria - Will sign (51/50) White peace /       Metternich signals that Austria will sign the settlement of France vs Austria. / This peace carries.
   Sire, the white peace for France vs Austria is ready: no terms exchanged, no map redrawn — only the war ends. Ratify and the field falls quiet. Recognition: Austria will recognize the order at the Congress — Vienna stays ours by this treaty. /  / Allies and Standing /   * Austria - Seat at settlement (Defenders) /   * France - Seat at settlement (Attackers, war leader) /   * Bavaria - Named benefi …
   controls: [Ratify White Peace]  [Open War Detail]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: submit settlement for review
map: unchanged (109 labels)
```

```
#0093  click Ratify White Peace  ->  ok
  (clicked at (1455, 856))
view: <run>\frames\0093_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 100 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3358,64)]  [icon: Treasury in deficit @(3400,64)]  [icon: Marshal Murat seeks an audience @(3442,64)]  [icon: The Marshalate awaits @(3484,64)]  [icon: Treaty with Hesse @(3526,64)]  [icon: Treaty with Papal States @(3568,64)]  [+9]
── DiplomaticLedger (layer 50) ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 6/7
   ═══ ACTIVE TREATIES ═══ /  / Sweden ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (2 turns ago) /  / Naples ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (2 turns ago) /  / Portugal ↔ France: Open Borders /   Clauses: Gold payment: 60 (Portugal -> France) /   Duration: permanent   Ca …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES](disabled: You are reading this book)  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <v Settlement of France vs Austria: settlement ratified.>
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   4,739
   Inf:
   86,675
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: confirm settlement
   Settlement Ratified: France vs Austria (3 pairs resolved). Status quo: Bohemia, Tyrol and Vienna stay ours by the treaty — titled. Recognition: Austria will recognize the order at the Congress — Vienna stays ours by this treaty.
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney +3(2276,461)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Soult(2471,539)  ?(2127,138)  Brunswick(2126,103)  Bernadotte(1899,455)  ?(1079,763)  Castanos(1078,729)  Lannes(2074,708)  Murat(2101,674)  Teulie(2130,640)  Dumonceau(1660,203)  ?(2376,360)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0094  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0094_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (111 labels)
```

```
#0095  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0095_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -1
   T:3
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (111 labels)
```

```
#0096  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0096_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 4
   BAVARIA / ──────────────────────────── / - Deroy holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 97 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,051
   Inf:
   88,625
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Talleyrand attempted to negotiate, but Austria found our counter-terms unacceptable. The proposal is rejected. (1 DP spent)
   ► propose common peace with Austria
   Directing Talleyrand: settlement dial harsher
   Directing Talleyrand: settlement demand remove
   Directing Talleyrand: settlement cover drop
   Directing Talleyrand: settlement cover drop
   Directing Talleyrand: submit settlement for review
   Directing Talleyrand: confirm settlement
   Settlement Ratified: France vs Austria (3 pairs resolved). Status quo: Bohemia, Tyrol and Vienna stay ours by the treaty — titled. Recognition: Austria will recognize the order at the Congress — Vienna stays ours by this treaty.
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   ► end turn
   Your unratified settlement draft with Austria (1 clause) was set aside at turn's end.
   ═══════════════════════════════════════
   TURN 5 BEGINS
   ═══════════════════════════════════════
   Income: 2714g | Occupation: -227g | Charges of Empire: -218g | Admiralty: -90g | Blockade: -368g | Other: +1569g | Upkeep: -1068g | Net: +2312g
   Treasury: 7,051g
   Actions refreshed: 4/4
   Bavaria completes a supply depot at Munich.
   Supply shortage at Bohemia: Ney loses 456 troops — 54 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Bohemia: Davout loses 707 troops — 84 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Bohemia: Massena loses 1,101 troops — 130 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Bohemia: Napoleon loses 266 troops — 31 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Tyrol: Lannes loses 342 troops
   Supply shortage at Tyrol: Murat loses 444 troops
   Supply shortage at Tyrol: Teulie loses 173 troops
   Garrison at Vienna reinforced: 0 -> 2,000
   Holland loyalty 97 (-3): the lord's defeats, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Kingdom of Italy loyalty 95 (-5): the lord's defeats, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 93 (-5): the lord's defeats, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   The war the Kingdom of Italy shared with France is over — Teulie's contingent takes the road home to Milan.
   Britain subsidizes Russia with 200 gold.
   Murat meant to go at the enemy on his own initiative, but no enemy stood within his reach when the moment came — he stands where he was, and his orders are unchanged.
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Murat's resentment of Ney has cooled with time.
   Berthier notes that Bernadotte has grown restless — he has not seen laurels while Massena wins them. I recommend giving him meaningful orders soon.
   Berthier: Enemy forces spotted near Vienna! Kutuzov (33,950 troops) at Moravia.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney +3(2276,461)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Soult(2471,539)  ?(2127,138)  Brunswick(2126,103)  ?(2666,499)  Kutuzov(2666,465)  Bernadotte(1899,455)  Lannes(2074,708)  Murat(2101,674)  Teulie(2130,640)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  ?(2376,360)  2k(2470,651)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0097  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0097_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 97 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified @(3358,64)]  [icon: Treasury in deficit @(3400,64)]  [icon: The Moniteur is out @(3442,64)]  [icon: The Marshalate awaits @(3484,64)]  [icon: Treaty with Hesse @(3526,64)]  [icon: Treaty with Papal States @(3568,64)]  [+9]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -2
   T:4
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   7,051
   Inf:
   88,625
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 19,310 [confirmed]
   Archduke Charles — Carniola — screening force [partial]
   Archduke John — Carniola — small force [partial]
   Brunswick — Berlin — large force [partial]
   Kutuzov — Moravia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 3,489 men, at Bohemia and Tyrol.
   Garrison at Vienna reinforced: 0 -> 2,000
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Murat meant to go at the enemy on his own initiative, but no enemy stood within his reach when the moment came — he stands where he was, and his orders are unchanged.
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Murat's resentment of Ney has cooled with time.
   Berthier notes that Bernadotte has grown restless — he has not seen laurels while Massena wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   Bohemia, Tyrol and Vienna — retained by the peace with Austria, titled by treaty.
   Settlement of France vs Austria: settlement ratified.
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The war the Kingdom of Italy shared with France is over — Teulie's contingent takes the road home to Milan.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war come, having been asked.
   THE CONTINENTAL SYSTEM tightens: 42% of the Continent's ports are closed to Britain.
   The court of Austria takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their capital in our hands is worth ten field victories, Sire. Expect their court to sue — or to flee."
   ════════════════════════════════════
map: unchanged (114 labels)
```

```
#0098  type Ney, attack Kutuzov in Moravia  ->  ok
  (typed and Enter)
view: <run>\frames\0098_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney pursues Kutuzov (at Moravia). Moves to Dresden. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted by an interrupt, and stands down if intelligence on him lapses. 'Ney, cancel' recalls him. Ney: "Run him to ground, then. My sabers are hungry."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   7,051
   Inf:
   88,625
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Archduke Charles — Carniola — screening force [partial]
   Archduke John — Carniola — small force [partial]
   Brunswick — Berlin — large force [partial]
   Kutuzov — Moravia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 3,489 men, at Bohemia and Tyrol.
   Garrison at Vienna reinforced: 0 -> 2,000
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Murat meant to go at the enemy on his own initiative, but no enemy stood within his reach when the moment came — he stands where he was, and his orders are unchanged.
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Murat's resentment of Ney has cooled with time.
   Berthier notes that Bernadotte has grown restless — he has not seen laurels while Massena wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   Bohemia, Tyrol and Vienna — retained by the peace with Austria, titled by treaty.
   Settlement of France vs Austria: settlement ratified.
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The war the Kingdom of Italy shared with France is over — Teulie's contingent takes the road home to Milan.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war come, having been asked.
   THE CONTINENTAL SYSTEM tightens: 42% of the Continent's ports are closed to Britain.
   The court of Austria takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their capital in our hands is worth ten field victories, Sire. Expect their court to sue — or to flee."
   ════════════════════════════════════
   ► Ney, attack Kutuzov in Moravia
   Ney pursues Kutuzov (at Moravia). Moves to Dresden. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted by an interrupt, and stands down if intelligence on him lapses. 'Ney, cancel' recalls him. Ney: "Run him to ground, then. My sabers are hungry."
   [2/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Ney(2376,248)  Davout(2248,485)  Massena(2277,451)  Napoleon(2304,416)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Soult(2471,539)  ?(2127,138)  Brunswick(2126,103)  ?(2666,499)  Kutuzov(2666,465)  Bernadotte(1899,455)  Lannes(2074,708)  Murat(2101,674)  Teulie(2130,640)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  10k(2376,360)  2k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0099  type Davout, move to Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0099_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Bohemia to Vienna (186 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   7,051
   Inf:
   88,625
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, move to Vienna
   → Davout moves from Bohemia to Vienna (186 lost to march)
   [1/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Ney(2376,248)  Massena(2249,485)  Napoleon(2304,451)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Soult(2499,505)  ?(2127,138)  Brunswick(2126,103)  ?(2666,499)  Kutuzov(2666,465)  Bernadotte(1899,455)  Lannes(2074,708)  Murat(2101,674)  Teulie(2130,640)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  10k(2376,360)  2k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0100  type Massena, move to Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0100_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Massena moves from Bohemia to Vienna (811 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   7,051
   Inf:
   88,625
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, move to Vienna
   → Massena moves from Bohemia to Vienna (811 lost to march)
   [0/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Ney(2376,248)  Napoleon(2276,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Soult(2471,505)  Massena(2499,471)  ?(2127,138)  Brunswick(2126,103)  ?(2666,499)  Kutuzov(2666,465)  Bernadotte(1899,455)  Lannes(2074,708)  Murat(2101,674)  Teulie(2130,640)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  10k(2376,360)  2k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0101  type what are admin actions for?  ->  ok
  (typed and Enter)
view: <run>\frames\0101_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Each turn gives the day's orders (military actions) and administrative actions. A tactical order costs one; a standing march, pursuit or hold 2 (1 for a literal marshal or the Emperor); support 1; recruiting, building and the laws spend administrative actions; retreat and the desk are free.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what are admin actions for?
   Each turn gives the day's orders (military actions) and administrative actions. A tactical order costs one; a standing march, pursuit or hold 2 (1 for a literal marshal or the Emperor); support 1; recruiting, building and the laws spend administrative actions; retreat and the desk are free.
map: unchanged (119 labels)
```

```
#0102  type recruit infantry in Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0102_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte recruits 3,000 infantry for Rhineland (1 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 21% -> 26%
Infantry pool: 88,625 -> 85,625 [WARNING] Morale dropped to 26% — consider drilling before battle.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   6,451
   Inf:
   85,625
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry in Rhineland
   + Bernadotte recruits 3,000 infantry for Rhineland (1 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 21% -> 26%
   Infantry pool: 88,625 -> 85,625 [WARNING] Morale dropped to 26% — consider drilling before battle.
   [0/4 actions remaining]
map: unchanged (119 labels)
```

```
#0103  type build supply depot in Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0103_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Cannot build in Vienna — region stability too low (35/100). Need 51+.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   Bohemia, Tyrol and Vienna — retained by the peace with Austria, titled by treaty.
   Settlement of France vs Austria: settlement ratified.
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The war the Kingdom of Italy shared with France is over — Teulie's contingent takes the road home to Milan.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war come, having been asked.
   THE CONTINENTAL SYSTEM tightens: 42% of the Continent's ports are closed to Britain.
   The court of Austria takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Their capital in our hands is worth ten field victories, Sire. Expect their court to sue — or to flee."
   ════════════════════════════════════
   ► Ney, attack Kutuzov in Moravia
   Ney pursues Kutuzov (at Moravia). Moves to Dresden. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted by an interrupt, and stands down if intelligence on him lapses. 'Ney, cancel' recalls him. Ney: "Run him to ground, then. My sabers are hungry."
   [2/4 actions remaining]
   ► Davout, move to Vienna
   → Davout moves from Bohemia to Vienna (186 lost to march)
   [1/4 actions remaining]
   ► Massena, move to Vienna
   → Massena moves from Bohemia to Vienna (811 lost to march)
   [0/4 actions remaining]
   ► what are admin actions for?
   Each turn gives the day's orders (military actions) and administrative actions. A tactical order costs one; a standing march, pursuit or hold 2 (1 for a literal marshal or the Emperor); support 1; recruiting, building and the laws spend administrative actions; retreat and the desk are free.
   ► recruit infantry in Rhineland
   + Bernadotte recruits 3,000 infantry for Rhineland (1 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 21% -> 26%
   Infantry pool: 88,625 -> 85,625 [WARNING] Morale dropped to 26% — consider drilling before battle.
   [0/4 actions remaining]
   ► build supply depot in Vienna
   Cannot build in Vienna — region stability too low (35/100). Need 51+.
map: unchanged (119 labels)
```

```
#0104  type recruit cavalry in Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0104_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Berthier checks the order of battle. 'No marshal of cavalry can reach Rhineland, Sire — Bernadotte commands infantry.' Murat commands our horse at Tyrol — march him within reach. Nothing was spent.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit cavalry in Rhineland
   Berthier checks the order of battle. 'No marshal of cavalry can reach Rhineland, Sire — Bernadotte commands infantry.' Murat commands our horse at Tyrol — march him within reach. Nothing was spent.
map: unchanged (119 labels)
```

```
#0105  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0105_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 5
   RUSSIA / ──────────────────────────── / - Kutuzov attacks Ney /     Battle of Dresden /     Kutuzov: 1,040 casualties, 32,910 remaining /     Ney: 4,101 casualties, 7,765 remaining /     Result: Attacker tactical victory (Kutuzov victorious) /     Ney forced to retreat! /     ⚔ View the field /     --- Berthier's Report --- /     Attack: Kutuzov (Defensive stance -10%) /     Defense: Ney (Terrain  …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,483
   Inf:
   87,425
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [2/4 actions remaining]
   ► Davout, move to Vienna
   → Davout moves from Bohemia to Vienna (186 lost to march)
   [1/4 actions remaining]
   ► Massena, move to Vienna
   → Massena moves from Bohemia to Vienna (811 lost to march)
   [0/4 actions remaining]
   ► what are admin actions for?
   Each turn gives the day's orders (military actions) and administrative actions. A tactical order costs one; a standing march, pursuit or hold 2 (1 for a literal marshal or the Emperor); support 1; recruiting, building and the laws spend administrative actions; retreat and the desk are free.
   ► recruit infantry in Rhineland
   + Bernadotte recruits 3,000 infantry for Rhineland (1 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 21% -> 26%
   Infantry pool: 88,625 -> 85,625 [WARNING] Morale dropped to 26% — consider drilling before battle.
   [0/4 actions remaining]
   ► build supply depot in Vienna
   Cannot build in Vienna — region stability too low (35/100). Need 51+.
   ► recruit cavalry in Rhineland
   Berthier checks the order of battle. 'No marshal of cavalry can reach Rhineland, Sire — Bernadotte commands infantry.' Murat commands our horse at Tyrol — march him within reach. Nothing was spent.
   ► end turn
   ═══════════════════════════════════════
   TURN 6 BEGINS
   ═══════════════════════════════════════
   Income: 2789g | Occupation: -205g | Charges of Empire: -366g | Admiralty: -90g | Blockade: -368g | Materiel: -205g | Other: +1549g | Upkeep: -1072g | Net: +2032g | Spent: 600g
   Treasury: 8,483g
   Actions refreshed: 4/4
   Ney's army is recovering. Effectiveness penalty: -30%.
   Supply shortage at Vienna: Davout loses 404 troops — all of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Vienna: Soult loses 469 troops — all of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Vienna: Massena loses 619 troops — all of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Moravia: Kutuzov loses 361 troops
   Supply shortage at Moravia: Buxhowden loses 341 troops
   Supply shortage at Tyrol: Lannes loses 144 troops
   Supply shortage at Tyrol: Murat loses 187 troops
   Garrison at Vienna reinforced: 2,000 -> 4,000
   Holland loyalty 95 (-2): satellite drift, the lord's defeats
   Kingdom of Italy loyalty 91 (-4): satellite drift, the lord's defeats
   Switzerland loyalty 89 (-4): satellite drift, the lord's defeats
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Russia and Austria grows.
   Berthier notes that Bernadotte has grown restless — he has not seen laurels while Massena wins them. I recommend giving him meaningful orders soon.
   Berthier: Enemy forces spotted near Vienna! Buxhowden (30,699 troops) at Moravia.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Ney(2249,485)  Napoleon(2276,451)  Teulie(2305,416)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Soult(2471,505)  Massena(2499,471)  ?(2127,138)  Brunswick(2126,103)  ?(2648,499)  Kutuzov(2648,465)  ?(2684,499)  Buxhowden(2684,431)  Bernadotte(1899,455)  Lannes(2074,708)  Murat(2129,674)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  10k(2376,360)  4k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0106  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0106_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   RUSSIA LOSSES
   0
   0
   ⚔
   Ney ◆
   Kutuzov ◆
   11,866 → 7,765
   33,950 → 32,910
   +1 corps in reserve
   Davout — could not reach the field
   Soult — awaits explicit orders
   BATTLE OF DRESDEN
   click anywhere to skip ▸
   DRESDEN · TURN 5
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Teulie — Bohemia — 6,812 — Moving to Milan — 3 turns out.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 19,310 [confirmed]
   Hohenlohe — Silesia — substantial force [partial]
   Archduke Charles — Carniola — screening force [partial]
   Archduke John — Carniola — small force [partial]
   Brunswick — Berlin — large force [partial]
   Kutuzov — Moravia — substantial force [partial]
   Buxhowden — Moravia — substantial force [partial]
   Castanos — Normandy — small force [partial]
   Podolia garrison — Podolia — garrison — screening force [partial]
   TURN EVENTS
   Ney's army is recovering. Effectiveness penalty: -30%.
   Supply cost you 1,823 men, at Vienna and Tyrol.
   Garrison at Vienna reinforced: 2,000 -> 4,000
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Berthier notes that Bernadotte has grown restless — he has not seen laurels while Massena wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   Intelligence reports Russia has raised Bennigsen to high command.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from the Kingdom of Italy has arrived with a petition.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Kingdom of Italy — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-2)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-4)
   COALITION THREAT
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
map: unchanged (121 labels)
```

```
#0107  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Ney ◆' (Control, layer 121))
view: <run>\frames\0107_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS LOST
   FRANCE LOSSES
   RUSSIA LOSSES
   4,101
   1,040
   ⚔
   Ney ◆
   Kutuzov ◆
   11,866 → 7,765
   33,950 → 32,910
   +1 corps in reserve
   ROUTED
   Davout — could not reach the field
   Soult — awaits explicit orders
   Berthier: “Ney stood alone, Sire. Davout, Soult, Massena and Napoleon never came.” / Kutuzov: "The old man strikes once, and only when the snow agrees."
   BATTLE OF DRESDEN
   DRESDEN · TURN 5
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
map: unchanged (121 labels)
```

```
#0108  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0108_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,483
   Inf:
   87,425
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
map: unchanged (121 labels)
```

```
#0109  click Envoys  ->  ok
  (clicked at (3377, 18))
view: <run>\frames\0109_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Marescalchi (Loyalist) of Kingdom of Italy /  / The petition: /   - Grant it, and Tyrol passes to the Kingdom of Italy: loyalty +9 (to the 100 ceiling), its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. Our net rises by 3g a turn — 108g of income forfeited, 30g of occupation relieved, 81g returned as tribute at today's 75% rate, the force limit fal …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,483
   Inf:
   87,425
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
map: unchanged (121 labels)
```

```
#0110  click Grant  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0110_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 95 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: Settlement Ratified @(3393,64)]  [icon: Treasury in deficit @(3435,64)]  [icon: Client's Petition Accepted @(3477,64)]  [icon: The Moniteur is out @(3519,64)]  [icon: The Marshalate awaits @(3561,64)]  [+11]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -5
   T:5
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,483
   Inf:
   87,425
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to the Kingdom of Italy's proposal: accepted
   Tyrol is ceded to the Kingdom of Italy. Loyalty +9 (91 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 3g a turn — 108g of income forfeited, 30g of occupation relieved, 81g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today.
map: unchanged (121 labels)
```

```
#0111  type Napoleon, move to Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0111_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon moves from Bohemia to Vienna (70 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   8,483
   Inf:
   87,425
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, move to Vienna
   → Napoleon moves from Bohemia to Vienna (70 lost to march)
   [3/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Ney(2249,485)  Teulie(2305,463)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout +3(2471,515)  ?(2127,138)  Brunswick(2126,103)  ?(2648,499)  Kutuzov(2648,465)  ?(2684,499)  Buxhowden(2684,431)  Bernadotte(1899,455)  Lannes(2074,708)  Murat(2129,674)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  10k(2376,360)  4k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0112  type Massena, attack Kutuzov  ->  ok
  (typed and Enter)
view: <run>\frames\0112_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Massena (27,561) vs Kutuzov (substantial force) at Moravia — the balance of force looks unfavorable.
  WILL NOT — Davout: cannot march — the field is on soil we are not at war with
  WILL NOT — Soult: cannot march — the field is on soil we are not at war with
  WILL NOT — Napoleon: cannot march — the field is on soil we are not at war with
  Kutuzov does not stand alone: at least 1 enemy corps within reach of Moravia would march to him. Their columns gather slowly — Slow to concentrate: the bar 10 higher.
  What Moravia can feed is not known — the province is unscouted.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.


[Combat] Massena leads the charge! (Aggressive: +15% attack)
[Shield] Kutuzov's DEFENSIVE stance strengthens the line! (+15% defense)
[Shield] Kutuzov's methodical defense is exemplary! (Cautious: +20% total)
[Combat] Adjacent allies bolster Massena's attack! (+6%)
Massena engages in solid combat. Kutuzov holds the line. Casualties: Massena 6,243, Kutuzov's army 2,387. Both armies remain in the field.
[Materiel] Guns, horses and stores lost with the fallen: France -312g, Russia -119g.
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   RUSSIA LOSSES
   0
   0
   Buxhowden
   30,699 → 30,173
   ⚔
   Massena ◆
   Kutuzov ◆
   27,561 → 21,318
   32,549 → 30,688
   Davout — could not reach the field
   Soult — awaits explicit orders
   BATTLE OF MORAVIA
   click anywhere to skip ▸
   MORAVIA · TURN 6
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Russia
   -9
   T:5
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   8,171
   Inf:
   87,425
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [3/4 actions remaining]
   ► Massena, attack Kutuzov
   ⚔ Battle of Moravia ⚔
   MUSTER — Massena (27,561) vs Kutuzov (substantial force) at Moravia — the balance of force looks unfavorable.
   WILL NOT — Davout: cannot march — the field is on soil we are not at war with
   WILL NOT — Soult: cannot march — the field is on soil we are not at war with
   WILL NOT — Napoleon: cannot march — the field is on soil we are not at war with
   Kutuzov does not stand alone: at least 1 enemy corps within reach of Moravia would march to him. Their columns gather slowly — Slow to concentrate: the bar 10 higher.
   What Moravia can feed is not known — the province is unscouted.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Shield] Kutuzov's DEFENSIVE stance strengthens the line! (+15% defense)
   [Shield] Kutuzov's methodical defense is exemplary! (Cautious: +20% total)
   [Combat] Adjacent allies bolster Massena's attack! (+6%)
   Massena engages in solid combat. Kutuzov holds the line. Casualties: Massena 6,243, Kutuzov's army 2,387. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -312g, Russia -119g.
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout halted at the frontier — the field lies on soil we are not at war with, and no order could send him there.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon halted at the frontier — the field lies on soil we are not at war with, and no order could send him there.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Kutuzov fought with Buxhowden beside him — massed effective strength: 32,549 (lead) + 12,619 committed (Buxhowden) = 45,168.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Kutuzov's supporting ally lost 526 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "They had the ground and the luck. Luck runs out."
   Attack: Massena (Personality (aggressive) +15%)
   Defense: Kutuzov (Defensive stance +15%, Personality (cautious) +5%)
   Casualties: Massena 6,243 | Kutuzov's own corps 1,861
   Strength: Massena 27,561 → 21,318 | Kutuzov 32,549 → 30,688
   Berthier: "Where were Davout, Soult and Napoleon? Massena held the field alone — reinforcement never came."
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Ney(2249,485)  Teulie(2305,463)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout +3(2471,515)  ?(2127,138)  Brunswick(2126,103)  Kutuzov(2638,496)  Buxhowden(2694,462)  Bernadotte(1899,455)  Lannes(2074,708)  Murat(2129,674)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  10k(2376,360)  4k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0113  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Massena ◆' (Control, layer 121))
view: <run>\frames\0113_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE ASSAULT FAILS
   FRANCE LOSSES
   RUSSIA LOSSES
   6,243
   2,387
   Buxhowden
   30,699 → 30,173
   ⚔
   Massena ◆
   Kutuzov ◆
   27,561 → 21,318
   32,549 → 30,688
   Davout — could not reach the field
   Soult — awaits explicit orders
   Berthier: “The Emperor watched this field. Where were Davout, Soult and Napoleon? Massena held the field alone — reinforcement never came.” / Kutuzov: "The old man sleeps with one eye open. It was open today."
   BATTLE OF MORAVIA
   MORAVIA · TURN 6
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Kutuzov (Defensive stance +15%, Personality (cautious) +5%)
   Casualties: Massena 6,243 | Kutuzov's own corps 1,861
   Strength: Massena 27,561 → 21,318 | Kutuzov 32,549 → 30,688
   Berthier: "Where were Davout, Soult and Napoleon? Massena held the field alone — reinforcement never came."
map: unchanged (115 labels)
```

```
#0114  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0114_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Kutuzov (Defensive stance +15%, Personality (cautious) +5%)
   Casualties: Massena 6,243 | Kutuzov's own corps 1,861
   Strength: Massena 27,561 → 21,318 | Kutuzov 32,549 → 30,688
   Berthier: "Where were Davout, Soult and Napoleon? Massena held the field alone — reinforcement never came."
map: unchanged (115 labels)
```

```
#0115  type Davout, fortify Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0115_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Vienna. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   8,171
   Inf:
   87,425
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   MUSTER — Massena (27,561) vs Kutuzov (substantial force) at Moravia — the balance of force looks unfavorable.
   WILL NOT — Davout: cannot march — the field is on soil we are not at war with
   WILL NOT — Soult: cannot march — the field is on soil we are not at war with
   WILL NOT — Napoleon: cannot march — the field is on soil we are not at war with
   Kutuzov does not stand alone: at least 1 enemy corps within reach of Moravia would march to him. Their columns gather slowly — Slow to concentrate: the bar 10 higher.
   What Moravia can feed is not known — the province is unscouted.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Shield] Kutuzov's DEFENSIVE stance strengthens the line! (+15% defense)
   [Shield] Kutuzov's methodical defense is exemplary! (Cautious: +20% total)
   [Combat] Adjacent allies bolster Massena's attack! (+6%)
   Massena engages in solid combat. Kutuzov holds the line. Casualties: Massena 6,243, Kutuzov's army 2,387. Both armies remain in the field.
   [Materiel] Guns, horses and stores lost with the fallen: France -312g, Russia -119g.
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout halted at the frontier — the field lies on soil we are not at war with, and no order could send him there.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon halted at the frontier — the field lies on soil we are not at war with, and no order could send him there.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Kutuzov fought with Buxhowden beside him — massed effective strength: 32,549 (lead) + 12,619 committed (Buxhowden) = 45,168.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Kutuzov's supporting ally lost 526 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "They had the ground and the luck. Luck runs out."
   Attack: Massena (Personality (aggressive) +15%)
   Defense: Kutuzov (Defensive stance +15%, Personality (cautious) +5%)
   Casualties: Massena 6,243 | Kutuzov's own corps 1,861
   Strength: Massena 27,561 → 21,318 | Kutuzov 32,549 → 30,688
   Berthier: "Where were Davout, Soult and Napoleon? Massena held the field alone — reinforcement never came."
   ► Davout, fortify Vienna
   [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Vienna. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
   [0/4 actions remaining]
map: unchanged (115 labels)
```

```
#0116  type recruit infantry in Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0116_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte recruits 3,000 infantry for Rhineland (1 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 26% -> 29%
Infantry pool: 87,425 -> 84,425 [WARNING] Morale dropped to 29% — consider drilling before battle.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   7,571
   Inf:
   84,425
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry in Rhineland
   + Bernadotte recruits 3,000 infantry for Rhineland (1 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 26% -> 29%
   Infantry pool: 87,425 -> 84,425 [WARNING] Morale dropped to 29% — consider drilling before battle.
   [0/4 actions remaining]
map: unchanged (115 labels)
```

```
#0117  type build supply depot in Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0117_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Construction started: Supply Depot in Rhineland (2 turns, 300 gold) That was the last order the day could take, Sire — the turn ends when you say so.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   0/4
   Admin:
   0/2
   Gold:
   7,271
   Inf:
   84,425
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E) ▸]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► build supply depot in Rhineland
   Construction started: Supply Depot in Rhineland (2 turns, 300 gold) That was the last order the day could take, Sire — the turn ends when you say so.
   [0/4 actions remaining]
map: unchanged (115 labels)
```

```
#0118  click End Turn  ->  ok
  (clicked at (929, 978))
view: <run>\frames\0118_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 6
   RUSSIA / ──────────────────────────── / - Kutuzov fortifies position / - Bennigsen moves to Lithuania / - Bennigsen moves to Podolia / - Bennigsen moves to Moravia /  / BAVARIA / ──────────────────────────── / - Deroy holds position / - Deroy recruits troops /  / ──────────────────────────── / Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sigh …
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   9,521
   Inf:
   86,050
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Davout, fortify Vienna
   [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Vienna. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
   [0/4 actions remaining]
   ► recruit infantry in Rhineland
   + Bernadotte recruits 3,000 infantry for Rhineland (1 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 26% -> 29%
   Infantry pool: 87,425 -> 84,425 [WARNING] Morale dropped to 29% — consider drilling before battle.
   [0/4 actions remaining]
   ► build supply depot in Rhineland
   Construction started: Supply Depot in Rhineland (2 turns, 300 gold) That was the last order the day could take, Sire — the turn ends when you say so.
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 7 BEGINS
   ═══════════════════════════════════════
   Income: 2873g | Occupation: -100g | Contributions: -110g | Charges of Empire: -501g | Admiralty: -90g | Blockade: -368g | Other: +1606g | Upkeep: -1060g | Net: +2250g | Spent: 900g
   Treasury: 9,521g
   Actions refreshed: 4/4
   Ney's army is recovering. Effectiveness penalty: -15%.
   Davout's resolve hardens behind his earthworks (1/3) — his next assault will strike +8% harder. (Iron Resolve)
   Davout's fortifications strengthen: +12% defense (MAX)
   Crowded at Vienna: Davout loses 540 troops to the press of 4 corps on one province's roads
   Crowded at Vienna: Soult loses 626 troops to the press of 4 corps on one province's roads
   Crowded at Vienna: Massena loses 639 troops to the press of 4 corps on one province's roads
   Crowded at Vienna: Napoleon loses 208 troops to the press of 4 corps on one province's roads
   Supply shortage at Moravia: Kutuzov loses 658 troops
   Supply shortage at Moravia: Buxhowden loses 647 troops
   Supply shortage at Moravia: Bennigsen loses 106 troops
   Supply shortage at Tyrol: Lannes loses 141 troops
   Supply shortage at Tyrol: Murat loses 183 troops
   Garrison at Vienna reinforced: 4,000 -> 6,000
   Holland loyalty 93 (-2): satellite drift, the lord's defeats
   Kingdom of Italy loyalty 97 (-3): satellite drift, the lord's defeats
   Switzerland loyalty 85 (-4): satellite drift, the lord's defeats
   Britain subsidizes Russia with 200 gold.
   Russia has downgraded relations with Austria: ALLIANCE → DEFENSIVE_ALLIANCE.
   Territorial rivalry between Russia and Prussia grows.
   Russia has downgraded relations with Sweden: OPEN_BORDERS → PEACE.
   Prussia declares war on Hanover — The Hanoverian Prize.
   Berthier notes that Bernadotte has grown restless — he has not seen laurels while Massena wins them. I recommend giving him meaningful orders soon.
   Berthier: Enemy forces spotted near Vienna! Bennigsen (4,844 troops) at Moravia.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Teulie(2377,248)  Ney(2276,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout +3(2471,515)  ?(2127,138)  Brunswick(2126,103)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Bernadotte(1899,455)  ?(1079,763)  Paget(1079,729)  Lannes(2074,708)  Murat(2129,674)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  10k(2376,360)  6k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0119  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0119_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   9,521
   Inf:
   86,050
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Bennigsen — Moravia — 4,844 [confirmed]
   Hohenlohe — Silesia — substantial force [partial]
   Archduke Charles — Carniola — small force [partial]
   Archduke John — Carniola — small force [partial]
   Brunswick — Berlin — large force [partial]
   Paget — Gascony — screening force [partial]
   Castanos — Normandy — small force [partial]
   Podolia garrison — Podolia — garrison — screening force [partial]
   TURN EVENTS
   Ney's army is recovering. Effectiveness penalty: -15%.
   Davout's fortifications strengthen: +12% defense (MAX)
   Supply cost you 2,337 men, at Vienna and Tyrol.
   Garrison at Vienna reinforced: 4,000 -> 6,000
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Berthier notes that Bernadotte has grown restless — he has not seen laurels while Massena wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   War exhaustion grows — France nears breaking point (exhaustion: 62).
   Intelligence reports Britain has raised Wellesley to high command.
   An envoy from Russia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   Prussia has declared war on Hanover.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   Relations with Prussia have worsened significantly (-15 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Russia — Armistice Losing
   - Switzerland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-8)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (117 labels)
```

```
#0120  click Envoys  ->  ok
  (clicked at (3381, 18))
view: <run>\frames\0120_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   ACTIVE
   Russia
   Proposal
   Open ▸
   Turn 6
   Incoming proposal: Armistice
   WAITING
   Switzerland
   Proposal
   Open ▸
   Turn 7
   Incoming proposal: Client's Petition
   controls: {ACTIVE}  {WAITING}  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (117 labels)
```

```
#0121  click ACTIVE  ->  ok
  (clicked at (1829, 283))
view: <run>\frames\0121_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Czartoryski (Schemer) of Russia /  / Proposes: Armistice / Terms: /   - Proposal: Armistice / Assessment: GENEROUS /  / War Summary / War score: -8 v (Battle -6) / Settlement: White Peace / Objective: Defense - the homeland — 28 of 28 provinces held (inactive) / Ticking: +0 / Duration: 5 turns   Battles: 0W / 2L / Casualties: ours 10344 / theirs 3427 /  / Armistice Terms /   A 5 …
   controls: [Accept]  [Counter]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   9,521
   Inf:
   86,050
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (117 labels)
```

```
#0122  click Accept  ->  ok
  (clicked at (1604, 687))
view: <run>\frames\0122_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Chancery of Helvetia (Dove) of Switzerland /  / The petition: /   - Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +10, its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Responding to Russia's proposal: accepted
   You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia.
map: unchanged (117 labels)
```

```
#0123  click Grant  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0123_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Settlement Ratified @(3435,64)]  [icon: Treasury in deficit @(3477,64)]  [icon: Treaty with Russia @(3519,64)]  [icon: Diplomatic Action Accepted @(3561,64)]  [+15]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain
   -2
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [Britain]  [Russia  5t]  [Prussia vs Hanover]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   9,521
   Inf:
   86,050
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (85 → 95); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (117 labels)
```

```
#0124  type is Paris safe?  ->  ok
  (typed and Enter)
view: <run>\frames\0124_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Paris is ours, Sire, held by a garrison of 25,000. Threats we can see: Paget of Britain is at Gascony, two marches off (screening force). It is safe for a turn or two, no longer.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► is Paris safe?
   Paris is ours, Sire, held by a garrison of 25,000. Threats we can see: Paget of Britain is at Gascony, two marches off (screening force). It is safe for a turn or two, no longer.
map: unchanged (117 labels)
```

```
#0125  type Bernadotte, march to Gascony and drive out Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0125_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['objection'], region_panel=no
reply: ok Bernadotte challenges the order: 'That road to Gascony runs through enemy country, Sire. It is dangerous.'
── ObjectionDialog (layer 108) ──
   BERNADOTTE OBJECTS
   "Bernadotte challenges the order: 'That road to Gascony runs through enemy country, Sire. It is dangerous.'"
   Personality: Cautious
   Trust: 40 (Strained)
   Track record: Neutral
   Authority: 95
   controls: [Trust: Bernadotte fortifies position (1 AP, +3 trust)]  [Proceed through danger (2 AP, -12 trust)]  [Accept: Safe route (2 AP, +3 trust)]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   9,521
   Inf:
   86,050
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   TURN EVENTS
   Ney's army is recovering. Effectiveness penalty: -15%.
   Davout's fortifications strengthen: +12% defense (MAX)
   Supply cost you 2,337 men, at Vienna and Tyrol.
   Garrison at Vienna reinforced: 4,000 -> 6,000
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Berthier notes that Bernadotte has grown restless — he has not seen laurels while Massena wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   War exhaustion grows — France nears breaking point (exhaustion: 62).
   Intelligence reports Britain has raised Wellesley to high command.
   An envoy from Russia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   Prussia has declared war on Hanover.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   Relations with Prussia have worsened significantly (-15 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Russia — Armistice Losing
   - Switzerland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-8)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (85 → 95); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► is Paris safe?
   Paris is ours, Sire, held by a garrison of 25,000. Threats we can see: Paget of Britain is at Gascony, two marches off (screening force). It is safe for a turn or two, no longer.
   ► Bernadotte, march to Gascony and drive out Paget
   ⚠ Marshal Bernadotte raises concerns...
map: unchanged (117 labels)
```

```
#0126  click Safe route  ->  ok
  (clicked at (2143, 582))
view: <run>\frames\0126_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 93 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Settlement Ratified @(3435,64)]  [icon: Treasury in deficit @(3477,64)]  [icon: Treaty with Russia @(3519,64)]  [icon: Diplomatic Action Accepted @(3561,64)]  [+15]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain
   -2
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [Britain]  [Russia  5t]  [Prussia vs Hanover]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   9,521
   Inf:
   86,050
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► You seek a middle ground with your marshal.
   Bernadotte will take a safer route to Gascony. Moves to Lorraine.
   [2/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Teulie(2377,248)  Ney(2276,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout +3(2471,515)  ?(2127,138)  Brunswick(2126,103)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(1079,763)  Paget(1079,729)  Lannes(2074,708)  Murat(2129,674)  Bernadotte(1655,391)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  10k(2376,360)  6k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0127  type Massena, move to Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0127_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Massena moves from Vienna to Bohemia (234 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   9,521
   Inf:
   86,050
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, move to Bohemia
   → Massena moves from Vienna to Bohemia (234 lost to march)
   [1/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Teulie(2377,248)  Ney(2249,485)  Massena(2305,451)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Soult(2471,505)  Napoleon(2498,471)  ?(2127,138)  Brunswick(2126,103)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(1079,763)  Paget(1079,729)  Lannes(2074,708)  Murat(2129,674)  Bernadotte(1655,391)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  10k(2376,360)  6k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0128  type Murat, move to Munich  ->  ok
  (typed and Enter)
view: <run>\frames\0128_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat moves from Tyrol to Munich (345 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   9,521
   Inf:
   86,050
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, move to Munich
   → Murat moves from Tyrol to Munich (345 lost to march)
   [0/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Teulie(2377,248)  Ney(2249,485)  Massena(2305,451)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Soult(2471,505)  Napoleon(2498,471)  ?(2127,138)  Brunswick(2126,103)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(1079,763)  Paget(1079,729)  Lannes(2102,708)  Bernadotte(1655,391)  Murat(1994,618)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  10k(2376,360)  6k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0129  type recruit cavalry for Murat  ->  ok
  (typed and Enter)
view: <run>\frames\0129_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Berthier frowns. 'We do not control Munich, Your Majesty — Murat stands there on foreign ground. Recruitment is impossible there.'
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit cavalry for Murat
   Berthier frowns. 'We do not control Munich, Your Majesty — Murat stands there on foreign ground. Recruitment is impossible there.'
map: unchanged (119 labels)
```

```
#0130  type recruit infantry in Lorraine  ->  ok
  (typed and Enter)
view: <run>\frames\0130_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte recruits 3,000 infantry for Lorraine (0 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 29% -> 30%
Infantry pool: 86,050 -> 83,050 [WARNING] Morale dropped to 30% — consider drilling before battle.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   8,921
   Inf:
   83,050
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   Relations with Prussia have worsened significantly (-15 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Russia — Armistice Losing
   - Switzerland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-8)
   COALITION THREAT
   Threat: 93/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   Responding to Russia's proposal: accepted
   You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (85 → 95); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► is Paris safe?
   Paris is ours, Sire, held by a garrison of 25,000. Threats we can see: Paget of Britain is at Gascony, two marches off (screening force). It is safe for a turn or two, no longer.
   ► Bernadotte, march to Gascony and drive out Paget
   ⚠ Marshal Bernadotte raises concerns...
   ► You seek a middle ground with your marshal.
   Bernadotte will take a safer route to Gascony. Moves to Lorraine.
   [2/4 actions remaining]
   ► Massena, move to Bohemia
   → Massena moves from Vienna to Bohemia (234 lost to march)
   [1/4 actions remaining]
   ► Murat, move to Munich
   → Murat moves from Tyrol to Munich (345 lost to march)
   [0/4 actions remaining]
   ► recruit cavalry for Murat
   Berthier frowns. 'We do not control Munich, Your Majesty — Murat stands there on foreign ground. Recruitment is impossible there.'
   ► recruit infantry in Lorraine
   + Bernadotte recruits 3,000 infantry for Lorraine (0 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 29% -> 30%
   Infantry pool: 86,050 -> 83,050 [WARNING] Morale dropped to 30% — consider drilling before battle.
   [0/4 actions remaining]
map: unchanged (119 labels)
```

```
#0131  click Ledger  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0131_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Late December 1805 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 95 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Idle  Location:  …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► recruit infantry in Lorraine
   + Bernadotte recruits 3,000 infantry for Lorraine (0 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 29% -> 30%
   Infantry pool: 86,050 -> 83,050 [WARNING] Morale dropped to 30% — consider drilling before battle.
   [0/4 actions remaining]
map: unchanged (119 labels)
```

```
#0132  click LAWS  ->  ok
  (clicked at (2123, 283))
view: <run>\frames\0132_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) ──
   STRATEGIC LEDGER
   THE LAWS OF STATE / Late December 1805 /  / The Grand Quartier Général  Berthier's Imperial Headquarters, expanded 1805–07 /   Berthier's headquarters grown into a true general staff: one more order carried each day. /   • +1 order of the day, from the next refill /   9,000 gold to enact · 300 gold a turn /  /     Enact    The Grand Quartier Général costs 9,000 gold; the treasury holds 8,921. /  / …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS](disabled: You are reading this book)  <Enact>  <Enact>  <Enact>  <Enact>  <Enact>
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► recruit infantry in Lorraine
   + Bernadotte recruits 3,000 infantry for Lorraine (0 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 29% -> 30%
   Infantry pool: 86,050 -> 83,050 [WARNING] Morale dropped to 30% — consider drilling before battle.
   [0/4 actions remaining]
map: unchanged (119 labels)
```

```
#0133  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0133_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain
   -2
   T:6
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [Britain]  [Russia  5t]  [Prussia vs Hanover]
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► recruit infantry in Lorraine
   + Bernadotte recruits 3,000 infantry for Lorraine (0 regions away) (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 29% -> 30%
   Infantry pool: 86,050 -> 83,050 [WARNING] Morale dropped to 30% — consider drilling before battle.
   [0/4 actions remaining]
map: unchanged (119 labels)
```

```
#0134  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0134_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 7
   RUSSIA / ──────────────────────────── / - Bennigsen changes stance to defensive / - Bennigsen fortifies position / - Buxhowden holds position /  / BAVARIA / ──────────────────────────── / - Deroy detaches a garrison / - Deroy holds position / - Deroy recruits troops /  / ──────────────────────────── / Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond  …
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 91 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,778
   Inf:
   84,575
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 8 BEGINS
   ═══════════════════════════════════════
   Income: 2930g | Occupation: -100g | Contributions: -110g | Charges of Empire: -681g | Infrastructure: -20g | Admiralty: -90g | Blockade: -368g | Other: +1408g | Upkeep: -1112g | Net: +1857g | Spent: 600g
   Treasury: 10,778g
   Actions refreshed: 4/4
   Ney's army has fully recovered and is combat ready.
   Davout's resolve hardens behind his earthworks (2/3) — his next assault will strike +16% harder. (Iron Resolve)
   Construction complete: Supply Depot in Rhineland!
   Supply shortage at Moravia: Kutuzov loses 633 troops
   Supply shortage at Moravia: Buxhowden loses 622 troops
   Supply shortage at Moravia: Bennigsen loses 102 troops
   Garrison at Vienna reinforced: 6,000 -> 8,000
   Garrison at Hanover reinforced: 5,000 -> 7,000
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Britain and Portugal grows.
   Russia has downgraded relations with Austria: DEFENSIVE_ALLIANCE → NON_AGGRESSION.
   Territorial rivalry between Russia and Sweden grows.
   Russia and Naples have signed a Non-Aggression Pact.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Ney(2249,485)  Massena(2277,451)  Teulie(2305,416)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Soult(2471,505)  Napoleon(2498,471)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(1834,103)  Brunswick(1834,51)  ?(1079,763)  Paget(1079,729)  Lannes(2102,708)  Bernadotte(1655,391)  Murat(1994,618)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  ?(2673,261)  10k(2376,360)  3k(2090,538)  8k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  25k(1294,516)  12k(1193,417)  7k(1710,145)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0135  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0135_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,778
   Inf:
   84,575
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ Morale failing (30) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Lannes — Tyrol — 13,326 — 5 turns idle.
   ⚠ Starving — supply has failed at Tyrol four turns running.
   - Ney — Bohemia — 7,727 — Awaiting orders. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Napoleon — Vienna — 6,746 — Awaiting orders.
   > Teulie — Bohemia — 6,657 — Moving to Milan — 2 turns out.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,310 [confirmed]
   Kutuzov — Moravia — 29,397 [confirmed]
   Buxhowden — Moravia — 28,904 [confirmed]
   Bennigsen — Moravia — 4,742 [confirmed]
   Hohenlohe — Silesia — substantial force [partial]
   Archduke Charles — Carniola — substantial force [partial]
   Archduke John — Carniola — small force [partial]
   Brunswick — Brunswick — large force [partial]
   Paget — Gascony — screening force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Ney's army has fully recovered and is combat ready.
   Construction complete: Supply Depot in Rhineland!
   Garrison at Vienna reinforced: 6,000 -> 8,000
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   DIPLOMATIC EVENTS
   Sire — Russia and France have signed the Armistice.
   A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   Talleyrand reports: Russia and Naples have signed the Non-Aggression Pact.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-2)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
map: unchanged (122 labels)
```

```
#0136  click Ledger  ->  ok
  (clicked at (138, 18))
view: <run>\frames\0136_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 91 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Settlement Ratified @(3435,64)]  [icon: Treasury in deficit @(3477,64)]  [icon: Treaty with Russia @(3519,64)]  [icon: Diplomatic Action Accepted @(3561,64)]  [+15]
── StrategicLedger (layer 50) ──
   STRATEGIC LEDGER
   ═══ FORCES ═══ / Early January 1806 / The muster of your corps — strength, morale, and each marshal's temper. Keys 1–8 turn the ledger's books (Alt+1–8 while you type); press T to close it. /  / THE CABINET — Talleyrand is at the Cabinet, free to send: press F1, choose a court, and send him on a mission. /  / Authority: 95 (Strong) /  / THE EMPEROR — Napoleon  Infantry /   Status: Idle  Location:  …
   controls: [Pin]  [icon @(2193,246)]  [FORCES](disabled: You are reading this book)  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
map: unchanged (122 labels)
```

```
#0137  click LAWS  ->  ok
  (clicked at (2123, 283))
view: <run>\frames\0137_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) ──
   STRATEGIC LEDGER
   THE LAWS OF STATE / Early January 1806 /  / The Grand Quartier Général  Berthier's Imperial Headquarters, expanded 1805–07 /   Berthier's headquarters grown into a true general staff: one more order carried each day. /   • +1 order of the day, from the next refill /   9,000 gold to enact · 300 gold a turn /   Not in force. /  /     Enact    9,000 gold now, then 300 gold a turn; one more order each …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS](disabled: You are reading this book)  <Enact>  <Enact>  <Enact>  <Enact>  <Enact>  <Enact>
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
map: unchanged (122 labels)
```

```
#0138  click#1 Enact  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0138_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (disabled)
open: screens=['ledger'], pinned=-, popups=['clarification'], region_panel=no
── ClarificationPopup (layer 102) ──
   THE COUNCIL OF STATE ASKS:
   "The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown into a true general staff: one more order carried each day. 9,000 gold now, then 300 gold a turn; one more order each day from the next refill. The treasury holds 10,778 gold. Enact it? (yes / no)"
   controls: [Enact the Grand Quartier Général]  [Not now]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 91 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── StrategicLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,778
   Inf:
   84,575
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ⚠ Starving — supply has failed at Tyrol four turns running.
   - Ney — Bohemia — 7,727 — Awaiting orders. Morale:0%
   ⚠ Morale failing (0) — the men waver. Two turns of drill would steady them (+10 morale; +15 with a training ground).
   - Napoleon — Vienna — 6,746 — Awaiting orders.
   > Teulie — Bohemia — 6,657 — Moving to Milan — 2 turns out.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,310 [confirmed]
   Kutuzov — Moravia — 29,397 [confirmed]
   Buxhowden — Moravia — 28,904 [confirmed]
   Bennigsen — Moravia — 4,742 [confirmed]
   Hohenlohe — Silesia — substantial force [partial]
   Archduke Charles — Carniola — substantial force [partial]
   Archduke John — Carniola — small force [partial]
   Brunswick — Brunswick — large force [partial]
   Paget — Gascony — screening force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Ney's army has fully recovered and is combat ready.
   Construction complete: Supply Depot in Rhineland!
   Garrison at Vienna reinforced: 6,000 -> 8,000
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   DIPLOMATIC EVENTS
   Sire — Russia and France have signed the Armistice.
   A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   Talleyrand reports: Russia and Naples have signed the Non-Aggression Pact.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-2)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
   ► enact the Grand Quartier Général
   The Council of State requests clarification...
map: unchanged (122 labels)
```

```
#0139  click Enact the Grand  ->  ok
  (clicked at (1829, 524))
view: <run>\frames\0139_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 91 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: Prussia Declares War! @(3393,64)]  [icon: Settlement Ratified @(3435,64)]  [icon: Treasury in deficit @(3477,64)]  [icon: Treaty with Russia @(3519,64)]  [icon: Diplomatic Action Accepted @(3561,64)]  [+15]
── StrategicLedger (layer 50) ──
   STRATEGIC LEDGER
   THE LAWS OF STATE / Early January 1806 /  / The Grand Quartier Général  Berthier's Imperial Headquarters, expanded 1805–07 /   Berthier's headquarters grown into a true general staff: one more order carried each day. /   • +1 order of the day, from the next refill /   9,000 gold to enact · 300 gold a turn /   In force since turn 8. /  /     Repeal    ends 300 gold a turn — its extra order of the d …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY]  [LAWS](disabled: You are reading this book)  <Repeal>  <Enact>  <Enact>  <Enact>
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   1,778
   Inf:
   84,575
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > enact the Grand Quartier Général confirmed
   The Grand Quartier Général is in force — enacted for 9,000 gold. It costs 300 gold a turn from now on. From the next refill, one more order each day.
   [4/4 actions remaining]
map: unchanged (122 labels)
```

```
#0140  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0140_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50): unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   The Council of State requests clarification...
   > enact the Grand Quartier Général confirmed
   The Grand Quartier Général is in force — enacted for 9,000 gold. It costs 300 gold a turn from now on. From the next refill, one more order each day.
   [4/4 actions remaining]
map: unchanged (122 labels)
```

```
#0141  type Ney, drill your men  ->  ok
  (typed and Enter; focus by grab_focus (the click did not focus the line))
view: <run>\frames\0141_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 10.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain
   -1
   T:7
   FOREIGN WARS
   controls: [THIRD COALITION  ▸]  [Britain]  [Russia  4t]  [Prussia vs Hanover]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   3/4
   Admin:
   1/2
   Gold:
   1,778
   Inf:
   84,575
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, drill your men
   Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 10.
   [3/4 actions remaining]
map: unchanged (122 labels)
```

```
#0142  type Lannes, move to Munich  ->  ok
  (typed and Enter)
view: <run>\frames\0142_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Lannes moves from Tyrol to Munich (266 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   2/4
   Admin:
   1/2
   Gold:
   1,778
   Inf:
   84,575
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, move to Munich
   → Lannes moves from Tyrol to Munich (266 lost to march)
   [2/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Ney(2249,485)  Massena(2277,451)  Teulie(2305,416)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Soult(2471,505)  Napoleon(2498,471)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(1834,103)  Brunswick(1834,51)  ?(1079,763)  Paget(1079,729)  Bernadotte(1655,391)  Lannes(1967,618)  Murat(2022,584)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  ?(2673,261)  10k(2376,360)  3k(2090,538)  8k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  25k(1294,516)  12k(1193,417)  7k(1710,145)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0143  type Murat, hunt down Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0143_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat pursues Paget (at Gascony). Cavalry charges through Franche-Comte -> Nivernais. Murat: "He is already beaten — he merely has not been told. I will tell him."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   0/4
   Admin:
   1/2
   Gold:
   1,778
   Inf:
   84,575
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, hunt down Paget
   Murat pursues Paget (at Gascony). Cavalry charges through Franche-Comte -> Nivernais. Murat: "He is already beaten — he merely has not been told. I will tell him."
   [0/4 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Hohenlohe(2673,118)  Ney(2249,485)  Massena(2277,451)  Teulie(2305,416)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Soult(2471,505)  Napoleon(2498,471)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(1834,103)  Brunswick(1834,51)  ?(1079,763)  Paget(1079,729)  Bernadotte(1655,391)  Lannes(1995,618)  Murat(1644,505)  ?(1193,308)  Castanos(1193,274)  Dumonceau(1660,203)  ?(2673,261)  10k(2376,360)  3k(2090,538)  8k(2470,651)  ?(2798,413)  ?(2126,239)  10k(1994,730)  25k(1294,516)  12k(1193,417)  ?(1691,692)  7k(1710,145)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0144  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0144_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 8
   RUSSIA / ──────────────────────────── / - Buxhowden holds position /  / BAVARIA / ──────────────────────────── / - Deroy holds position /  / ──────────────────────────── / Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 89 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   4,119
   Inf:
   86,000
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-2)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 91/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
   ► enact the Grand Quartier Général
   The Council of State requests clarification...
   > enact the Grand Quartier Général confirmed
   The Grand Quartier Général is in force — enacted for 9,000 gold. It costs 300 gold a turn from now on. From the next refill, one more order each day.
   [4/4 actions remaining]
   ► Ney, drill your men
   Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 10.
   [3/4 actions remaining]
   ► Lannes, move to Munich
   → Lannes moves from Tyrol to Munich (266 lost to march)
   [2/4 actions remaining]
   ► Murat, hunt down Paget
   Murat pursues Paget (at Gascony). Cavalry charges through Franche-Comte -> Nivernais. Murat: "He is already beaten — he merely has not been told. I will tell him."
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 9 BEGINS
   ═══════════════════════════════════════
   Income: 2977g | Occupation: -80g | Contributions: -110g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Blockade: -368g | Other: +1408g | Upkeep: -1076g | Net: +2341g | Spent: 9000g
   Treasury: 4,119g
   Actions refreshed: 5/5
   Ney is now locked in intensive drill. Cannot receive orders until training completes.
   Davout's resolve hardens behind his earthworks (3/3) — his next assault will strike +24% harder. (Iron Resolve)
   Supply shortage at Moravia: Kutuzov loses 841 troops
   Supply shortage at Moravia: Buxhowden loses 827 troops
   Supply shortage at Moravia: Bennigsen loses 135 troops
   Garrison at Vienna reinforced: 8,000 -> 10,000
   Garrison at Hanover reinforced: 0 -> 2,000
   Teulie's contingent comes home crowned with victory — 6,524 of 7,500 men. The Kingdom of Italy rejoices (+5 loyalty).
   Britain subsidizes Russia with 300 gold.
   Russia has downgraded relations with Austria: NON_AGGRESSION → OPEN_BORDERS.
   Berthier reports that Soult appears envious of Massena's laurels — he has grown scrupulous to the point of reproach.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Ardennes(1486,378)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney(2249,485)  Massena(2305,451)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Soult(2471,505)  Napoleon(2498,471)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(2407,2)  ?(1079,763)  Paget(1079,729)  Lannes(1995,618)  ?(811,816)  Castanos(811,782)  Bernadotte(1525,411)  Murat(1644,505)  Dumonceau(1660,203)  ?(2673,261)  10k(2376,360)  3k(2090,538)  10k(2470,651)  ?(2798,413)  ?(2126,239)  ?(2407,111)  10k(1994,730)  25k(1294,516)  12k(1193,417)  ?(1691,692)  2k(1710,145)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0145  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0145_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   4,119
   Inf:
   86,000
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   - Napoleon — Vienna — 6,746 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,310 [confirmed]
   Kutuzov — Moravia — 28,556 [confirmed]
   Buxhowden — Moravia — 28,077 [confirmed]
   Bennigsen — Moravia — 4,607 [confirmed]
   Hohenlohe — Silesia — substantial force [partial]
   Archduke Charles — Carniola — substantial force [partial]
   Archduke John — Carniola — small force [partial]
   Brunswick — Berlin — large force [partial]
   Paget — Gascony — screening force [partial]
   Castanos — Bordelais — small force [partial]
   TURN EVENTS
   Ney is now locked in intensive drill. Cannot receive orders until training completes.
   Garrison at Vienna reinforced: 8,000 -> 10,000
   Berthier reports that Soult appears envious of Massena's laurels — he has grown scrupulous to the point of reproach.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   DIPLOMATIC EVENTS
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Britain has offered terms to settle France vs Britain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Teulie's contingent comes home crowned with victory — 6,524 of 7,500 men. The Kingdom of Italy rejoices (+5 loyalty).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Settlement Offer
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (121 labels)
```

```
#0146  click Envoys  ->  ok
  (clicked at (3395, 18))
view: <run>\frames\0146_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   SETTLEMENT OFFER FROM BRITAIN /  / France vs Britain /  / "His Majesty's Government offers terms for France vs Britain. No indemnity is asked and none is offered; London proposes only that the guns fall silent." /  / Their proposed terms: /   • Peace /   • Status quo: Britain retains Leon. /  / Covered enemies: Britain /  / "Sire, Britain has dispatched a settlement of France vs Britain. No indemn …
   controls: [Review Settlement Offer]  [Request Revision]  [Reject Offer]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   4,119
   Inf:
   86,000
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (121 labels)
```

```
#0147  click Review Settlement Offer  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0147_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   Settlement of France vs Britain — ready for ratification / France vs Britain - Separate settlement / STAGED FOR REVIEW — the terms are frozen. Ratify, revise, or return to shaping. / Covered enemies: Britain / Still at war: Russia / Will carry — these are the terms they offered. / Sire, this settlement of France vs Britain seats 1 courts at the table. Every court at the table will sign; the settle …
   The table /   * Britain - Their own terms (11/50) White peace /       Blocker: Settlement legitimacy /       Castlereagh for Britain: these are the terms Britain laid before France; Britain does not haggle with its own dispatch. / This peace carries.
   Sire, the white peace for France vs Britain is ready: no terms exchanged, no map redrawn — only the war ends. Ratify and the field falls quiet. /  / Allies and Standing /   * France - Seat at settlement (Attackers, war leader) /   * Britain - Seat at settlement (Defenders, war leader) /   * Holland - No settlement standing (Attackers) /   * Spain - No settlement standing (Attackers) /  / Warnings  …
   controls: [Ratify White Peace]  [Open War Detail]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 89 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: accept settlement offer
map: unchanged (121 labels)
```

```
#0148  scroll 1828 600 down 10  ->  ok
  (scrolled down 10 at (1828, 600))
view: <run>\frames\0148_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   Directing Talleyrand: accept settlement offer
map: unchanged (121 labels)
```

```
#0149  click Ratify White Peace  ->  ok
  (clicked at (1455, 876))
view: <run>\frames\0149_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 44 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: Settlement Ratified (x2) @(3393,64)]  [icon: Marshal Soult seeks an audience @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Treasury in deficit @(3519,64)]  [icon: The Moniteur is out (x2) @(3561,64)]  [+19]
── DiplomaticLedger (layer 50) ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 7/7
   ═══ ACTIVE TREATIES ═══ /  / Sweden ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (7 turns ago) /  / Russia ↔ Naples: Non Aggression /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 8 (1 turns ago) /  / Portugal ↔ France: Open Borders /   Clauses: Gold payment: 60 (Portugal -> France) /   Duration: permanent    …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES](disabled: You are reading this book)  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <v Settlement of France vs Britain: settlement ratified.>  <v Settlement of France vs Austria: settlement ratified.>
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   4,119
   Inf:
   86,000
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Hohenlohe — Silesia — substantial force [partial]
   Archduke Charles — Carniola — substantial force [partial]
   Archduke John — Carniola — small force [partial]
   Brunswick — Berlin — large force [partial]
   Paget — Gascony — screening force [partial]
   Castanos — Bordelais — small force [partial]
   TURN EVENTS
   Ney is now locked in intensive drill. Cannot receive orders until training completes.
   Garrison at Vienna reinforced: 8,000 -> 10,000
   Berthier reports that Soult appears envious of Massena's laurels — he has grown scrupulous to the point of reproach.
   Soult seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   DIPLOMATIC EVENTS
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Britain has offered terms to settle France vs Britain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Teulie's contingent comes home crowned with victory — 6,524 of 7,500 men. The Kingdom of Italy rejoices (+5 loyalty).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Settlement Offer
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   Directing Talleyrand: accept settlement offer
   Directing Talleyrand: confirm settlement
   Settlement Ratified: France vs Britain (3 pairs resolved). Status quo: Leon stays British by the treaty.
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (121 labels)
```

```
#0150  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0150_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (121 labels)
```

```
#0151  click_at 3435 64  ->  ok
  (clicked at (3435, 64) on @Button@5967  (Button, layer 75))
view: <run>\frames\0151_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 44 / 100
   Turn 9 — Late January 1806
   Imperial Box
   Marshal Soult seeks an audience
   T8
   Soult asks to be heard — at your leisure, Sire; nothing waits on it. His card is on the Generals screen.
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: Settlement Ratified (x2) @(3393,64)]  [icon: Marshal Soult seeks an audience @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Treasury in deficit @(3519,64)]  [icon: The Moniteur is out (x2) @(3561,64)]  [+19]  [Hear him]  [Keep]  [Acknowledge]
── DiplomaticLedger (layer 50): unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (121 labels)
```

```
#0152  click Hear him  ->  ok
  (clicked at (3399, 221))
view: <run>\frames\0152_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114) ──
   SOULT — Marshal Soult seeks an audience
   Give him a command is closed — There is no enemy within his reach to send him against.
   "My orders have been carried out exactly, Sire. I note that Massena was given orders worth carrying out." /  / Sire, Soult's dispatches have become unusually detailed — obsessively so. Staff report he feels his current assignment is... beneath his abilities.
   Free, and it fixes nothing. For 2 more turns he brings his 20,243 men to any battle Massena leads, but no more — the goodwill that made him worth a quarter more is gone, and the quarrel may harden further.
   His patience is bought — the grievance shortens by 2 turns, and for 6 turns the quarrel cannot harden further.
   Trust -5. The grievance shortens by 1 turn. His patrols pause a turn in reluctant compliance.
   controls: [Let it stand   [Free]]  [Reassign   [1 AP]]  [Rebuke]  [Later (he will return)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 44 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: Settlement Ratified (x2) @(3393,64)]  [icon: Marshal Soult seeks an audience @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Treasury in deficit @(3519,64)]  [icon: The Moniteur is out (x2) @(3561,64)]  [+19]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   4,119
   Inf:
   86,000
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (121 labels)
```

```
#0153  click Reassign  ->  ok
  (clicked at (1825, 596))
view: <run>\frames\0153_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 44 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: Settlement Ratified (x2) @(3393,64)]  [icon: Prussia Declares War! @(3435,64)]  [icon: Treasury in deficit @(3477,64)]  [icon: The Moniteur is out (x2) @(3519,64)]  [icon: Britain Left Coalition @(3561,64)]  [+18]
── DiplomaticLedger (layer 50): unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/5
   Admin:
   2/2
   Gold:
   4,119
   Inf:
   86,000
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (121 labels)
```

```
#0154  click NATIONS  ->  ok
  (clicked at (1466, 273))
view: <run>\frames\0154_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 7/7
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  / How Europe Reads France /   Read as: The hegemon of Europe — 41% of the continent's weight. /   The courts believe he will go as far as alliance (alarm 44). /   They think he is coming for Austria — his corps stand against their soil. /  / The Em …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (121 labels)
```

```
#0155  click_at 2655 236  ->  ok
  (clicked at (2655, 236) on BackgroundOverlay  (ColorRect, layer 50))
view: <run>\frames\0155_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   FOREIGN WARS
   controls: [Russia  3t]  [Prussia vs Hanover]
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (121 labels)
```

```
#0156  click ⚖ Diplomacy  ->  ok
  (clicked at (829, 978))
view: <run>\frames\0156_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   Treaties (10)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -74 (Hostile)]  [Prussia  —  Open Borders  |  -23 (Wary)]  [Spain  —  Alliance  |  +32 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -12 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (121 labels)
```

```
#0157  click the terms  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0157_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▾ hide the terms /     ✓ 1 administrative action (you have 2) /     • 45 titled provinces (38 of 45) /     ✓ Paris held /     ✓ the Emperor free /     ✓ no satellite on the brink of rebellion /     ✓ Europe's alarm below 80 (now 44 — rising 1 a turn: our bloc's weight in Europe +1, the designs we deny +1 against 3 of decay (one, plus one for each court at  …
   The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and settle).
   controls: [icon: Close (Esc) @(2075,284)]  <▾ hide the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (121 labels)
```

```
#0158  click hide the terms  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0158_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   Treaties (10)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -74 (Hostile)]  [Prussia  —  Open Borders  |  -23 (Wary)]  [Spain  —  Alliance  |  +32 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -12 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (121 labels)
```

```
#0159  scroll 1825 593 down 10  ->  ok
  (scrolled down 10 at (1825, 593))
view: <run>\frames\0159_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (6)
   controls: [icon: Close (Esc) @(2075,284)]  [Hesse  —  Non-Aggression  |  0 (Neutral)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  +20 (Neutral)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Britain  —  Peace  |  -90 (Hostile)]  [Austria  —  Peace  |  -75 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (121 labels)
```

```
#0160  scroll 1825 593 down 10  ->  ok
  (scrolled down 10 at (1825, 593))
view: <run>\frames\0160_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (6)
   controls: [icon: Close (Esc) @(2075,284)]  [Kingdom of Italy  —  Vassal  |  +20 (Neutral)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Britain  —  Peace  |  -90 (Hostile)]  [Austria  —  Peace  |  -75 (Hostile)]  [Sweden  —  Peace  |  -52 (Hostile)]  [Naples  —  Peace  |  -22 (Wary)]  [Hanover  —  Peace  |  -42 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (121 labels)
```

```
#0161  click Naples  ->  ok
  (clicked at (1825, 603))
view: <run>\frames\0161_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY — Naples
   DP: 7
   TALLEYRAND'S ASSESSMENT — NAPLES / Status: Peace   Relation: -22 (Wary) /  / "Naples maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate.
   Relations with Naples stand at -22; an Open Borders needs -20.
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Open Borders (1 DP)  —  Uncertain — a counter is likely](disabled: Relations with Naples stand at -22; an Open Borders needs -20.)  [Declare War (1 DP)]  [Send Ultimatum (2 DP)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Court Nation (2 DP)  —  +8 relation/turn, proposals +2/turn courted (max +10), 20% blowback]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (121 labels)
```

```
#0162  click Back  ->  ok
  (clicked at (1774, 740))
view: <run>\frames\0162_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   Treaties (10)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -74 (Hostile)]  [Prussia  —  Open Borders  |  -23 (Wary)]  [Spain  —  Alliance  |  +32 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -12 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (121 labels)
```

```
#0163  click Prussia  ->  ok
  (clicked at (1825, 561))
view: <run>\frames\0163_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY — Prussia
   DP: 7
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Open Borders   Relation: -23 (Wary) /  / "Our borders with Prussia are open, but trust remains shallow. A non-aggression pact would formalize the thaw." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. /  / KEY FACTORS /   + Base willingness (+10) /   + Diplomatic skil …
   Relations with Prussia stand at -23; a Non-Aggression needs 0.
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Non-Aggression (1 DP)  —  Unlikely](disabled: Relations with Prussia stand at -23; a Non-Aggression needs 0.)  [Propose Vassal (3 DP)  —  Hopeless]  [Declare War (1 DP)]  [Break Treaty (1 DP)]  [Downgrade (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (121 labels)
```

```
#0164  click Cancel  ->  ok
  (clicked at (1884, 740))
view: <run>\frames\0164_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (121 labels)
```

```
#0165  type what borders Dresden?  ->  ok
  (typed and Enter)
view: <run>\frames\0165_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Dresden borders Berlin, Bohemia, Brandenburg, Franconia, Moravia, Podolia, Posen, Silesia and Vienna, Sire.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► what borders Dresden?
   Dresden borders Berlin, Bohemia, Brandenburg, Franconia, Moravia, Podolia, Posen, Silesia and Vienna, Sire.
map: unchanged (121 labels)
```

```
#0166  type Massena, move to Dresden  ->  ok
  (typed and Enter)
view: <run>\frames\0166_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Massena moves from Bohemia to Dresden (289 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   4,119
   Inf:
   86,000
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, move to Dresden
   → Massena moves from Bohemia to Dresden (289 lost to march)
   [3/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Ardennes(1486,378)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Massena(2377,248)  Ney(2276,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Soult(2471,505)  Napoleon(2498,471)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(2407,2)  ?(1079,763)  Paget(1079,729)  Lannes(1995,618)  ?(811,816)  Castanos(811,782)  Bernadotte(1525,411)  Murat(1644,505)  Dumonceau(1660,203)  ?(2673,261)  10k(2376,360)  3k(2090,538)  10k(2470,651)  ?(2798,413)  ?(2126,239)  ?(2407,111)  10k(1994,730)  25k(1294,516)  12k(1193,417)  ?(1691,692)  2k(1710,145)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0167  type Soult, move to Dresden  ->  ok
  (typed and Enter)
view: <run>\frames\0167_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult moves from Vienna to Dresden (275 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   4,119
   Inf:
   86,000
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, move to Dresden
   → Soult moves from Vienna to Dresden (275 lost to march)
   [2/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Ardennes(1486,378)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Soult(2349,248)  Massena(2405,214)  Ney(2276,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Napoleon(2498,505)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(2407,2)  ?(1079,763)  Paget(1079,729)  Lannes(1995,618)  ?(811,816)  Castanos(811,782)  Bernadotte(1525,411)  Murat(1644,505)  Dumonceau(1660,203)  ?(2673,261)  10k(2376,360)  3k(2090,538)  10k(2470,651)  ?(2798,413)  ?(2126,239)  ?(2407,111)  10k(1994,730)  25k(1294,516)  12k(1193,417)  ?(1691,692)  2k(1710,145)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0168  type Napoleon, move to Dresden  ->  ok
  (typed and Enter)
view: <run>\frames\0168_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon moves from Vienna to Dresden (87 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   1/5
   Admin:
   2/2
   Gold:
   4,119
   Inf:
   86,000
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   Britain has offered terms to settle France vs Britain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Teulie's contingent comes home crowned with victory — 6,524 of 7,500 men. The Kingdom of Italy rejoices (+5 loyalty).
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Settlement Offer
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 89/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   Directing Talleyrand: accept settlement offer
   Directing Talleyrand: confirm settlement
   Settlement Ratified: France vs Britain (3 pairs resolved). Status quo: Leon stays British by the treaty.
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Soult bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   ► what borders Dresden?
   Dresden borders Berlin, Bohemia, Brandenburg, Franconia, Moravia, Podolia, Posen, Silesia and Vienna, Sire.
   ► Massena, move to Dresden
   → Massena moves from Bohemia to Dresden (289 lost to march)
   [3/5 actions remaining]
   ► Soult, move to Dresden
   → Soult moves from Vienna to Dresden (275 lost to march)
   [2/5 actions remaining]
   ► Napoleon, move to Dresden
   → Napoleon moves from Vienna to Dresden (87 lost to march)
   [1/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Ardennes(1486,378)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Soult(2349,248)  Massena(2377,214)  Napoleon(2404,180)  Ney(2276,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2470,539)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(2407,2)  ?(1079,763)  Paget(1079,729)  Lannes(1995,618)  ?(811,816)  Castanos(811,782)  Bernadotte(1525,411)  Murat(1644,505)  Dumonceau(1660,203)  ?(2673,261)  10k(2376,360)  3k(2090,538)  10k(2470,651)  ?(2798,413)  ?(2126,239)  ?(2407,111)  10k(1994,730)  25k(1294,516)  12k(1193,417)  ?(1691,692)  2k(1710,145)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0169  type Davout, unfortify  ->  ok
  (typed and Enter)
view: <run>\frames\0169_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, unfortify
   Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
map: unchanged (120 labels)
```

```
#0170  type Davout, move to Dresden  ->  ok
  (typed and Enter)
view: <run>\frames\0170_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Vienna to Dresden (227 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/5
   Admin:
   2/2
   Gold:
   4,119
   Inf:
   86,000
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, move to Dresden
   → Davout moves from Vienna to Dresden (227 lost to march)
   [0/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Ardennes(1486,378)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout +3(2377,224)  Ney(2276,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(2407,2)  ?(1079,763)  Paget(1079,729)  Lannes(1995,618)  ?(811,816)  Castanos(811,782)  Bernadotte(1525,411)  Murat(1644,505)  Dumonceau(1660,203)  ?(2673,261)  10k(2376,360)  3k(2090,538)  10k(2470,651)  ?(2798,413)  ?(2126,239)  ?(2407,111)  10k(1994,730)  25k(1294,516)  12k(1193,417)  ?(1691,692)  2k(1710,145)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0171  type recruit infantry for Bernadotte  ->  ok
  (typed and Enter)
view: <run>\frames\0171_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte recruits 3,000 infantry at Orleanais (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 30% -> 31%
Infantry pool: 86,000 -> 83,000 [WARNING] Morale dropped to 31% — consider drilling before battle.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/5
   Admin:
   1/2
   Gold:
   3,919
   Inf:
   83,000
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Orleanais (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 30% -> 31%
   Infantry pool: 86,000 -> 83,000 [WARNING] Morale dropped to 31% — consider drilling before battle.
   [0/5 actions remaining]
map: unchanged (118 labels)
```

```
#0172  type recruit infantry for Bernadotte  ->  ok
  (typed and Enter)
view: <run>\frames\0172_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte recruits 3,000 infantry at Orleanais (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 31% -> 32%
Infantry pool: 83,000 -> 80,000 [WARNING] Morale dropped to 32% — consider drilling before battle. That was the last order the day could take, Sire — the turn ends when you say so.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   0/5
   Admin:
   0/2
   Gold:
   3,719
   Inf:
   80,000
   Cav:
   29,000
   Art:
   14,800
   [recruit infantry for Bernadotte]  (Tab)
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E) ▸]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Orleanais (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 31% -> 32%
   Infantry pool: 83,000 -> 80,000 [WARNING] Morale dropped to 32% — consider drilling before battle. That was the last order the day could take, Sire — the turn ends when you say so.
   [0/5 actions remaining]
map: unchanged (118 labels)
```

```
#0173  click End Turn  ->  ok
  (clicked at (929, 978))
view: <run>\frames\0173_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 9
   RUSSIA / ──────────────────────────── / - Buxhowden holds position /  / PRUSSIA / ──────────────────────────── / - Hohenlohe fortifies position /  / BAVARIA / ──────────────────────────── / - Deroy holds position /  / ──────────────────────────── / Britain, Austria, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 45 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,806
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   → Napoleon moves from Vienna to Dresden (87 lost to march)
   [1/5 actions remaining]
   ► Davout, unfortify
   Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
   ► Davout, move to Dresden
   → Davout moves from Vienna to Dresden (227 lost to march)
   [0/5 actions remaining]
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Orleanais (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 30% -> 31%
   Infantry pool: 86,000 -> 83,000 [WARNING] Morale dropped to 31% — consider drilling before battle.
   [0/5 actions remaining]
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Orleanais (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 31% -> 32%
   Infantry pool: 83,000 -> 80,000 [WARNING] Morale dropped to 32% — consider drilling before battle. That was the last order the day could take, Sire — the turn ends when you say so.
   [0/5 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 10 BEGINS
   ═══════════════════════════════════════
   Income: 3047g | Occupation: -50g | Charges of Empire: -29g | Laws: -300g | Infrastructure: -20g | Other: +1383g | Upkeep: -944g | Net: +3087g | Spent: 400g
   Treasury: 6,806g
   Actions refreshed: 5/5
   DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 10).
   Supply shortage at Dresden: Davout loses 672 troops
   Supply shortage at Dresden: Soult loses 778 troops
   Supply shortage at Dresden: Massena loses 786 troops
   Supply shortage at Dresden: Napoleon loses 259 troops
   Supply shortage at Moravia: Kutuzov loses 798 troops
   Supply shortage at Moravia: Buxhowden loses 785 troops
   Supply shortage at Moravia: Bennigsen loses 128 troops
   Supply shortage at Burgundy: Bernadotte loses 3 troops
   Garrison at Vienna reinforced: 10,000 -> 12,000
   Garrison at Hanover reinforced: 2,000 -> 4,000
   Holland loyalty 91 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   Territorial rivalry between Britain and Portugal grows.
   Territorial rivalry between Russia and Sweden grows.
   Peace concluded between Hanover and Prussia without France. Hanover pays 1,899 gold. Prussia is now free to look elsewhere.
   Soult's resentment of Massena is set aside. He holds you to your word.
   Berthier reports that Soult appears envious of Ney's laurels — he has grown scrupulous to the point of reproach. He asked for an audience on turn 8, and will not ask again before turn 14.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout +3(2377,224)  Ney(2276,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Hohenlohe(2407,0)  Lannes(1995,618)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Bernadotte(1499,526)  3k(2673,261)  10k(2376,360)  3k(2090,538)  12k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  10k(1994,730)  25k(1294,516)  12k(1193,417)  ?(1691,692)  4k(1710,145)  ?(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0174  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0174_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,806
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Archduke John — Carniola — small force [partial]
   Castanos — Bordelais — small force [partial]
   TURN EVENTS
   DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 10).
   Supply cost you 2,498 men, at Dresden and Burgundy.
   Garrison at Vienna reinforced: 10,000 -> 12,000
   Holland loyalty 91 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Soult's resentment of Massena is set aside. He holds you to your word.
   Berthier reports that Soult appears envious of Ney's laurels — he has grown scrupulous to the point of reproach. He asked for an audience on turn 8, and will not ask again before turn 14.
   DIPLOMATIC EVENTS
   The coalition against France has dissolved.
   Settlement of France vs Britain: settlement ratified.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Holland has arrived with a petition.
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 1,899 gold. Prussia is now free to look elsewhere.
   THE CONTINENTAL SYSTEM loosens: 0% of the Continent's ports are closed to Britain.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   The court of Prussia takes up a new design: Armed Neutrality.
   The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
   The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
   And Sardinia stirs at its own design.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Holland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 28 and declare on turn 31: Austria, Prussia and 5 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
map: unchanged (114 labels)
```

```
#0175  click Envoys  ->  ok
  (clicked at (3378, 18))
view: <run>\frames\0175_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Schimmelpenninck (Loyalist) of Holland /  / The petition: /   - Grant it, and Holland's tribute of 337g a turn is remitted for 8 collections (2696g forgone): loyalty +9 (to the 100 ceiling), its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and Holland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loya …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,806
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 28 and declare on turn 31: Austria, Prussia and 5 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
map: unchanged (114 labels)
```

```
#0176  click Refuse  ->  ok
  (clicked at (1829, 687))
view: <run>\frames\0176_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 45 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: Settlement Ratified (x2) @(3435,64)]  [icon: Prussia Declares War! @(3477,64)]  [icon: Treasury in deficit @(3519,64)]  [icon: Client's Petition Rejected @(3561,64)]  [+20]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   controls: [Russia  2t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,806
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (91 → 81); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (114 labels)
```

```
#0177  click ⚖ Diplomacy  ->  ok
  (clicked at (829, 978))
view: <run>\frames\0177_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   Treaties (10)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Russia  —  Armistice  |  -71 (Hostile)]  [Prussia  —  Open Borders  |  -22 (Wary)]  [Spain  —  Alliance  |  +31 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -11 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (91 → 81); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (114 labels)
```

```
#0178  click Prussia  ->  ok
  (clicked at (1825, 561))
view: <run>\frames\0178_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY — Prussia
   DP: 7
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Open Borders   Relation: -22 (Wary) /  / "Our borders with Prussia are open, but trust remains shallow. A non-aggression pact would formalize the thaw." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. /  / KEY FACTORS /   + Base willingness (+10) /   + Diplomatic skil …
   Relations with Prussia stand at -22; a Non-Aggression needs 0.
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Non-Aggression (1 DP)  —  Unlikely](disabled: Relations with Prussia stand at -22; a Non-Aggression needs 0.)  [Propose Vassal (3 DP)  —  Hopeless]  [Declare War (1 DP)]  [Break Treaty (1 DP)]  [Downgrade (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (91 → 81); bond 0 → -20 (-1 a turn). Nothing is charged.
map: unchanged (114 labels)
```

```
#0179  click Declare War  ->  ok
  (clicked at (1825, 570))
view: <run>\frames\0179_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   WAR PURPOSE - Prussia /  / Choose your war purpose against Prussia. /  / Conquest /   Seize Berlin. +2/turn while held. /   Ticking score: +2/turn /  / Forced Alliance /   Force Prussia into alliance. +2/turn while Berlin held. /   Ticking score: +2/turn /  / Subjugation /   Total defeat — vassalize Prussia. +3/turn while Berlin held. /   Ticking score: +3/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Conquest]  [Forced Alliance]  [Subjugation]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 45 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,806
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► declare war on Prussia
map: unchanged (114 labels)
```

```
#0180  click Conquest  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0180_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   WAR DECLARATION — Prussia /  / Sire, we have an Open Borders Agreement with Prussia. Setting a treaty aside is a matter of arithmetic, not of honour; permit me only to observe that Europe keeps the longer memory, and will price our next undertaking accordingly. Shall I proceed regardless? /  / Political Context: /   • Reliability would fall from 0 to -10. /   • Likely co-belligerents: Spain, Bavar …
   controls: [icon: Close (Esc) @(2151,292)]  [Proceed — break the treaty]  [Reconsider]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand…
map: unchanged (114 labels)
```

```
#0181  click Proceed  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0181_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['talleyrand_objection'], region_panel=no
── TalleyrandObjectionPopup (layer 113) ──
   TALLEYRAND OBJECTS / STRONG /  / "Sire, Europe's alarm stands at 45 — low enough that no league stands against us. A declaration on Prussia would carry it to 65, past the 60 at which a coalition gathers. The courts are still recovering from the last league — 4 turns yet — but if the alarm still stands at 60 when they have, one gathers, and Austria, Ottoman Empire, Sweden and 7 other courts would j …
   controls: [Proceed Anyway]  [Modify Proposal]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: force declare war
map: unchanged (114 labels)
```

```
#0182  click Proceed Anyway  ->  ok
  (clicked at (1684, 647))
view: <run>\frames\0182_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Prussia /  / Terms Talleyrand proposes: /   • Spain can find no road to Prussia — no shared border, and no friendly passage within reach — so its armies could never come to grips. /   • Bavaria will join against Prussia without additional terms. /  /  / Political Context: /   • Spain can find no road to Prussia — no shared border, and no friendly passage within reach — so its …
   controls: [Accept Ally Entry]  [Proceed Without Allies]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Overriding Talleyrand's objection...
map: unchanged (114 labels)
```

```
#0183  click Accept Ally Entry  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0183_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 65 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: Bavaria Joins Offensive! @(3435,64)]  [icon: War with Prussia! @(3477,64)]  [icon: Settlement Ratified (x2) @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+22]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia
   0
   T:0
   controls: [Prussia]  [Russia  2t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,806
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: ally entry accept all
   France declares war on Prussia, shattering the Open Borders Agreement! Bavaria enters the war against Prussia, honoring alliance with France! Holland follows France into the war against Prussia! Kingdom of Italy follows France into the war against Prussia! Switzerland follows France into the war against Prussia!
map: unchanged (114 labels)
```

```
#0184  type Soult, attack Silesia  ->  ok
  (typed and Enter)
view: <run>\frames\0184_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok ASSAULT — Soult storms the works at Silesia alone: 19,190 men, 28,705 in the assault's reckoning (+18% from the corps at his side), against a garrison of 3,000. Davout, Massena and Napoleon do not join an assault on the works; a detachment fights to the last man.
Soult assaults the Silesia garrison! Garrison: 3,000 -> 1,500 (-1,500). Soult loses 501 troops. Garrison holds — 1,500 defenders remain.
[Materiel] Guns, horses and stores lost with the fallen: France -25g, Prussia -75g.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia
   -3
   T:0
   controls: [Prussia]  [Russia  2t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/5
   Admin:
   2/2
   Gold:
   6,781
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, attack Silesia
   ASSAULT — Soult storms the works at Silesia alone: 19,190 men, 28,705 in the assault's reckoning (+18% from the corps at his side), against a garrison of 3,000. Davout, Massena and Napoleon do not join an assault on the works; a detachment fights to the last man.
   Soult assaults the Silesia garrison! Garrison: 3,000 -> 1,500 (-1,500). Soult loses 501 troops. Garrison holds — 1,500 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -25g, Prussia -75g.
   [4/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout +3(2377,224)  Ney(2276,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Hohenlohe(2407,0)  Lannes(1995,618)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Bernadotte(1499,526)  1k(2673,261)  10k(2376,360)  3k(2090,538)  12k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  10k(1994,730)  25k(1294,516)  12k(1193,417)  ?(1691,692)  4k(1710,145)  ?(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0185  type Soult, attack Silesia again  ->  ok
  (typed and Enter)
view: <run>\frames\0185_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok ASSAULT — Soult storms the works at Silesia alone: 18,689 men, 25,160 in the assault's reckoning (+18% from the corps at his side), against a garrison of 1,500. Davout, Massena and Napoleon do not join an assault on the works; a detachment fights to the last man.
Soult assaults the Silesia garrison! Garrison: 1,500 -> 750 (-750). Soult loses 278 troops. Garrison holds — 750 defenders remain.
[Materiel] Guns, horses and stores lost with the fallen: France -13g, Prussia -37g.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia
   -6
   T:0
   controls: [Prussia]  [Russia  2t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   6,768
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   The court of Prussia takes up a new design: Armed Neutrality.
   The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
   The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
   And Sardinia stirs at its own design.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Holland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 28 and declare on turn 31: Austria, Prussia and 5 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (91 → 81); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► declare war on Prussia
   Directing Talleyrand…
   Directing Talleyrand: force declare war
   Overriding Talleyrand's objection...
   Directing Talleyrand: ally entry accept all
   France declares war on Prussia, shattering the Open Borders Agreement! Bavaria enters the war against Prussia, honoring alliance with France! Holland follows France into the war against Prussia! Kingdom of Italy follows France into the war against Prussia! Switzerland follows France into the war against Prussia!
   ► Soult, attack Silesia
   ASSAULT — Soult storms the works at Silesia alone: 19,190 men, 28,705 in the assault's reckoning (+18% from the corps at his side), against a garrison of 3,000. Davout, Massena and Napoleon do not join an assault on the works; a detachment fights to the last man.
   Soult assaults the Silesia garrison! Garrison: 3,000 -> 1,500 (-1,500). Soult loses 501 troops. Garrison holds — 1,500 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -25g, Prussia -75g.
   [4/5 actions remaining]
   ► Soult, attack Silesia again
   ASSAULT — Soult storms the works at Silesia alone: 18,689 men, 25,160 in the assault's reckoning (+18% from the corps at his side), against a garrison of 1,500. Davout, Massena and Napoleon do not join an assault on the works; a detachment fights to the last man.
   Soult assaults the Silesia garrison! Garrison: 1,500 -> 750 (-750). Soult loses 278 troops. Garrison holds — 750 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -13g, Prussia -37g.
   [3/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout +3(2377,224)  Ney(2276,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Hohenlohe(2407,0)  Lannes(1995,618)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Bernadotte(1499,526)  750(2673,261)  10k(2376,360)  3k(2090,538)  12k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  10k(1994,730)  25k(1294,516)  12k(1193,417)  ?(1691,692)  4k(1710,145)  ?(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0186  type Massena, attack Silesia  ->  ok
  (typed and Enter)
view: <run>\frames\0186_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok ASSAULT — Massena storms the works at Silesia alone: 19,370 men, 27,382 in the assault's reckoning (+12% from the corps at his side), against a garrison of 750. Davout, Soult and Napoleon do not join an assault on the works; a detachment fights to the last man.
Massena assaults the Silesia garrison! Garrison: 750 -> 375 (-375). Massena loses 132 troops. Garrison holds — 375 defenders remain.
[Materiel] Guns, horses and stores lost with the fallen: France -6g, Prussia -18g.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   6,762
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, attack Silesia
   ASSAULT — Massena storms the works at Silesia alone: 19,370 men, 27,382 in the assault's reckoning (+12% from the corps at his side), against a garrison of 750. Davout, Soult and Napoleon do not join an assault on the works; a detachment fights to the last man.
   Massena assaults the Silesia garrison! Garrison: 750 -> 375 (-375). Massena loses 132 troops. Garrison holds — 375 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -6g, Prussia -18g.
   [2/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout +3(2377,224)  Ney(2276,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Hohenlohe(2407,0)  Lannes(1995,618)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Bernadotte(1499,526)  375(2673,261)  10k(2376,360)  3k(2090,538)  12k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  10k(1994,730)  25k(1294,516)  12k(1193,417)  ?(1691,692)  4k(1710,145)  ?(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0187  type Davout, attack Silesia  ->  ok
  (typed and Enter)
view: <run>\frames\0187_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['objection'], region_panel=no
reply: ok Davout respectfully raises concerns: 'Sire, the enemy is too strong. We need reinforcements.' (Trust him and he will fortify current position instead.)
── ObjectionDialog (layer 108) ──
   DAVOUT'S ADVICE
   "Davout respectfully raises concerns: 'Sire, the enemy is too strong. We need reinforcements.' (Trust him and he will fortify current position instead.)"
   Personality: Cautious
   Trust: 82 (Loyal)
   Track record: Neutral
   Authority: 80
   controls: [Trust Davout: fortify current position (+3 trust)]  [Proceed as Ordered (-5 trust)]  [Compromise: defend at Dresden (+3 trust)]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 65 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   6,762
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Davout, attack Silesia
   ⚠ Marshal Davout raises concerns...
map: unchanged (114 labels)
```

```
#0188  click Proceed as Ordered  ->  ok
  (clicked at (1844, 618))
view: <run>\frames\0188_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Davout has taken Silesia
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+800 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   1/5
   Admin:
   2/2
   Gold:
   6,762
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► You insist the order be carried out as given.
   ⚑ You insist on the original order. Davout complies reluctantly.
   Davout's hand trembled on the hilt, but discipline held... barely. (Trust -8 in all — -5 for the order pressed home, -3 more for the manner of his obedience.)
   Davout follows your orders.
   The detachment of 375 at Silesia lays down its arms. Davout marches from Dresden into Silesia unopposed! (165 lost to march) Captured: Prussia → France
   Your forces have taken Silesia. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [1/5 actions remaining]
   Your forces await orders: Plunder or Secure?
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  Soult(2349,248)  Massena(2377,214)  Napoleon(2404,180)  Ney(2276,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Hohenlohe(2407,0)  Lannes(1995,618)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Bernadotte(1499,526)  10k(2376,360)  3k(2090,538)  12k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  10k(1994,730)  25k(1294,516)  12k(1193,417)  ?(1691,692)  4k(1710,145)  ?(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0189  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0189_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 67 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: Bavaria Joins Offensive! @(3435,64)]  [icon: War with Prussia! @(3477,64)]  [icon: Settlement Ratified (x2) @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+22]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia
   +1
   T:0
   controls: [Prussia]  [Russia  2t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   1/5
   Admin:
   2/2
   Gold:
   6,762
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 28 and declare on turn 31: Austria, Prussia and 5 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   Responding to Holland's proposal: declined
   Holland's petition for relief is refused: loyalty −10 (91 → 81); bond 0 → -20 (-1 a turn). Nothing is charged.
   ► declare war on Prussia
   Directing Talleyrand…
   Directing Talleyrand: force declare war
   Overriding Talleyrand's objection...
   Directing Talleyrand: ally entry accept all
   France declares war on Prussia, shattering the Open Borders Agreement! Bavaria enters the war against Prussia, honoring alliance with France! Holland follows France into the war against Prussia! Kingdom of Italy follows France into the war against Prussia! Switzerland follows France into the war against Prussia!
   ► Soult, attack Silesia
   ASSAULT — Soult storms the works at Silesia alone: 19,190 men, 28,705 in the assault's reckoning (+18% from the corps at his side), against a garrison of 3,000. Davout, Massena and Napoleon do not join an assault on the works; a detachment fights to the last man.
   Soult assaults the Silesia garrison! Garrison: 3,000 -> 1,500 (-1,500). Soult loses 501 troops. Garrison holds — 1,500 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -25g, Prussia -75g.
   [4/5 actions remaining]
   ► Soult, attack Silesia again
   ASSAULT — Soult storms the works at Silesia alone: 18,689 men, 25,160 in the assault's reckoning (+18% from the corps at his side), against a garrison of 1,500. Davout, Massena and Napoleon do not join an assault on the works; a detachment fights to the last man.
   Soult assaults the Silesia garrison! Garrison: 1,500 -> 750 (-750). Soult loses 278 troops. Garrison holds — 750 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -13g, Prussia -37g.
   [3/5 actions remaining]
   ► Massena, attack Silesia
   ASSAULT — Massena storms the works at Silesia alone: 19,370 men, 27,382 in the assault's reckoning (+12% from the corps at his side), against a garrison of 750. Davout, Soult and Napoleon do not join an assault on the works; a detachment fights to the last man.
   Massena assaults the Silesia garrison! Garrison: 750 -> 375 (-375). Massena loses 132 troops. Garrison holds — 375 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -6g, Prussia -18g.
   [2/5 actions remaining]
   ► Davout, attack Silesia
   ⚠ Marshal Davout raises concerns...
   ► You insist the order be carried out as given.
   ⚑ You insist on the original order. Davout complies reluctantly.
   Davout's hand trembled on the hilt, but discipline held... barely. (Trust -8 in all — -5 for the order pressed home, -3 more for the manner of his obedience.)
   Davout follows your orders.
   The detachment of 375 at Silesia lays down its arms. Davout marches from Dresden into Silesia unopposed! (165 lost to march) Captured: Prussia → France
   Your forces have taken Silesia. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [1/5 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Davout secures Silesia. Stability set to 25. Order is maintained. 1 building damaged.
map: unchanged (115 labels)
```

```
#0190  type Lannes, move to Franconia  ->  ok
  (typed and Enter)
view: <run>\frames\0190_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Lannes moves from Munich to Franconia (130 lost to march, 261 to enemy harassment)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   0/5
   Admin:
   2/2
   Gold:
   6,762
   Inf:
   82,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, move to Franconia
   → Lannes moves from Munich to Franconia (130 lost to march, 261 to enemy harassment)
   [0/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  Soult(2349,248)  Massena(2377,214)  Napoleon(2404,180)  Ney(2276,485)  Lannes(2062,426)  Deroy(2118,392)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Hohenlohe(2407,0)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Bernadotte(1499,526)  10k(2376,360)  3k(2090,538)  12k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  4k(1710,145)  ?(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0191  type recruit infantry for Bernadotte  ->  ok
  (typed and Enter)
view: <run>\frames\0191_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte recruits 3,000 infantry at Burgundy (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
Infantry pool: 82,500 -> 79,500 [WARNING] Morale dropped to 32% — consider drilling before battle.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   0/5
   Admin:
   1/2
   Gold:
   6,162
   Inf:
   79,500
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Burgundy (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
   Infantry pool: 82,500 -> 79,500 [WARNING] Morale dropped to 32% — consider drilling before battle.
   [0/5 actions remaining]
map: unchanged (117 labels)
```

```
#0192  type recruit cavalry for Murat  ->  ok
  (typed and Enter)
view: <run>\frames\0192_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat recruits 3,000 cavalry at Nivernais (field levy — no depot; capped at 3,000) - Cost: 1035 gold (×3 at war) (Murat's intendance: +15%). Morale: 80% -> 73%
Cavalry pool: 30,000 -> 27,000 That was the last order the day could take, Sire — the turn ends when you say so.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   0/5
   Admin:
   0/2
   Gold:
   5,127
   Inf:
   79,500
   Cav:
   27,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E) ▸]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit cavalry for Murat
   + Murat recruits 3,000 cavalry at Nivernais (field levy — no depot; capped at 3,000) - Cost: 1035 gold (×3 at war) (Murat's intendance: +15%). Morale: 80% -> 73%
   Cavalry pool: 30,000 -> 27,000 That was the last order the day could take, Sire — the turn ends when you say so.
   [0/5 actions remaining]
map: unchanged (117 labels)
```

```
#0193  click End Turn  ->  ok
  (clicked at (929, 978))
view: <run>\frames\0193_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 10
   RUSSIA / ──────────────────────────── / - Buxhowden holds position /  / PRUSSIA / ──────────────────────────── / - Brunswick moves to Oldenburg / - Brunswick moves to Hanover / - Brunswick moves to Brunswick / - Brunswick moves to Berlin / - Brunswick recruits troops /  / ──────────────────────────── / Britain, Austria, Spain and 5 other courts stirred as well, but their formations remain beyond o …
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 66 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   7,239
   Inf:
   81,900
   Cav:
   28,750
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ⚑ You insist on the original order. Davout complies reluctantly.
   Davout's hand trembled on the hilt, but discipline held... barely. (Trust -8 in all — -5 for the order pressed home, -3 more for the manner of his obedience.)
   Davout follows your orders.
   The detachment of 375 at Silesia lays down its arms. Davout marches from Dresden into Silesia unopposed! (165 lost to march) Captured: Prussia → France
   Your forces have taken Silesia. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [1/5 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Davout secures Silesia. Stability set to 25. Order is maintained. 1 building damaged.
   ► Lannes, move to Franconia
   → Lannes moves from Munich to Franconia (130 lost to march, 261 to enemy harassment)
   [0/5 actions remaining]
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Burgundy (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
   Infantry pool: 82,500 -> 79,500 [WARNING] Morale dropped to 32% — consider drilling before battle.
   [0/5 actions remaining]
   ► recruit cavalry for Murat
   + Murat recruits 3,000 cavalry at Nivernais (field levy — no depot; capped at 3,000) - Cost: 1035 gold (×3 at war) (Murat's intendance: +15%). Morale: 80% -> 73%
   Cavalry pool: 30,000 -> 27,000 That was the last order the day could take, Sire — the turn ends when you say so.
   [0/5 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 11 BEGINS
   ═══════════════════════════════════════
   Income: 3094g | Occupation: -120g | Charges of Empire: -222g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Other: +1386g | Upkeep: -1616g | Net: +2112g | Spent: 1635g
   Treasury: 7,239g
   Actions refreshed: 5/5
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Dresden: Soult loses 396 troops
   Supply shortage at Dresden: Massena loses 413 troops
   Supply shortage at Dresden: Napoleon loses 137 troops
   Supply shortage at Moravia: Kutuzov loses 758 troops
   Supply shortage at Moravia: Buxhowden loses 745 troops
   Supply shortage at Moravia: Bennigsen loses 122 troops
   Garrison at Vienna reinforced: 12,000 -> 14,000
   Holland loyalty 73 (-8): the lord's defeats, satellite drift
   Kingdom of Italy loyalty 93 (-6): the lord's defeats, satellite drift
   Switzerland loyalty 86 (-6): the lord's defeats, satellite drift
   Switzerland sends 3,500 men under Amey to the colours at Bern — they await the orders of France. The nearest host is Murat at Nivernais. Switzerland pays them; their dead will be its grief.
   Berthier reports that Ney appears envious of Murat's laurels — he has grown restless for glory.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  Soult(2349,248)  Massena(2377,214)  Napoleon(2404,180)  Ney(2276,485)  Lannes(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Brunswick(2098,127)  Yorck(2154,93)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Hohenlohe(2407,0)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1305,564)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Amey(1691,580)  10k(2376,360)  3k(2090,538)  14k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1710,145)  ?(1660,304)  12k(1571,330)
```

```
#0194  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0194_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   7,239
   Inf:
   81,900
   Cav:
   28,750
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Brunswick — Berlin — 46,465 [confirmed]
   Yorck — Berlin — 5,000 [confirmed]
   Kutuzov — Moravia — 27,000 [confirmed]
   Buxhowden — Moravia — 26,547 [confirmed]
   Bennigsen — Moravia — 4,357 [confirmed]
   Hohenlohe — Posen — 25,000 [confirmed]
   Archduke Charles — Carniola — substantial force [partial]
   Archduke John — Carniola — small force [partial]
   Deroy — Swabia — substantial force [partial]
   Castanos — Bordelais — small force [partial]
   Berlin garrison — Berlin — garrison of 25,000 [confirmed]
   Posen garrison — Posen — garrison of 3,000 [confirmed]
   Hanover garrison — Hanover — garrison — small force [stale - T8]
   TURN EVENTS
   Supply cost you 946 men, at Dresden.
   Garrison at Vienna reinforced: 12,000 -> 14,000
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Berthier reports that Ney appears envious of Murat's laurels — he has grown restless for glory.
   DIPLOMATIC EVENTS
   Bavaria has joined France's war against Prussia, honoring their alliance.
   France has declared war on Prussia, shattering the Open Borders Agreement, with 2 allied courts poised to follow.
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   Intelligence reports Prussia has raised Yorck to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Switzerland sends 3,500 men under Amey to the colours at Bern — they await the orders of France. The nearest host is Murat at Nivernais. Switzerland pays them; their dead will be its grief.
   The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
   The court of Britain hardens over The Low Countries — prepared now to go as far as an ultimatum.
   And Sardinia stirs at its own design.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled (1 held, unsettled: Silesia) · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 66/100 [Brewing]
   Europe has watched us 5 quiet turns. At this pace the courts consult on turn 14 and declare on turn 17: Austria and 9 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The Presence is read at every table in Europe, Sire. A victory with him at its head restores more than a province; a defeat under him costs more than one."
   ════════════════════════════════════
map: unchanged (119 labels)
```

```
#0195  type where is Hohenlohe  ->  ok
  (typed and Enter)
view: <run>\frames\0195_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Hohenlohe of Prussia is at Posen — 25,000 men, confirmed.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 66 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: Bavaria Joins Offensive! @(3435,64)]  [icon: War with Prussia! @(3477,64)]  [icon: Settlement Ratified (x2) @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+22]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia
   0
   T:1
   controls: [Prussia]  [Russia  1t]
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Kutuzov — Moravia — 27,000 [confirmed]
   Buxhowden — Moravia — 26,547 [confirmed]
   Bennigsen — Moravia — 4,357 [confirmed]
   Hohenlohe — Posen — 25,000 [confirmed]
   Archduke Charles — Carniola — substantial force [partial]
   Archduke John — Carniola — small force [partial]
   Deroy — Swabia — substantial force [partial]
   Castanos — Bordelais — small force [partial]
   Berlin garrison — Berlin — garrison of 25,000 [confirmed]
   Posen garrison — Posen — garrison of 3,000 [confirmed]
   Hanover garrison — Hanover — garrison — small force [stale - T8]
   TURN EVENTS
   Supply cost you 946 men, at Dresden.
   Garrison at Vienna reinforced: 12,000 -> 14,000
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Berthier reports that Ney appears envious of Murat's laurels — he has grown restless for glory.
   DIPLOMATIC EVENTS
   Bavaria has joined France's war against Prussia, honoring their alliance.
   France has declared war on Prussia, shattering the Open Borders Agreement, with 2 allied courts poised to follow.
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   Intelligence reports Prussia has raised Yorck to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Switzerland sends 3,500 men under Amey to the colours at Bern — they await the orders of France. The nearest host is Murat at Nivernais. Switzerland pays them; their dead will be its grief.
   The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
   The court of Britain hardens over The Low Countries — prepared now to go as far as an ultimatum.
   And Sardinia stirs at its own design.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled (1 held, unsettled: Silesia) · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 66/100 [Brewing]
   Europe has watched us 5 quiet turns. At this pace the courts consult on turn 14 and declare on turn 17: Austria and 9 lesser courts would march. Bound for now by a fresh peace: Britain. Held by our truce: Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The Presence is read at every table in Europe, Sire. A victory with him at its head restores more than a province; a defeat under him costs more than one."
   ════════════════════════════════════
   ► where is Hohenlohe
   Hohenlohe of Prussia is at Posen — 25,000 men, confirmed.
map: unchanged (119 labels)
```

```
#0196  type Massena, attack Hohenlohe at Posen  ->  ok
  (typed and Enter)
view: <run>\frames\0196_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Massena (18,825; expect about 36,561 with the corps likely to arrive, up to 37,129 if all march) vs Hohenlohe (25,000 men) at Posen — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Massena' and he will march
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  The Emperor commands in person — though his star dims — every corps on this field fights +9% harder, if he marches.
  The band weighs more than the men: Hohenlohe stands +34% on the defense (his stance, his character and his works).
  Posen feeds 32,000 — the whole muster standing there would lose ~1,014 men a turn to short supply. Living off the land: this poor country feeds our army 80% of what it would otherwise draw.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.


[Combat] Massena leads the charge! (Aggressive: +15% attack)
[Shield] Hohenlohe's DEFENSIVE stance strengthens the line! (+15% defense)
[Shield] Hohenlohe's methodical defense is exemplary! (Cautious: +20% total)
[Fort] Hohenlohe's fortified position provides +11% defense!
[Combat] Adjacent allies bolster Massena's att
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   PRUSSIA LOSSES
   0
   0
   Napoleon
   6,263 → 5,819
   Davout
   16,410 → 15,247
   ⚔
   Massena ◆
   Hohenlohe ◆
   18,825 → 16,600
   25,000 → 21,340
   marched to the guns
   marched to the guns
   Soult — awaits explicit orders
   He resents Ney's glory.
   BATTLE OF POSEN
   click anywhere to skip ▸
   POSEN · TURN 11
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/5
   Admin:
   2/2
   Gold:
   7,048
   Inf:
   81,900
   Cav:
   28,750
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Massena' and he will march
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   The Emperor commands in person — though his star dims — every corps on this field fights +9% harder, if he marches.
   The band weighs more than the men: Hohenlohe stands +34% on the defense (his stance, his character and his works).
   Posen feeds 32,000 — the whole muster standing there would lose ~1,014 men a turn to short supply. Living off the land: this poor country feeds our army 80% of what it would otherwise draw.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Shield] Hohenlohe's DEFENSIVE stance strengthens the line! (+15% defense)
   [Shield] Hohenlohe's methodical defense is exemplary! (Cautious: +20% total)
   [Fort] Hohenlohe's fortified position provides +11% defense!
   [Combat] Adjacent allies bolster Massena's attack! (+2%)
   Massena struggles in a costly engagement. Brutal stalemate between Massena and Hohenlohe. Heavy casualties on both sides: Massena's army 3,832, Hohenlohe 3,660.
   [Materiel] Guns, horses and stores lost with the fallen: France -191g, Prussia -183g.
   Davout withdraws to Silesia after the battle.
   Napoleon withdraws to Dresden after the battle.
   ⚔ View the field
   [4/5 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 18,825 (lead) + 18,304 committed (Davout, Napoleon) = 37,129.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 1,607 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "Blood on both sides and no verdict — I despise an unfinished page."
   Berthier: the corps marched apart and arrived together.
   Attack: Massena (Personality (aggressive) +15%, The Emperor commands in person (his star dims) +9%)
   Defense: Hohenlohe (Defensive stance +15%, Fortified position +11%, Personality (cautious) +5%)
   Casualties: Massena's own corps 2,225 | Hohenlohe 3,660
   Strength: Massena 18,825 → 16,600 | Hohenlohe 25,000 → 21,340
   Berthier: "Davout and Napoleon arrived to reinforce Massena, but Soult failed to reach the field in time."
map: unchanged (119 labels)
```

```
#0197  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Massena ◆' (Control, layer 121))
view: <run>\frames\0197_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A BLOODY STALEMATE
   FRANCE LOSSES
   PRUSSIA LOSSES
   3,832
   3,660
   Napoleon
   6,263 → 5,819
   Davout
   16,410 → 15,247
   ⚔
   Massena ◆
   Hohenlohe ◆
   18,825 → 16,600
   25,000 → 21,340
   marched to the guns
   marched to the guns
   Soult — awaits explicit orders
   He resents Ney's glory.
   Berthier: “The Emperor watched this field. Davout and Napoleon arrived to reinforce Massena, but Soult failed to reach the field in time.” / Hohenlohe: "You gained nothing. I call that a victory of arithmetic."
   BATTLE OF POSEN
   POSEN · TURN 11
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Hohenlohe (Defensive stance +15%, Fortified position +11%, Personality (cautious) +5%)
   Casualties: Massena's own corps 2,225 | Hohenlohe 3,660
   Strength: Massena 18,825 → 16,600 | Hohenlohe 25,000 → 21,340
   Berthier: "Davout and Napoleon arrived to reinforce Massena, but Soult failed to reach the field in time."
map: unchanged (119 labels)
```

```
#0198  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0198_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Hohenlohe (Defensive stance +15%, Fortified position +11%, Personality (cautious) +5%)
   Casualties: Massena's own corps 2,225 | Hohenlohe 3,660
   Strength: Massena 18,825 → 16,600 | Hohenlohe 25,000 → 21,340
   Berthier: "Davout and Napoleon arrived to reinforce Massena, but Soult failed to reach the field in time."
map: unchanged (119 labels)
```

```
#0199  type Soult, move to Brandenburg  ->  ok
  (typed and Enter)
view: <run>\frames\0199_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok Soult moves from Dresden to Brandenburg. Brandenburg falls to France! (was Prussia) (180 lost to march)
Pomerania lies undefended — an attack takes it.
Your forces have taken Brandenburg. Plunder it for 400 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Soult has taken Brandenburg
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+400 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 68 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   7,048
   Inf:
   81,900
   Cav:
   28,750
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Soult, move to Brandenburg
   → Soult moves from Dresden to Brandenburg. Brandenburg falls to France! (was Prussia) (180 lost to march)
   Pomerania lies undefended — an attack takes it.
   Your forces have taken Brandenburg. Plunder it for 400 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [3/5 actions remaining]
   Your forces await orders: Plunder or Secure?
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  Massena(2349,248)  Napoleon(2404,214)  Ney(2276,485)  Lannes(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Brunswick(2098,127)  Yorck(2154,93)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Hohenlohe(2407,0)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1305,564)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Amey(1691,580)  10k(2376,360)  3k(2090,538)  14k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1710,145)  ?(1660,304)  12k(1571,330)
```

```
#0200  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0200_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 68 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: Bavaria Joins Offensive! @(3435,64)]  [icon: War with Prussia! @(3477,64)]  [icon: Settlement Ratified (x2) @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+22]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia
   +7
   T:1
   controls: [Prussia]  [Russia  1t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   7,048
   Inf:
   81,900
   Cav:
   28,750
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   You order your troops to secure the region.
   Soult secures Brandenburg. Stability set to 25. Order is maintained.
map: unchanged (117 labels)
```

```
#0201  type Soult, move to Pomerania  ->  ok
  (typed and Enter)
view: <run>\frames\0201_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok Soult moves from Brandenburg to Pomerania. Pomerania falls to France! (was Prussia) (178 lost to march)
Your forces have taken Pomerania. Plunder it for 400 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Soult has taken Pomerania
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+400 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 70 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   7,048
   Inf:
   81,900
   Cav:
   28,750
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Davout withdraws to Silesia after the battle.
   Napoleon withdraws to Dresden after the battle.
   ⚔ View the field
   [4/5 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Massena!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 18,825 (lead) + 18,304 committed (Davout, Napoleon) = 37,129.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 1,607 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "Blood on both sides and no verdict — I despise an unfinished page."
   Berthier: the corps marched apart and arrived together.
   Attack: Massena (Personality (aggressive) +15%, The Emperor commands in person (his star dims) +9%)
   Defense: Hohenlohe (Defensive stance +15%, Fortified position +11%, Personality (cautious) +5%)
   Casualties: Massena's own corps 2,225 | Hohenlohe 3,660
   Strength: Massena 18,825 → 16,600 | Hohenlohe 25,000 → 21,340
   Berthier: "Davout and Napoleon arrived to reinforce Massena, but Soult failed to reach the field in time."
   ► Soult, move to Brandenburg
   → Soult moves from Dresden to Brandenburg. Brandenburg falls to France! (was Prussia) (180 lost to march)
   Pomerania lies undefended — an attack takes it.
   Your forces have taken Brandenburg. Plunder it for 400 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [3/5 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Soult secures Brandenburg. Stability set to 25. Order is maintained.
   ► Soult, move to Pomerania
   → Soult moves from Brandenburg to Pomerania. Pomerania falls to France! (was Prussia) (178 lost to march)
   Your forces have taken Pomerania. Plunder it for 400 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [2/5 actions remaining]
   Your forces await orders: Plunder or Secure?
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  Massena(2349,248)  Napoleon(2404,214)  Ney(2276,485)  Lannes(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Brunswick(2098,127)  Yorck(2154,93)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Hohenlohe(2407,0)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1305,564)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Armfelt(2066,16)  Amey(1691,580)  10k(2376,360)  3k(2090,538)  14k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1710,145)  ?(1660,304)  12k(1571,330)
```

```
#0202  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0202_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 70 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Ney orders lost @(3351,64)]  [icon: European Courts Concerned @(3393,64)]  [icon: Bavaria Joins Offensive! @(3435,64)]  [icon: War with Prussia! @(3477,64)]  [icon: Settlement Ratified (x2) @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+22]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia
   +14
   T:1
   controls: [Prussia]  [Russia  1t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   7,048
   Inf:
   81,900
   Cav:
   28,750
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   You order your troops to secure the region.
   Soult secures Pomerania. Stability set to 25. Order is maintained.
map: unchanged (117 labels)
```

```
#0203  type Ney, move to Dresden  ->  ok
  (typed and Enter)
view: <run>\frames\0203_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney moves from Bohemia to Dresden (100 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   1/5
   Admin:
   2/2
   Gold:
   7,048
   Inf:
   81,900
   Cav:
   28,750
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, move to Dresden
   → Ney moves from Bohemia to Dresden (100 lost to march)
   [1/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  Ney(2348,248)  Massena(2377,214)  Napoleon(2404,180)  Lannes(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Brunswick(2098,127)  Yorck(2154,93)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Hohenlohe(2407,0)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1305,564)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Armfelt(2066,16)  Amey(1691,580)  10k(2376,360)  3k(2090,538)  14k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1710,145)  ?(1660,304)  12k(1571,330)
```

```
#0204  type Lannes, move to Dresden  ->  ok
  (typed and Enter)
view: <run>\frames\0204_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Lannes moves from Franconia to Dresden (164 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   0/5
   Admin:
   2/2
   Gold:
   7,048
   Inf:
   81,900
   Cav:
   28,750
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Lannes, move to Dresden
   → Lannes moves from Franconia to Dresden (164 lost to march)
   [0/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  Ney +3(2376,224)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Brunswick(2098,127)  Yorck(2154,93)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Hohenlohe(2407,0)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1305,564)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Armfelt(2066,16)  Amey(1691,580)  10k(2376,360)  ?(2090,538)  14k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1710,145)  ?(1660,304)  12k(1571,330)
```

```
#0205  type recruit infantry for Bernadotte  ->  ok
  (typed and Enter)
view: <run>\frames\0205_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte recruits 3,000 infantry at Limousin (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
Infantry pool: 81,900 -> 78,900 [WARNING] Morale dropped to 32% — consider drilling before battle.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   0/5
   Admin:
   1/2
   Gold:
   6,448
   Inf:
   78,900
   Cav:
   28,750
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Limousin (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
   Infantry pool: 81,900 -> 78,900 [WARNING] Morale dropped to 32% — consider drilling before battle.
   [0/5 actions remaining]
map: unchanged (116 labels)
```

```
#0206  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0206_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 11
   RUSSIA / ──────────────────────────── / - Buxhowden holds position /  / PRUSSIA / ──────────────────────────── / - Brunswick attacks Brandenburg /     Region captured: Brandenburg (was France) (secured) / - Hohenlohe abandons fortified position / - Yorck attacks Franconia /     Assault on the garrison of Franconia /       Garrison: 1,500 lost, 1,500 still under arms /       The assault cost them 6 …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 69 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   8,789
   Inf:
   81,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Soult secures Pomerania. Stability set to 25. Order is maintained.
   ► Ney, move to Dresden
   → Ney moves from Bohemia to Dresden (100 lost to march)
   [1/5 actions remaining]
   ► Lannes, move to Dresden
   → Lannes moves from Franconia to Dresden (164 lost to march)
   [0/5 actions remaining]
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Limousin (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
   Infantry pool: 81,900 -> 78,900 [WARNING] Morale dropped to 32% — consider drilling before battle.
   [0/5 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 12 BEGINS
   ═══════════════════════════════════════
   Income: 3099g | Occupation: -170g | Charges of Empire: -335g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Materiel: -298g | Other: +1411g | Upkeep: -956g | Net: +2341g | Spent: 600g
   Treasury: 8,789g
   Actions refreshed: 5/5
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Silesia: Ney loses 224 troops — 5 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Silesia: Davout loses 442 troops — 9 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Silesia: Lannes loses 367 troops — 7 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Silesia: Massena loses 491 troops — 9 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Moravia: Kutuzov loses 721 troops
   Supply shortage at Moravia: Buxhowden loses 709 troops
   Supply shortage at Moravia: Bennigsen loses 116 troops
   Supply shortage at Pomerania: Soult loses 153 troops
   Supply shortage at Pomerania: Brunswick loses 820 troops
   Supply shortage at Stralsund: Armfelt loses 374 troops
   Garrison at Vienna reinforced: 14,000 -> 16,000
   Holland loyalty 70 (-3): satellite drift, the lord's defeats
   The armistice between France and Russia has collapsed. War resumes.
   Berthier reports that Murat resents Ney's laurels again, 9 turns after the last — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier: Enemy forces spotted near Vienna! Kutuzov (26,279 troops) at Moravia.
   Berthier: Enemy forces spotted near Vienna! Buxhowden (25,838 troops) at Moravia.
   Berthier: Enemy forces spotted near Vienna! Bennigsen (4,241 troops) at Moravia.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney +3(2673,126)  Napoleon(2376,248)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Yorck(2126,127)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Hohenlohe(2407,0)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1079,761)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Armfelt(2066,16)  Amey(1691,580)  10k(2376,360)  750(2089,538)  16k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1710,145)  ?(1660,304)  12k(1571,330)
```

```
#0207  scroll 1828 548 down 5  ->  ok
  (scrolled down 5 at (1828, 548))
view: <run>\frames\0207_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier: Enemy forces spotted near Vienna! Kutuzov (26,279 troops) at Moravia.
   Berthier: Enemy forces spotted near Vienna! Buxhowden (25,838 troops) at Moravia.
   Berthier: Enemy forces spotted near Vienna! Bennigsen (4,241 troops) at Moravia.
map: unchanged (115 labels)
```

```
#0208  scroll 1828 548 down 5  ->  ok
  (scrolled down 5 at (1828, 548))
view: <run>\frames\0208_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier: Enemy forces spotted near Vienna! Kutuzov (26,279 troops) at Moravia.
   Berthier: Enemy forces spotted near Vienna! Buxhowden (25,838 troops) at Moravia.
   Berthier: Enemy forces spotted near Vienna! Bennigsen (4,241 troops) at Moravia.
map: unchanged (115 labels)
```

```
#0209  scroll 1828 548 down 10  ->  ok
  (scrolled down 10 at (1828, 548))
view: <run>\frames\0209_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   Berthier: Enemy forces spotted near Vienna! Kutuzov (26,279 troops) at Moravia.
   Berthier: Enemy forces spotted near Vienna! Buxhowden (25,838 troops) at Moravia.
   Berthier: Enemy forces spotted near Vienna! Bennigsen (4,241 troops) at Moravia.
map: unchanged (115 labels)
```

```
#0210  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0210_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   PRUSSIA LOSSES
   0
   0
   ⚔
   Soult ◆
   Brunswick ◆
   17,657 → 13,759
   45,769 → 43,360 → 42,710 after the advance
   Yorck — awaits explicit orders
   BATTLE OF POMERANIA
   click anywhere to skip ▸
   POMERANIA · TURN 11
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ⚠ Starving — supply has failed at Dresden two turns running.
   - Amey — Bern — 3,500 — Awaiting orders.
   INTELLIGENCE
   Yorck — Berlin — 3,961 [confirmed]
   Kutuzov — Moravia — 26,279 [confirmed]
   Buxhowden — Moravia — 25,838 [confirmed]
   Bennigsen — Moravia — 4,241 [confirmed]
   Hohenlohe — Posen — 17,223 [confirmed]
   Brunswick — Pomerania — 41,890 [confirmed]
   Armfelt — Stralsund — 37,110 [confirmed]
   Archduke Charles — Carniola — substantial force [partial]
   Archduke John — Carniola — small force [partial]
   Deroy — Swabia — substantial force [partial]
   Castanos — Bordelais — small force [partial]
   Podolia garrison — Podolia — garrison of 3,000 [confirmed]
   Berlin garrison — Berlin — garrison of 25,000 [confirmed]
   Posen garrison — Posen — garrison of 3,000 [confirmed]
   Hanover garrison — Hanover — garrison — small force [stale - T8]
   TURN EVENTS
   Supply cost you 1,677 men, at Silesia and Pomerania.
   Garrison at Vienna reinforced: 14,000 -> 16,000
   Holland loyalty 70 (-3): satellite drift, the lord's defeats
   Berthier reports that Murat resents Ney's laurels again, 9 turns after the last — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Bernadotte appears envious of Ney's laurels — he has grown quiet in the way the staff have learned to read.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The armistice between France and Russia has collapsed. War resumes!
   REVANCHE: Prussia will not forgive France the loss of Silesia and 1 more province. A new design hardens in their court.
   The court of Prussia takes up a new design: Revanche.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled (2 held, unsettled: Pomerania, Silesia) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+5)
   COALITION THREAT
   Threat: 69/100 [Brewing]
   At this pace the courts consult on turn 14 and declare on turn 17: Austria and 9 lesser courts would march. Bound for now by a fresh peace: Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The Presence is read at every table in Europe, Sire. A victory with him at its head restores more than a province; a defeat under him costs more than one."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0211  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Soult ◆' (Control, layer 121))
view: <run>\frames\0211_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS LOST
   FRANCE LOSSES
   PRUSSIA LOSSES
   3,898
   2,409
   ⚔
   Soult ◆
   Brunswick ◆
   17,657 → 13,759
   45,769 → 43,360 → 42,710 after the advance
   Yorck — awaits explicit orders
   Berthier: “A narrow defeat for Soult, Sire. Better-prepared troops might have tipped the balance.” / Brunswick: "The moment was measured twice before I struck."
   BATTLE OF POMERANIA
   POMERANIA · TURN 11
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 69/100 [Brewing]
   At this pace the courts consult on turn 14 and declare on turn 17: Austria and 9 lesser courts would march. Bound for now by a fresh peace: Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The Presence is read at every table in Europe, Sire. A victory with him at its head restores more than a province; a defeat under him costs more than one."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0212  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0212_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   8,789
   Inf:
   81,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 69/100 [Brewing]
   At this pace the courts consult on turn 14 and declare on turn 17: Austria and 9 lesser courts would march. Bound for now by a fresh peace: Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The Presence is read at every table in Europe, Sire. A victory with him at its head restores more than a province; a defeat under him costs more than one."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0213  type where is Soult  ->  ok
  (typed and Enter)
view: <run>\frames\0213_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Marshal Soult stands at Pomerania with 13,606 men (morale 76).
── TopBar (layer 75) ──
   DP: 7/7
   Threat 69 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Ney orders lost @(3393,64)]  [icon: Davout — free attack! @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Marshal Murat seeks an audience @(3519,64)]  [icon: European Courts Concerned @(3561,64)]  [+29]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia + Russia
   +3
   T:2
   controls: [Prussia + Russia]
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► where is Soult
   Marshal Soult stands at Pomerania with 13,606 men (morale 76).
map: unchanged (115 labels)
```

```
#0214  click_at 3435 64  ->  ok
  (clicked at (3435, 64) on @Button@8937  (Button, layer 75))
view: <run>\frames\0214_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 69 / 100
   Turn 12 — Early March 1806
   Imperial Box
   Davout — free attack!
   T11
   Davout earned a free attack from his defensive victory — Hohenlohe stands within reach at Posen. Use it THIS turn or the opportunity expires.
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Ney orders lost @(3393,64)]  [icon: Davout — free attack! @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Marshal Murat seeks an audience @(3519,64)]  [icon: European Courts Concerned @(3561,64)]  [+29]  [Strike Hohenlohe — free]  [Keep]  [Acknowledge]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "The Presence is read at every table in Europe, Sire. A victory with him at its head restores more than a province; a defeat under him costs more than one."
   ════════════════════════════════════
   ► where is Soult
   Marshal Soult stands at Pomerania with 13,606 men (morale 76).
map: unchanged (115 labels)
```

```
#0215  click Strike Hohenlohe  ->  ok
  (clicked at (3503, 243))
view: <run>\frames\0215_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   PRUSSIA LOSSES
   0
   0
   Ney
   7,106 → 6,881
   Lannes
   11,651 → 11,282
   Massena
   15,591 → 15,196
   ⚔
   Davout ◆
   Hohenlohe ◆
   marched to the guns
   14,010 → 13,418
   17,223 → 11,328
   marched to the guns
   marched to the guns
   +1 corps in reserve — 184 lost
   SECOND BATTLE OF POSEN
   click anywhere to skip ▸
   POSEN · TURN 12
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 72 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Ney orders lost @(3393,64)]  [icon: Bernadotte arrived @(3435,64)]  [icon: Marshal Murat seeks an audience @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Bavaria Joins Offensive! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Prussia + Russia
   +8
   T:2
   controls: [Prussia + Russia]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   8,701
   Inf:
   81,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ========================================
   [!] COUNTER-PUNCH! (FREE ACTION) [!]
   ========================================
   Davout strikes back after successfully defending!
   This attack costs NO actions.
   [Combat] Davout's DEFENSIVE stance hampers offensive operations (-10% attack)
   [Combat] Davout attacks cautiously at unfavorable odds on his own numbers. (Cautious: -10% attack)
   [Shield] Hohenlohe's DEFENSIVE stance strengthens the line! (+15% defense)
   [Shield] Hohenlohe's methodical defense is exemplary! (Cautious: +20% total)
   Davout attacks with overwhelming force. Davout gains the advantage over Hohenlohe. Casualties: Davout's army 1,765, Hohenlohe 5,895. Both armies remain in the field. Davout halts before Posen's works — a detachment that fights to the last man of 3,000 still stands and must be assaulted.
   [Materiel] Guns, horses and stores lost with the fallen: France -88g, Prussia -294g.
   [!] Hohenlohe's broken army flees to Brandenburg! (56 lost to march) (recovering for 3 turns)
   ⚔ View the field
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 14,010 (lead) + 37,096 committed (Ney, Lannes, Massena, Napoleon) = 51,106.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 1,173 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Davout: "They attacked prepared ground. The result was never in doubt."
   Berthier: the corps marched apart and arrived together.
   the Prussian line broke: Brittle deepened the rout (−51 morale, not −34)
   Attack: Davout (Defensive stance -10%, Personality (cautious) -10%, The Emperor commands in person +10%)
   Defense: Hohenlohe (Defensive stance +15%, Personality (cautious) +5%)
   Casualties: Davout's own corps 592 | Hohenlohe 5,895
   Strength: Davout 14,010 → 13,418 | Hohenlohe 17,223 → 11,328
   Berthier: "Ney, Lannes, Massena and Napoleon arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire."
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Yorck(2126,127)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1079,761)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Armfelt(2066,16)  Amey(1691,580)  10k(2376,360)  750(2089,538)  16k(2470,651)  3k(2798,413)  25k(2126,239)  3k(2407,111)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1710,145)  ?(1660,304)  12k(1571,330)
```

```
#0216  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Davout ◆' (Control, layer 121))
view: <run>\frames\0216_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS OURS
   FRANCE LOSSES
   PRUSSIA LOSSES
   1,765
   5,895
   Ney
   7,106 → 6,881
   Lannes
   11,651 → 11,282
   Massena
   15,591 → 15,196
   ⚔
   Davout ◆
   Hohenlohe ◆
   marched to the guns
   14,010 → 13,418
   17,223 → 11,328
   marched to the guns
   marched to the guns
   +1 corps in reserve — 184 lost
   ROUTED
   Berthier: “Ney, Lannes, Massena and Napoleon arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire.” / Hohenlohe: "I decline a battle on your terms; the next is on mine."
   SECOND BATTLE OF POSEN
   POSEN · TURN 12
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Hohenlohe (Defensive stance +15%, Personality (cautious) +5%)
   Casualties: Davout's own corps 592 | Hohenlohe 5,895
   Strength: Davout 14,010 → 13,418 | Hohenlohe 17,223 → 11,328
   Berthier: "Ney, Lannes, Massena and Napoleon arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire."
map: unchanged (114 labels)
```

```
#0217  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0217_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Hohenlohe (Defensive stance +15%, Personality (cautious) +5%)
   Casualties: Davout's own corps 592 | Hohenlohe 5,895
   Strength: Davout 14,010 → 13,418 | Hohenlohe 17,223 → 11,328
   Berthier: "Ney, Lannes, Massena and Napoleon arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire."
map: unchanged (114 labels)
```

```
#0218  type where are Ney, Lannes, Massena and Napoleon  ->  ok
  (typed and Enter)
view: <run>\frames\0218_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Our marshals, Sire:
  Ney — 6,881 men at Posen, morale 0
  Lannes — 11,282 men at Posen, morale 65
  Massena — 15,196 men at Posen, morale 26
  Napoleon — 5,635 men at Posen, morale 50
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► where are Ney, Lannes, Massena and Napoleon
   Our marshals, Sire:
   Ney — 6,881 men at Posen, morale 0
   Lannes — 11,282 men at Posen, morale 65
   Massena — 15,196 men at Posen, morale 26
   Napoleon — 5,635 men at Posen, morale 50
map: unchanged (114 labels)
```

```
#0219  type Lannes, storm the Posen garrison  ->  ok
  (typed and Enter)
view: <run>\frames\0219_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok ASSAULT — Lannes storms the works at Posen alone: 11,282 men, 16,162 in the assault's reckoning (+13% from the corps at his side), against a garrison of 3,000. Ney, Davout, Massena and Napoleon do not join an assault on the works; a detachment fights to the last man.
Lannes assaults the Posen garrison! Garrison: 3,000 -> 1,500 (-1,500). Lannes loses 523 troops. Garrison holds — 1,500 defenders remain.
[Materiel] Guns, horses and stores lost with the fallen: France -26g, Prussia -75g.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia + Russia
   +5
   T:2
   controls: [Prussia + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/5
   Admin:
   2/2
   Gold:
   8,675
   Inf:
   81,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   [!] Hohenlohe's broken army flees to Brandenburg! (56 lost to march) (recovering for 3 turns)
   ⚔ View the field
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Lannes's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Davout!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 14,010 (lead) + 37,096 committed (Ney, Lannes, Massena, Napoleon) = 51,106.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 1,173 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Davout: "They attacked prepared ground. The result was never in doubt."
   Berthier: the corps marched apart and arrived together.
   the Prussian line broke: Brittle deepened the rout (−51 morale, not −34)
   Attack: Davout (Defensive stance -10%, Personality (cautious) -10%, The Emperor commands in person +10%)
   Defense: Hohenlohe (Defensive stance +15%, Personality (cautious) +5%)
   Casualties: Davout's own corps 592 | Hohenlohe 5,895
   Strength: Davout 14,010 → 13,418 | Hohenlohe 17,223 → 11,328
   Berthier: "Ney, Lannes, Massena and Napoleon arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire."
   ► where are Ney, Lannes, Massena and Napoleon
   Our marshals, Sire:
   Ney — 6,881 men at Posen, morale 0
   Lannes — 11,282 men at Posen, morale 65
   Massena — 15,196 men at Posen, morale 26
   Napoleon — 5,635 men at Posen, morale 50
   ► Lannes, storm the Posen garrison
   ASSAULT — Lannes storms the works at Posen alone: 11,282 men, 16,162 in the assault's reckoning (+13% from the corps at his side), against a garrison of 3,000. Ney, Davout, Massena and Napoleon do not join an assault on the works; a detachment fights to the last man.
   Lannes assaults the Posen garrison! Garrison: 3,000 -> 1,500 (-1,500). Lannes loses 523 troops. Garrison holds — 1,500 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -26g, Prussia -75g.
   [4/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Yorck(2126,127)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1079,761)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Armfelt(2066,16)  Amey(1691,580)  10k(2376,360)  750(2089,538)  16k(2470,651)  3k(2798,413)  25k(2126,239)  1k(2407,111)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1710,145)  ?(1660,304)  12k(1571,330)
```

```
#0220  type Massena, storm the Posen garrison  ->  ok
  (typed and Enter)
view: <run>\frames\0220_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok ASSAULT — Massena storms the works at Posen alone: 15,196 men, 21,625 in the assault's reckoning (+12% from the corps at his side), against a garrison of 1,500. Ney, Davout, Lannes and Napoleon do not join an assault on the works; a detachment fights to the last man.
Massena assaults the Posen garrison! Garrison: 1,500 -> 750 (-750). Massena loses 263 troops. Garrison holds — 750 defenders remain.
[Materiel] Guns, horses and stores lost with the fallen: France -13g, Prussia -37g.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia + Russia
   +3
   T:2
   controls: [Prussia + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   8,662
   Inf:
   81,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, storm the Posen garrison
   ASSAULT — Massena storms the works at Posen alone: 15,196 men, 21,625 in the assault's reckoning (+12% from the corps at his side), against a garrison of 1,500. Ney, Davout, Lannes and Napoleon do not join an assault on the works; a detachment fights to the last man.
   Massena assaults the Posen garrison! Garrison: 1,500 -> 750 (-750). Massena loses 263 troops. Garrison holds — 750 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -13g, Prussia -37g.
   [3/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Yorck(2126,127)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1079,761)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Armfelt(2066,16)  Amey(1691,580)  10k(2376,360)  750(2089,538)  16k(2470,651)  3k(2798,413)  25k(2126,239)  750(2407,111)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1710,145)  ?(1660,304)  12k(1571,330)
```

```
#0221  type Napoleon, storm the Posen garrison  ->  ok
  (typed and Enter)
view: <run>\frames\0221_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok ASSAULT — Napoleon storms the works at Posen alone: 5,635 men, 6,961 in the assault's reckoning (+13% from the corps at his side), against a garrison of 750. Ney, Davout, Lannes and Massena do not join an assault on the works; a detachment fights to the last man.
Napoleon assaults the Posen garrison! Garrison: 750 -> 375 (-375). Napoleon loses 151 troops. Garrison holds — 375 defenders remain.
[Materiel] Guns, horses and stores lost with the fallen: France -7g, Prussia -18g.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   8,655
   Inf:
   81,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, storm the Posen garrison
   ASSAULT — Napoleon storms the works at Posen alone: 5,635 men, 6,961 in the assault's reckoning (+13% from the corps at his side), against a garrison of 750. Ney, Davout, Lannes and Massena do not join an assault on the works; a detachment fights to the last man.
   Napoleon assaults the Posen garrison! Garrison: 750 -> 375 (-375). Napoleon loses 151 troops. Garrison holds — 375 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -7g, Prussia -18g.
   [2/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Yorck(2126,127)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1079,761)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Armfelt(2066,16)  Amey(1691,580)  10k(2376,360)  750(2089,538)  16k(2470,651)  3k(2798,413)  25k(2126,239)  375(2407,111)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1710,145)  ?(1660,304)  12k(1571,330)
```

```
#0222  type Lannes, take Posen  ->  ok
  (typed and Enter)
view: <run>\frames\0222_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok The detachment of 375 at Posen lays down its arms. Lannes takes Posen where he stands! Captured: Prussia → France
Your forces have taken Posen. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Lannes has taken Posen
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+600 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 74 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   1/5
   Admin:
   2/2
   Gold:
   8,655
   Inf:
   81,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Lannes, take Posen
   ⚑ The detachment of 375 at Posen lays down its arms. Lannes takes Posen where he stands! Captured: Prussia → France
   Your forces have taken Posen. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [1/5 actions remaining]
   Your forces await orders: Plunder or Secure?
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Yorck(2126,127)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1079,761)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Armfelt(2066,16)  Amey(1691,580)  10k(2376,360)  750(2089,538)  16k(2470,651)  3k(2798,413)  25k(2126,239)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1710,145)  ?(1660,304)  12k(1571,330)
```

```
#0223  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0223_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 74 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Ney orders lost @(3393,64)]  [icon: Bernadotte arrived @(3435,64)]  [icon: Marshal Murat seeks an audience @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Bavaria Joins Offensive! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia + Russia
   +10
   T:2
   controls: [Prussia + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   1/5
   Admin:
   2/2
   Gold:
   8,655
   Inf:
   81,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 1,173 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Davout: "They attacked prepared ground. The result was never in doubt."
   Berthier: the corps marched apart and arrived together.
   the Prussian line broke: Brittle deepened the rout (−51 morale, not −34)
   Attack: Davout (Defensive stance -10%, Personality (cautious) -10%, The Emperor commands in person +10%)
   Defense: Hohenlohe (Defensive stance +15%, Personality (cautious) +5%)
   Casualties: Davout's own corps 592 | Hohenlohe 5,895
   Strength: Davout 14,010 → 13,418 | Hohenlohe 17,223 → 11,328
   Berthier: "Ney, Lannes, Massena and Napoleon arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire."
   ► where are Ney, Lannes, Massena and Napoleon
   Our marshals, Sire:
   Ney — 6,881 men at Posen, morale 0
   Lannes — 11,282 men at Posen, morale 65
   Massena — 15,196 men at Posen, morale 26
   Napoleon — 5,635 men at Posen, morale 50
   ► Lannes, storm the Posen garrison
   ASSAULT — Lannes storms the works at Posen alone: 11,282 men, 16,162 in the assault's reckoning (+13% from the corps at his side), against a garrison of 3,000. Ney, Davout, Massena and Napoleon do not join an assault on the works; a detachment fights to the last man.
   Lannes assaults the Posen garrison! Garrison: 3,000 -> 1,500 (-1,500). Lannes loses 523 troops. Garrison holds — 1,500 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -26g, Prussia -75g.
   [4/5 actions remaining]
   ► Massena, storm the Posen garrison
   ASSAULT — Massena storms the works at Posen alone: 15,196 men, 21,625 in the assault's reckoning (+12% from the corps at his side), against a garrison of 1,500. Ney, Davout, Lannes and Napoleon do not join an assault on the works; a detachment fights to the last man.
   Massena assaults the Posen garrison! Garrison: 1,500 -> 750 (-750). Massena loses 263 troops. Garrison holds — 750 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -13g, Prussia -37g.
   [3/5 actions remaining]
   ► Napoleon, storm the Posen garrison
   ASSAULT — Napoleon storms the works at Posen alone: 5,635 men, 6,961 in the assault's reckoning (+13% from the corps at his side), against a garrison of 750. Ney, Davout, Lannes and Massena do not join an assault on the works; a detachment fights to the last man.
   Napoleon assaults the Posen garrison! Garrison: 750 -> 375 (-375). Napoleon loses 151 troops. Garrison holds — 375 defenders remain.
   [Materiel] Guns, horses and stores lost with the fallen: France -7g, Prussia -18g.
   [2/5 actions remaining]
   ► Lannes, take Posen
   ⚑ The detachment of 375 at Posen lays down its arms. Lannes takes Posen where he stands! Captured: Prussia → France
   Your forces have taken Posen. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [1/5 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Lannes secures Posen. Stability set to 25. Order is maintained. 1 building damaged.
map: unchanged (113 labels)
```

```
#0224  type Davout, hold Silesia  ->  ok
  (typed and Enter)
view: <run>\frames\0224_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Not enough actions! Need 2, have 1 — Davout cannot hold Silesia today.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, hold Silesia
   Not enough actions! Need 2, have 1 — Davout cannot hold Silesia today.
map: unchanged (113 labels)
```

```
#0225  type Ney, drill  ->  ok
  (typed and Enter)
view: <run>\frames\0225_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Ney cannot drill with enemy forces nearby! Hohenlohe is at Brandenburg, just one region away.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, drill
   Ney cannot drill with enemy forces nearby! Hohenlohe is at Brandenburg, just one region away.
map: unchanged (113 labels)
```

```
#0226  type Lannes, attack Hohenlohe at Brandenburg  ->  ok
  (typed and Enter)
view: <run>\frames\0226_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok MUSTER — Lannes (10,759) vs Hohenlohe (strength unknown) at Brandenburg — the balance of force looks even — a hard fight that may well decide nothing.
  WILL NOT — Ney: has already marched this turn
  WILL NOT — Soult: is pinned by enemies before his own front
  WILL NOT — Massena: has already marched this turn
  WILL NOT — Napoleon: has already marched this turn
  What Brandenburg can feed is not known — the province is unscouted.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.

[!] Hohenlohe is EXPOSED! (Just retreated, no ally to cover)


[Combat] Lannes leads the charge! (Aggressive: +15% attack)
[Shield] Hohenlohe's DEFENSIVE stance strengthens the line! (+15% defense)
[Shield] Hohenlohe's methodical defense is exemplary! (Cautious: +20% total)
[Alert] Lannes's troops are exhausted from repeated attacks! (2nd attack: -10%)
[Combat] Adjacent allies bolster Lannes's attack! (+8%)
Lannes's attack meets fierce resistance. Lannes gains the advantage over Hohenlohe. Casualties: Lannes 354, Hohenlohe 6,203. Both armies remain in the field.

[!] Hohenlohe's troops are BROKEN (morale 0%)! FORCED RETREAT! Lannes advances into Brandenburg. (104 lost to march) Brandenburg has been captured by France!
[Materiel] Guns, horses and stores lost with the fallen: France -17g, Prussia -310g.
[!] Hohenlohe's broken army flees to Berlin! (recovering for 3 turns)
Your fo
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Lannes has taken Brandenburg
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+400 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 79 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   0/5
   Admin:
   2/2
   Gold:
   8,638
   Inf:
   81,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [1/5 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Lannes secures Posen. Stability set to 25. Order is maintained. 1 building damaged.
   ► Davout, hold Silesia
   Not enough actions! Need 2, have 1 — Davout cannot hold Silesia today.
   ► Ney, drill
   Ney cannot drill with enemy forces nearby! Hohenlohe is at Brandenburg, just one region away.
   ► Lannes, attack Hohenlohe at Brandenburg
   ⚔ Battle of Brandenburg ⚔
   MUSTER — Lannes (10,759) vs Hohenlohe (strength unknown) at Brandenburg — the balance of force looks even — a hard fight that may well decide nothing.
   WILL NOT — Ney: has already marched this turn
   WILL NOT — Soult: is pinned by enemies before his own front
   WILL NOT — Massena: has already marched this turn
   WILL NOT — Napoleon: has already marched this turn
   What Brandenburg can feed is not known — the province is unscouted.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [!] Hohenlohe is EXPOSED! (Just retreated, no ally to cover)
   [Combat] Lannes leads the charge! (Aggressive: +15% attack)
   [Shield] Hohenlohe's DEFENSIVE stance strengthens the line! (+15% defense)
   [Shield] Hohenlohe's methodical defense is exemplary! (Cautious: +20% total)
   [Alert] Lannes's troops are exhausted from repeated attacks! (2nd attack: -10%)
   [Combat] Adjacent allies bolster Lannes's attack! (+8%)
   Lannes's attack meets fierce resistance. Lannes gains the advantage over Hohenlohe. Casualties: Lannes 354, Hohenlohe 6,203. Both armies remain in the field.
   [!] Hohenlohe's troops are BROKEN (morale 0%)! FORCED RETREAT! Lannes advances into Brandenburg. (104 lost to march) Brandenburg has been captured by France!
   [Materiel] Guns, horses and stores lost with the fallen: France -17g, Prussia -310g.
   [!] Hohenlohe's broken army flees to Berlin! (recovering for 3 turns)
   Your forces have taken Brandenburg. Plunder it for 400 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   ⚑ Brandenburg captured! ⚑
   ⚔ View the field
   [0/5 actions remaining]
   --- Berthier's Report ---
   Lannes: "The grenadiers went in with the bayonet and asked no questions."
   the Prussian line broke: Brittle deepened the rout (−82 morale, not −55)
   Attack: Lannes (Personality (aggressive) +15%, Exhaustion -10%)
   Defense: Hohenlohe (Defensive stance +15%, Personality (cautious) +5%)
   Casualties: Lannes 354 | Hohenlohe 6,203
   Strength: Lannes 10,759 → 10,405 → 10,301 after the advance | Hohenlohe 11,272 → 5,069
   Berthier: "Hohenlohe bled two men for each of Lannes's. A clear exchange, not yet a decision."
   Your forces await orders: Plunder or Secure?
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Hohenlohe(2099,127)  Yorck(2154,93)  Kutuzov(2638,496)  Buxhowden(2666,462)  Bennigsen(2694,428)  Ney(2379,0)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1079,761)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Armfelt(2066,16)  Amey(1691,580)  10k(2376,360)  750(2089,538)  16k(2470,651)  3k(2798,413)  25k(2126,239)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1710,145)  ?(1660,304)  12k(1571,330)
```

```
#0227  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0227_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   PRUSSIA LOSSES
   0
   0
   ⚔
   Lannes ◆
   Hohenlohe ◆
   10,759 → 10,405 → 10,301 after the advance
   11,272 → 5,069
   Yorck — awaits explicit orders
   BATTLE OF BRANDENBURG
   click anywhere to skip ▸
   BRANDENBURG · TURN 12
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 79 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Ney orders lost @(3393,64)]  [icon: Bernadotte arrived @(3435,64)]  [icon: Marshal Murat seeks an audience @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Bavaria Joins Offensive! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Prussia + Russia
   +20
   T:2
   controls: [Prussia + Russia]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You order your troops to secure the region.
   Lannes secures Brandenburg. Stability set to 25. Order is maintained.
map: unchanged (114 labels)
```

```
#0228  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Lannes ◆' (Control, layer 121))
view: <run>\frames\0228_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS OURS
   FRANCE LOSSES
   PRUSSIA LOSSES
   354
   6,203
   Brandenburg falls to France.
   ⚔
   Lannes ◆
   Hohenlohe ◆
   10,759 → 10,405 → 10,301 after the advance
   11,272 → 5,069
   ROUTED
   Yorck — awaits explicit orders
   Berthier: “Hohenlohe bled two men for each of Lannes's. A clear exchange, not yet a decision.” / Hohenlohe: "Retired in order. The army outlives the field."
   BATTLE OF BRANDENBURG
   BRANDENBURG · TURN 12
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Hohenlohe bled two men for each of Lannes's. A clear exchange, not yet a decision."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Lannes secures Brandenburg. Stability set to 25. Order is maintained.
map: unchanged (114 labels)
```

```
#0229  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0229_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   0/5
   Admin:
   2/2
   Gold:
   8,638
   Inf:
   81,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "Hohenlohe bled two men for each of Lannes's. A clear exchange, not yet a decision."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Lannes secures Brandenburg. Stability set to 25. Order is maintained.
map: unchanged (114 labels)
```

```
#0230  click Prussia + Russia  ->  ok
  (clicked at (3429, 996))
view: <run>\frames\0230_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) ──
   WAR WITH PRUSSIA + RUSSIA
   PR
   +20
   FR
   The ledger of one war — its score, its fronts, and the price of peace. Negotiate ends it. /  / Score Breakdown /   Territory:  +20 /   Battles:    -6 /   Decisive:   0 /   Capital:    0 /   Campaign:   +6 /   Blood:      +3 /   Ticking:    -3 /  / Settlement Tier: Favorable Terms / Objective: Defense - the homeland — 28 of 28 provinces held (against Russia) (not ticking, +0) — +1/turn once it begi …
   controls: [icon @(3139,276)]  [Negotiate Peace]  [Open Settlement]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Hohenlohe bled two men for each of Lannes's. A clear exchange, not yet a decision."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Lannes secures Brandenburg. Stability set to 25. Order is maintained.
map: unchanged (114 labels)
```

```
#0231  click Open Settlement  ->  ok
  (clicked at (2954, 784))
view: <run>\frames\0231_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   This settlement cannot be ratified now. / France vs Prussia + Russia - Whole-war settlement / Covered enemies: Prussia, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Prussia 12/50, Russia -4/50. / Treasury 8,638 gold: committed 0 / reserve 500 / remaining 8,138 / Sire, this settlement of France vs Prussia + Russia seats 2 courts at the table. Prussia will not sign; t …
   The table /   * Prussia ▸ - Holding out (12/50) White peace /       Blocker: Settlement legitimacy /       Hardenberg is plain: Prussia will not sign while it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. /       + Add demand /   * Russia ▸ - Holding out (-4/50) White peace /       Blocker: Settlement legitimacy /       Czartorysk …
   Prussia:
   Russia:
   Sire, a white peace for France vs Prussia + Russia cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. Author terms or hold until the field shifts. Vilna is unbeaten — a whole-war peace needs its consent (Prussia 12/50, Russia -4/50). Press Prussia alone: the separate peace. It costs 3 diplomatic points …
   controls: <Prussia ▸>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Press Prussia]  [Ease Prussia]  [Drop Prussia]  [Press Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 79 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   0/5
   Admin:
   2/2
   Gold:
   8,638
   Inf:
   81,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Opening settlement review for Prussia
map: unchanged (114 labels)
```

```
#0232  click Drop Russia  ->  ok
  (clicked at (1782, 639))
view: <run>\frames\0232_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   This settlement cannot be ratified now. / France vs Prussia - Separate settlement / Covered enemies: Prussia / Still at war: Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Prussia 14/50. / Treasury 8,638 gold: committed 0 / reserve 500 / remaining 8,138 / Sire, this settlement of France vs Prussia seats 1 courts at the table. Prussia will not sign; the settlement of F …
   The table /   * Prussia ▸ - Holding out (14/50) White peace /       Blocker: Settlement legitimacy /       Hardenberg is plain: Prussia will not sign while it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. /       + Add demand / Prussia is the holdout. / ▸ Prussia won't accept these terms yet. Use 'More generous' (or ease a court)  …
   Prussia:
   Coverage:
   Sire, a white peace for France vs Prussia cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. Author terms or hold until the field shifts. Every covered court has been beaten in the field — a whole-war peace still needs each one's consent (Prussia 14/50). Press Prussia alone: the separate peace. It cost …
   controls: <Prussia ▸>  <+ Add demand>  [Press Prussia]  [Ease Prussia]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement cover drop
map: unchanged (114 labels)
```

```
#0233  click More generous  ->  ok
  (clicked at (1829, 884))
view: <run>\frames\0233_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   This settlement cannot be ratified now. / France vs Prussia - Separate settlement / Covered enemies: Prussia / Still at war: Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Prussia 8/50. / Treasury 8,638 gold: committed 100 / reserve 500 / remaining 8,038 / Sire, this settlement of France vs Prussia seats 1 courts at the table. Prussia will not sign; the settlement of  …
   The table /   * Prussia ▸ - Holding out (8/50) Conceded: 100g /       Blocker: Settlement legitimacy /       Hardenberg is plain: Prussia will not sign while the terms claim a victory the field has not delivered. /       Conceded · France pays 100 gold  [-][+]  Remove /       + Add demand / Prussia is the holdout. / ▸ Prussia won't accept these terms yet. Use 'More generous' (or ease a court) unti …
   Prussia:
   Coverage:
   Sire, the settlement of France vs Prussia cannot be ratified now: the terms claim a victory the field has not delivered. Revise terms or stand down before pressing further. Every covered court has been beaten in the field — a whole-war peace still needs each one's consent (Prussia 8/50). Press Prussia alone: the separate peace. It costs 3 diplomatic points; you have 7. /  / Allies and Standing /   …
   controls: <Prussia ▸>  <Remove>  <+ Add demand>  [Press Prussia]  [Ease Prussia]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (114 labels)
```

```
#0234  click Back Out  ->  ok
  (clicked at (1455, 937))
view: <run>\frames\0234_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 79 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Ney orders lost @(3393,64)]  [icon: Bernadotte arrived @(3435,64)]  [icon: Marshal Murat seeks an audience @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Bavaria Joins Offensive! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia + Russia
   +20
   T:2
   controls: [Prussia + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   0/5
   Admin:
   2/2
   Gold:
   8,638
   Inf:
   81,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (114 labels)
```

```
#0235  type recruit infantry for Bernadotte  ->  ok
  (typed and Enter)
view: <run>\frames\0235_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte recruits 3,000 infantry at Gascony (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
Infantry pool: 81,162 -> 78,162 [WARNING] Morale dropped to 32% — consider drilling before battle.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   0/5
   Admin:
   1/2
   Gold:
   8,038
   Inf:
   78,162
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Gascony (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
   Infantry pool: 81,162 -> 78,162 [WARNING] Morale dropped to 32% — consider drilling before battle.
   [0/5 actions remaining]
map: unchanged (114 labels)
```

```
#0236  type recruit cavalry for Murat  ->  ok
  (typed and Enter)
view: <run>\frames\0236_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat recruits 3,000 cavalry at Nivernais (field levy — no depot; capped at 3,000) - Cost: 1035 gold (×3 at war) (Murat's intendance: +15%). Morale: 73% -> 68%
Cavalry pool: 30,000 -> 27,000 That was the last order the day could take, Sire — the turn ends when you say so.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   0/5
   Admin:
   0/2
   Gold:
   7,003
   Inf:
   78,162
   Cav:
   27,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E) ▸]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit cavalry for Murat
   + Murat recruits 3,000 cavalry at Nivernais (field levy — no depot; capped at 3,000) - Cost: 1035 gold (×3 at war) (Murat's intendance: +15%). Morale: 73% -> 68%
   Cavalry pool: 30,000 -> 27,000 That was the last order the day could take, Sire — the turn ends when you say so.
   [0/5 actions remaining]
map: unchanged (114 labels)
```

```
#0237  click End Turn  ->  ok
  (clicked at (929, 978))
view: <run>\frames\0237_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 12
   RUSSIA / ──────────────────────────── / - Bennigsen abandons fortified position / - Buxhowden abandons fortified position / - Kutuzov abandons fortified position / - Bennigsen moves to Vienna / - Buxhowden attacks Vienna /     Assault on the garrison of Vienna /       Garrison: 8,000 lost, 8,000 still under arms /       The assault cost them 4,040. / - Kutuzov attacks Vienna /     Region captured: …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 78 / 100
   Turn 13 — Late March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   8,319
   Inf:
   80,162
   Cav:
   28,750
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Lannes secures Brandenburg. Stability set to 25. Order is maintained.
   Opening settlement review for Prussia
   Directing Talleyrand: settlement cover drop
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Gascony (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
   Infantry pool: 81,162 -> 78,162 [WARNING] Morale dropped to 32% — consider drilling before battle.
   [0/5 actions remaining]
   ► recruit cavalry for Murat
   + Murat recruits 3,000 cavalry at Nivernais (field levy — no depot; capped at 3,000) - Cost: 1035 gold (×3 at war) (Murat's intendance: +15%). Morale: 73% -> 68%
   Cavalry pool: 30,000 -> 27,000 That was the last order the day could take, Sire — the turn ends when you say so.
   [0/5 actions remaining]
   ► end turn
   Your unratified settlement draft with Prussia (2 clauses) was set aside at turn's end.
   ═══════════════════════════════════════
   TURN 13 BEGINS
   ═══════════════════════════════════════
   Income: 2870g | Occupation: -192g | Charges of Empire: -398g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Materiel: -1116g | Other: +1386g | Upkeep: -824g | Net: +1316g | Spent: 1635g
   Treasury: 8,319g
   Actions refreshed: 5/5
   Soult's army is recovering. Effectiveness penalty: -30%.
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   Austria completes a market at Moravia.
   Crowded at Posen: Ney loses 137 troops to the press of 3 corps on one province's roads
   Crowded at Posen: Massena loses 298 troops to the press of 3 corps on one province's roads
   Crowded at Posen: Napoleon loses 109 troops to the press of 3 corps on one province's roads
   Supply shortage at Gascony: Bernadotte loses 27 troops
   Supply shortage at Brandenburg: Soult loses 202 troops — 30 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Brandenburg: Lannes loses 115 troops — 17 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Brandenburg: Brunswick loses 1,049 troops
   Supply shortage at Nivernais: Murat loses 6 troops
   Supply shortage at Stralsund: Armfelt loses 361 troops
   Garrison at Vienna reinforced: 0 -> 2,000
   Holland loyalty 64 (-6): the lord's defeats, satellite drift
   Kingdom of Italy loyalty 88 (-4): the lord's defeats, satellite drift
   Switzerland loyalty 81 (-4): the lord's defeats, satellite drift
   Territorial rivalry between Britain and Portugal grows.
   Berthier notes that Lannes's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-51)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Kutuzov(2443,539)  Bennigsen(2498,505)  Hohenlohe(2099,127)  Yorck(2154,93)  Buxhowden(2666,496)  Ney(2379,0)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1079,761)  ?(811,816)  Castanos(811,782)  Murat(1644,505)  Armfelt(2066,16)  Amey(1691,580)  ?(2376,360)  375(2089,538)  2k(2470,651)  3k(2798,413)  25k(2126,239)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1660,304)  12k(1571,330)
```

```
#0238  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0238_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt'], region_panel=no
── InterruptPopup (layer 103) ──
   LANNES REPORTS
   "Lannes is cornered at Brandenburg with 4,905 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout."
   controls: [Fight to the Last]  [Attempt a Breakout]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   --- Strategic Order Updates ---
   Lannes: Lannes is cornered at Brandenburg with 4,905 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
   Lannes awaits your orders!
map: unchanged (113 labels)
```

```
#0239  click Attempt a Breakout  ->  ok
  (clicked at (1971, 564))
view: <run>\frames\0239_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   PRUSSIA LOSSES
   0
   0
   ⚔
   Lannes ◆
   Brunswick ◆
   10,301 → 4,905
   40,279 → 39,052 → 38,467 after the advance
   Yorck — awaits explicit orders
   SECOND BATTLE OF BRANDENBURG
   click anywhere to skip ▸
   BRANDENBURG · TURN 12
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 78 / 100
   Turn 13 — Late March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Lannes is cornered @(3393,64)]  [icon: Ney orders lost @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: Marshal Murat seeks an audience @(3519,64)]  [icon: European Courts Concerned @(3561,64)]  [+29]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Prussia + Russia
   +20
   T:2
   controls: [Prussia + Russia]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   8,319
   Inf:
   82,557
   Cav:
   28,750
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ? Lannes — Brandenburg — 4,790 — Lannes, crowned last turn, has been beaten in the field. Morale:0%
   ⚠ IN PERIL — an enemy force of ~37,418 shares the field (Brandenburg).
   - Amey — Bern — 3,500 — Awaiting orders.
   INTELLIGENCE
   Kutuzov — Vienna — 23,784 [confirmed]
   Bennigsen — Vienna — 4,199 [confirmed]
   Hohenlohe — Berlin — 5,069 [confirmed]
   Yorck — Berlin — 3,794 [confirmed]
   Buxhowden — Moravia — 21,798 [confirmed]
   Brunswick — Brandenburg — 37,418 [confirmed]
   Armfelt — Stralsund — 36,749 [confirmed]
   Archduke Charles — Carniola — substantial force [partial]
   Archduke John — Carniola — small force [partial]
   Deroy — Swabia — substantial force [partial]
   Castanos — Bordelais — small force [partial]
   Vienna garrison — Vienna — garrison of 2,000 [confirmed]
   Podolia garrison — Podolia — garrison of 3,000 [confirmed]
   Berlin garrison — Berlin — garrison of 25,000 [confirmed]
   TURN EVENTS
   Soult's army is recovering. Effectiveness penalty: -30%.
   Supply cost you 894 men, at Posen, Gascony, Brandenburg and 1 more.
   Vienna's garrison regains 2,000: 0 -> 2,000.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   Berthier notes that Lannes's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   THE DOCTRINES: Britain brings the Militia Transfer into force beside its Staff — Irreplaceable is over; its army gathers as ours does.
   War exhaustion grows — France nears breaking point (exhaustion: 23).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   THE LAWS: Prussia cannot pay for the Emancipation Edict — the law lapses.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 37 of 45 titled (3 held, unsettled: Brandenburg, Posen, Silesia) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-7)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+3)
   COALITION THREAT
   Threat: 78/100 [Brewing]
   At this pace the courts consult on turn 14 and declare on turn 17: Austria and 9 lesser courts would march. Bound for now by a fresh peace: Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
map: unchanged (113 labels)
```

```
#0240  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Lannes ◆' (Control, layer 121))
view: <run>\frames\0240_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS LOST
   FRANCE LOSSES
   PRUSSIA LOSSES
   5,396
   1,227
   ⚔
   Lannes ◆
   Brunswick ◆
   10,301 → 4,905
   40,279 → 39,052 → 38,467 after the advance
   ROUTED
   Yorck — awaits explicit orders
   Berthier: “The toll on Lannes's forces is heavy, Sire. This defeat will be felt.” / Brunswick: "You were overextended. I merely presented the invoice."
   SECOND BATTLE OF BRANDENBURG
   BRANDENBURG · TURN 12
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 78/100 [Brewing]
   At this pace the courts consult on turn 14 and declare on turn 17: Austria and 9 lesser courts would march. Bound for now by a fresh peace: Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
map: unchanged (113 labels)
```

```
#0241  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0241_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   8,319
   Inf:
   82,557
   Cav:
   28,750
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 78/100 [Brewing]
   At this pace the courts consult on turn 14 and declare on turn 17: Austria and 9 lesser courts would march. Bound for now by a fresh peace: Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
map: unchanged (113 labels)
```

```
#0242  type status  ->  ok
  (typed and Enter)
view: <run>\frames\0242_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok === BERTHIER'S INTELLIGENCE REPORT ===

YOUR FORCES:
  Ney (Posen): 6,744 troops, morale 0, neutral stance
  Davout (Silesia): 13,418 troops, morale 60, defensive stance
  Soult (Brandenburg): 8,407 troops, morale 23, neutral stance, retreating
  Murat (Nivernais): 22,944 troops, morale 68, neutral stance
  Bernadotte (Gascony): 31,687 troops, morale 32, neutral stance
  Massena (Posen): 14,635 troops, morale 26, neutral stance
  Napoleon (Posen): 5,375 troops, morale 50, neutral stance
  Amey (Bern): 3,500 troops, morale 100, neutral stance

PRISONERS:
  Lannes: held by Prussia at Berlin since T13.

CONFIRMED INTELLIGENCE:
  Kutuzov (Russia): 23,784 troops at Vienna, defensive stance, morale 100 — famed for 'The Old Fox'
  Bennigsen (Russia): 4,199 troops at Vienna, defensive stance, morale 100
  Vienna (Russia): garrison of 2,000 holds the works
  Podolia (Russia): garrison of 3,000 holds the works
  Hohenlohe (Prussia): 5,069 troops at Berlin, defensive stance, morale 10
  Yorck (Prussia): 3,794 troops at Berlin, neutral stance, morale 100
  Berlin (Prussia): garrison of 25,000 holds the works
  Buxhowden (Russia): 21,798 troops at Moravia, defensive stance, morale 100
  Brunswick (Prussia): 37,418 troops at Brandenburg, defensive stance, morale 99
  Armfelt (Sweden): 36,749 troops at Stralsund, defensive stance, morale 55

RECENT REPORTS:
  Archduke Charles, Archduke John: substantial force near Carniola
  Deroy: substantial force near Swabia
  Castanos: small force near 
── TopBar (layer 75) ──
   DP: 7/7
   Threat 78 / 100
   Turn 13 — Late March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Ney orders lost @(3393,64)]  [icon: Bernadotte arrived @(3435,64)]  [icon: Marshal Murat seeks an audience @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Bavaria Joins Offensive! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia + Russia
   -4
   T:3
   controls: [Prussia + Russia]
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Posen): 6,744 troops, morale 0, neutral stance
   Davout (Silesia): 13,418 troops, morale 60, defensive stance
   Soult (Brandenburg): 8,407 troops, morale 23, neutral stance, retreating
   Murat (Nivernais): 22,944 troops, morale 68, neutral stance
   Bernadotte (Gascony): 31,687 troops, morale 32, neutral stance
   Massena (Posen): 14,635 troops, morale 26, neutral stance
   Napoleon (Posen): 5,375 troops, morale 50, neutral stance
   Amey (Bern): 3,500 troops, morale 100, neutral stance
   PRISONERS:
   Lannes: held by Prussia at Berlin since T13.
   CONFIRMED INTELLIGENCE:
   Kutuzov (Russia): 23,784 troops at Vienna, defensive stance, morale 100 — famed for 'The Old Fox'
   Bennigsen (Russia): 4,199 troops at Vienna, defensive stance, morale 100
   Vienna (Russia): garrison of 2,000 holds the works
   Podolia (Russia): garrison of 3,000 holds the works
   Hohenlohe (Prussia): 5,069 troops at Berlin, defensive stance, morale 10
   Yorck (Prussia): 3,794 troops at Berlin, neutral stance, morale 100
   Berlin (Prussia): garrison of 25,000 holds the works
   Buxhowden (Russia): 21,798 troops at Moravia, defensive stance, morale 100
   Brunswick (Prussia): 37,418 troops at Brandenburg, defensive stance, morale 99
   Armfelt (Sweden): 36,749 troops at Stralsund, defensive stance, morale 55
   RECENT REPORTS:
   Archduke Charles, Archduke John: substantial force near Carniola
   Deroy: substantial force near Swabia
   Castanos: small force near Bordelais
   NO INTELLIGENCE: No word from 66 provinces beyond the frontiers of Estonia, Volhynia, Albania, Aragon, Croatia, Rome, Ukraine, Norrland.
map: unchanged (113 labels)
```

```
#0243  click Prussia + Russia  ->  ok
  (clicked at (3429, 996))
view: <run>\frames\0243_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) ──
   WAR WITH PRUSSIA + RUSSIA
   PR
   −4
   FR
   The ledger of one war — its score, its fronts, and the price of peace. Negotiate ends it. /  / Score Breakdown /   Territory:  +15 /   Battles:    -12 /   Decisive:   0 /   Capital:    0 /   Campaign:   +2 /   Blood:      -3 /   Ticking:    -6 /  / Settlement Tier: White Peace / Objective: Defense - the homeland — 28 of 28 provinces held (against Russia) (not ticking, +0) — +1/turn once it begins  …
   controls: [icon @(3139,276)]  [Negotiate Peace]  [Open Settlement]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Archduke Charles, Archduke John: substantial force near Carniola
   Deroy: substantial force near Swabia
   Castanos: small force near Bordelais
   NO INTELLIGENCE: No word from 66 provinces beyond the frontiers of Estonia, Volhynia, Albania, Aragon, Croatia, Rome, Ukraine, Norrland.
map: unchanged (113 labels)
```

```
#0244  click Open Settlement  ->  ok
  (clicked at (2954, 784))
view: <run>\frames\0244_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   This settlement cannot be ratified now. / France vs Prussia + Russia - Whole-war settlement / Covered enemies: Prussia, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Prussia 4/50, Russia -3/50. / Treasury 8,319 gold: committed 0 / reserve 500 / remaining 7,819 / Sire, this settlement of France vs Prussia + Russia seats 2 courts at the table. Prussia will not sign; th …
   The table /   * Prussia ▸ - Holding out (4/50) White peace /       Blocker: Settlement legitimacy /       Hardenberg is plain: Prussia will not sign while it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. /       + Add demand /   * Russia ▸ - Holding out (-3/50) White peace /       Blocker: Settlement legitimacy /       Czartoryski …
   Prussia:
   Russia:
   Sire, a white peace for France vs Prussia + Russia cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. Author terms or hold until the field shifts. Vilna is unbeaten — a whole-war peace needs its consent (Prussia 4/50, Russia -3/50). Press Prussia alone: the separate peace. It costs 3 diplomatic points; …
   controls: <Prussia ▸>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Press Prussia]  [Ease Prussia]  [Drop Prussia]  [Press Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 78 / 100
   Turn 13 — Late March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   8,319
   Inf:
   82,557
   Cav:
   28,750
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Opening settlement review for Prussia
map: unchanged (113 labels)
```

```
#0245  click Back Out  ->  ok
  (clicked at (1455, 937))
view: <run>\frames\0245_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 78 / 100
   Turn 13 — Late March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Armistice Collapsed @(3351,64)]  [icon: Ney orders lost @(3393,64)]  [icon: Bernadotte arrived @(3435,64)]  [icon: Marshal Murat seeks an audience @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Bavaria Joins Offensive! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Prussia + Russia
   -4
   T:3
   controls: [Prussia + Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   8,319
   Inf:
   82,557
   Cav:
   28,750
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (113 labels)
```

```
#0246  type Murat, march to Dresden  ->  ok
  (typed and Enter)
view: <run>\frames\0246_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat begins march to Dresden. Route: Swabia → Franconia → Dresden. Cavalry charges through Lorraine -> Swabia. Murat: "Good. An army rots standing still."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   8,319
   Inf:
   82,557
   Cav:
   28,750
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, march to Dresden
   Murat begins march to Dresden. Route: Swabia → Franconia → Dresden. Cavalry charges through Lorraine -> Swabia. Murat: "Good. An army rots standing still."
   [3/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-51)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,558)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Kutuzov(2443,539)  Bennigsen(2498,505)  Hohenlohe(2099,127)  Yorck(2154,93)  Buxhowden(2666,496)  Ney(2379,0)  Murat(1871,455)  Deroy(1927,421)  Bernadotte(1079,761)  ?(811,816)  Castanos(811,782)  Armfelt(2066,16)  Amey(1691,591)  ?(2376,360)  375(2089,538)  2k(2470,651)  3k(2798,413)  25k(2126,239)  3k(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1660,304)  12k(1571,330)
```

```
#0247  type Bernadotte, march to Franconia  ->  ok
  (typed and Enter)
view: <run>\frames\0247_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte begins march to Franconia. Route: Limousin → Burgundy → Orleanais → Lorraine → Swabia → Franconia. Moves to Limousin. Bernadotte: "The roads will be scouted before each march, Sire."
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   1/5
   Admin:
   2/2
   Gold:
   8,319
   Inf:
   82,557
   Cav:
   28,750
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Posen): 6,744 troops, morale 0, neutral stance
   Davout (Silesia): 13,418 troops, morale 60, defensive stance
   Soult (Brandenburg): 8,407 troops, morale 23, neutral stance, retreating
   Murat (Nivernais): 22,944 troops, morale 68, neutral stance
   Bernadotte (Gascony): 31,687 troops, morale 32, neutral stance
   Massena (Posen): 14,635 troops, morale 26, neutral stance
   Napoleon (Posen): 5,375 troops, morale 50, neutral stance
   Amey (Bern): 3,500 troops, morale 100, neutral stance
   PRISONERS:
   Lannes: held by Prussia at Berlin since T13.
   CONFIRMED INTELLIGENCE:
   Kutuzov (Russia): 23,784 troops at Vienna, defensive stance, morale 100 — famed for 'The Old Fox'
   Bennigsen (Russia): 4,199 troops at Vienna, defensive stance, morale 100
   Vienna (Russia): garrison of 2,000 holds the works
   Podolia (Russia): garrison of 3,000 holds the works
   Hohenlohe (Prussia): 5,069 troops at Berlin, defensive stance, morale 10
   Yorck (Prussia): 3,794 troops at Berlin, neutral stance, morale 100
   Berlin (Prussia): garrison of 25,000 holds the works
   Buxhowden (Russia): 21,798 troops at Moravia, defensive stance, morale 100
   Brunswick (Prussia): 37,418 troops at Brandenburg, defensive stance, morale 99
   Armfelt (Sweden): 36,749 troops at Stralsund, defensive stance, morale 55
   RECENT REPORTS:
   Archduke Charles, Archduke John: substantial force near Carniola
   Deroy: substantial force near Swabia
   Castanos: small force near Bordelais
   NO INTELLIGENCE: No word from 66 provinces beyond the frontiers of Estonia, Volhynia, Albania, Aragon, Croatia, Rome, Ukraine, Norrland.
   Opening settlement review for Prussia
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
   ► Murat, march to Dresden
   Murat begins march to Dresden. Route: Swabia → Franconia → Dresden. Cavalry charges through Lorraine -> Swabia. Murat: "Good. An army rots standing still."
   [3/5 actions remaining]
   ► Bernadotte, march to Franconia
   Bernadotte begins march to Franconia. Route: Limousin → Burgundy → Orleanais → Lorraine → Swabia → Franconia. Moves to Limousin. Bernadotte: "The roads will be scouted before each march, Sire."
   [1/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-51)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,558)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2673,149)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Kutuzov(2443,539)  Bennigsen(2498,505)  Hohenlohe(2099,127)  Yorck(2154,93)  Buxhowden(2666,496)  Ney(2379,0)  Murat(1871,455)  Deroy(1927,421)  Bernadotte(1305,564)  ?(811,816)  Castanos(811,782)  Armfelt(2066,16)  Amey(1691,591)  ?(2376,360)  375(2089,538)  2k(2470,651)  3k(2798,413)  25k(2126,239)  3k(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1660,304)  12k(1571,330)
```

```
#0248  type Davout, move to Posen  ->  ok
  (typed and Enter)
view: <run>\frames\0248_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Silesia to Posen (134 lost to march)
East Prussia lies undefended — an attack takes it.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   0/5
   Admin:
   2/2
   Gold:
   8,319
   Inf:
   82,557
   Cav:
   28,750
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, move to Posen
   → Davout moves from Silesia to Posen (134 lost to march)
   East Prussia lies undefended — an attack takes it.
   [0/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-51)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,558)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Kutuzov(2443,539)  Bennigsen(2498,505)  Hohenlohe(2099,127)  Yorck(2154,93)  Buxhowden(2666,496)  Murat(1871,455)  Deroy(1927,421)  Bernadotte(1305,564)  ?(811,816)  Castanos(811,782)  Armfelt(2066,16)  Amey(1691,591)  ?(2376,360)  375(2089,538)  2k(2470,651)  3k(2798,413)  25k(2126,239)  3k(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  ?(1660,304)  12k(1571,330)
```

```
#0249  type recruit infantry for Bernadotte  ->  ok
  (typed and Enter)
view: <run>\frames\0249_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte recruits 3,000 infantry at Limousin (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
Infantry pool: 82,557 -> 79,557 [WARNING] Morale dropped to 32% — consider drilling before battle.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   0/5
   Admin:
   1/2
   Gold:
   7,719
   Inf:
   79,557
   Cav:
   28,750
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Limousin (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
   Infantry pool: 82,557 -> 79,557 [WARNING] Morale dropped to 32% — consider drilling before battle.
   [0/5 actions remaining]
map: unchanged (111 labels)
```

```
#0250  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0250_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 13
   RUSSIA / ──────────────────────────── / - Bennigsen attacks Bohemia /     Region captured: Bohemia (was France) (secured) /  / PRUSSIA / ──────────────────────────── / - Brunswick retreats to Berlin / - Brunswick changes stance to defensive /  / BAVARIA / ──────────────────────────── / - Deroy moves to Franconia / - Deroy holds position / - Deroy recruits troops / - Deroy recruits troops /  / ──── …
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 77 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   9,571
   Inf:
   81,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   NO INTELLIGENCE: No word from 66 provinces beyond the frontiers of Estonia, Volhynia, Albania, Aragon, Croatia, Rome, Ukraine, Norrland.
   Opening settlement review for Prussia
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
   ► Murat, march to Dresden
   Murat begins march to Dresden. Route: Swabia → Franconia → Dresden. Cavalry charges through Lorraine -> Swabia. Murat: "Good. An army rots standing still."
   [3/5 actions remaining]
   ► Bernadotte, march to Franconia
   Bernadotte begins march to Franconia. Route: Limousin → Burgundy → Orleanais → Lorraine → Swabia → Franconia. Moves to Limousin. Bernadotte: "The roads will be scouted before each march, Sire."
   [1/5 actions remaining]
   ► Davout, move to Posen
   → Davout moves from Silesia to Posen (134 lost to march)
   East Prussia lies undefended — an attack takes it.
   [0/5 actions remaining]
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Limousin (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
   Infantry pool: 82,557 -> 79,557 [WARNING] Morale dropped to 32% — consider drilling before battle.
   [0/5 actions remaining]
   ► end turn
   Your unratified settlement draft with Prussia (1 clause) was set aside at turn's end.
   ═══════════════════════════════════════
   TURN 14 BEGINS
   ═══════════════════════════════════════
   Income: 2698g | Occupation: -172g | Charges of Empire: -603g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Other: +1411g | Upkeep: -1072g | Net: +1852g | Spent: 600g
   Treasury: 9,571g
   Actions refreshed: 5/5
   Soult's army is recovering. Effectiveness penalty: -15%.
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   Crowded at Posen: Ney loses 202 troops to the press of 4 corps on one province's roads
   Crowded at Posen: Davout loses 398 troops to the press of 4 corps on one province's roads
   Crowded at Posen: Massena loses 439 troops to the press of 4 corps on one province's roads
   Crowded at Posen: Napoleon loses 161 troops to the press of 4 corps on one province's roads
   Garrison at Vienna reinforced: 2,000 -> 4,000
   Holland loyalty 62 (-2): satellite drift, relations with the lord
   A coalition is brewing! Britain, Austria, Ottoman, Sweden, Naples, Portugal, Saxony, Hanover, Hesse, Papal States, Sardinia are consulting.
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Murat's resentment of Ney has cooled with time.
   Bernadotte's resentment of Ney has cooled with time.
   Berthier notes that Davout's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   Lannes is no longer the army's most celebrated commander — the laurels have passed to Davout.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,558)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  ?(2798,303)  Buxhowden(2798,269)  Brunswick(2126,127)  ?(2666,499)  Kutuzov(2666,465)  Murat(1898,455)  Bernadotte(1305,564)  ?(811,816)  Castanos(811,782)  ?(2066,18)  Armfelt(2066,-16)  Amey(1691,591)  ?(2376,360)  375(2089,538)  4k(2470,651)  ?(2798,413)  25k(2126,239)  3k(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  12k(1571,330)
```

```
#0251  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0251_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   9,571
   Inf:
   81,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Buxhowden — Moravia — substantial force [stale - T11]
   Armfelt — Stralsund — substantial force [stale - T11]
   Bennigsen — Vienna — screening force [last known - T12]
   Yorck — Berlin — screening force [last known - T11]
   Vienna garrison — Vienna — garrison of 4,000 [confirmed]
   Podolia garrison — Podolia — garrison — screening force [stale - T11]
   Berlin garrison — Berlin — garrison of 25,000 [confirmed]
   TURN EVENTS
   Soult's army is recovering. Effectiveness penalty: -15%.
   Supply cost you 1,200 men, at Posen.
   Vienna's garrison regains 2,000: 2,000 -> 4,000.
   Holland loyalty 62 (-2): satellite drift, relations with the lord
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Murat's resentment of Ney has cooled with time.
   Bernadotte's resentment of Ney has cooled with time.
   Berthier notes that Davout's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   Lannes is no longer the army's most celebrated commander — the laurels have passed to Davout.
   PRISONERS OF WAR
   Lannes — held by Prussia since turn 13.
   DIPLOMATIC EVENTS
   THE LAWS: Austria enacts the Generalissimus — every levy costs 10% less (×0.9).
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand warns: a coalition may be forming against France.
   The court of Sweden takes up a new design: Scourge of the Usurper.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Prussia — Armistice Losing
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled (3 held, unsettled: Brandenburg, Posen, Silesia) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-9)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 77/100 [Brewing]
   Coalition forming in 3 turns!
   The courts consult now and declare on turn 17: Britain, Austria and 9 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Oudinot awaits a commission at 3,500g."
   ════════════════════════════════════
map: unchanged (113 labels)
```

```
#0252  click Envoys  ->  ok
  (clicked at (3397, 18))
view: <run>\frames\0252_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Armistice / Terms: /   - Proposal: Armistice / Assessment: GENEROUS /  / War Summary / War score: 3 ^ (Territory +15, Battle -12, Ticking -6) / Settlement: White Peace / Objective: Conquest - Berlin (inactive) / Ticking: +0 / Duration: 3 turns   Battles: 3W / 7L / Casualties: ours 20029 / theirs 25962 / We hold: Silesia, Posen, Branden …
   controls: [Accept]  [Counter]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   9,571
   Inf:
   81,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Coalition forming in 3 turns!
   The courts consult now and declare on turn 17: Britain, Austria and 9 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Oudinot awaits a commission at 3,500g."
   ════════════════════════════════════
map: unchanged (113 labels)
```

```
#0253  click Accept  ->  ok
  (clicked at (1604, 687))
view: <run>\frames\0253_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 77 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Coalition Brewing — 3 turns @(3351,64)]  [icon: Armistice Collapsed @(3393,64)]  [icon: Ney orders lost @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Bavaria Joins Offensive! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Russia
   -9
   T:2
   controls: [Russia]  [Prussia  5t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   9,571
   Inf:
   81,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: At War → Armistice with Prussia.
map: unchanged (113 labels)
```

```
#0254  click Diplomacy (D)  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0254_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 7/7
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  / How Europe Reads France /   Read as: The hegemon of Europe — 41% of the continent's weight. /   The courts believe he will go as far as an ultimatum (alarm 77). /   They think he is coming for Prussia — his corps stand against their soil. /  / Th …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Oudinot awaits a commission at 3,500g."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: At War → Armistice with Prussia.
map: unchanged (113 labels)
```

```
#0255  click THREAT & COALITION  ->  ok
  (clicked at (1670, 273))
view: <run>\frames\0255_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 7/7
   BALANCE OF EUROPE / ──────────────── / A coalition is brewing against French-led alignment. /  / COALITION THREAT / Threat Level: 77 / 100 — Brewing /   / Next war of conquest: 77 → 97 · brews at 60 (now) · forms at once at 80 (1) · dissolves below 20 /  / This Turn's Sources: /   • Hegemony Passive (+1) /   • Denied national designs (+1) /   • Natural threat decay (-3) /  / THE NEXT LEAGUE / The  …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [THREAT & COALITION](disabled: You are reading this book)  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Oudinot awaits a commission at 3,500g."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: At War → Armistice with Prussia.
map: unchanged (113 labels)
```

```
#0256  scroll 1828 600 down 5  ->  ok
  (scrolled down 5 at (1828, 600))
view: <run>\frames\0256_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Oudinot awaits a commission at 3,500g."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: At War → Armistice with Prussia.
map: unchanged (113 labels)
```

```
#0257  click_at 2655 236  ->  ok
  (clicked at (2655, 236) on BackgroundOverlay  (ColorRect, layer 50))
view: <run>\frames\0257_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Russia
   -9
   T:2
   controls: [Russia]  [Prussia  5t]
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Oudinot awaits a commission at 3,500g."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: At War → Armistice with Prussia.
map: unchanged (113 labels)
```

```
#0258  click ⚖ Diplomacy  ->  ok
  (clicked at (829, 978))
view: <run>\frames\0258_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   At War (1)
   Treaties (9)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 36 titled provinces — 45 are needed (9 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Russia  —  At War  |  -80 (Hostile)]  [Prussia  —  Armistice  |  -52 (Hostile)]  [Spain  —  Alliance  |  +12 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -22 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Oudinot awaits a commission at 3,500g."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: At War → Armistice with Prussia.
map: unchanged (113 labels)
```

```
#0259  scroll 1825 593 down 5  ->  ok
  (scrolled down 5 at (1825, 593))
view: <run>\frames\0259_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   controls: [icon: Close (Esc) @(2075,284)]  [Prussia  —  Armistice  |  -52 (Hostile)]  [Spain  —  Alliance  |  +12 (Neutral)]  [Ottoman Empire  —  Open Borders  |  -22 (Wary)]  [Portugal  —  Open Borders  |  -21 (Wary)]  [Denmark  —  Non-Aggression  |  -5 (Wary)]  [Bavaria  —  Alliance  |  +32 (Friendly)]  [Saxony  —  Open Borders  |  -21 (Wary)]  [Hesse  —  Non-Aggression  |  -11 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Oudinot awaits a commission at 3,500g."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: At War → Armistice with Prussia.
map: unchanged (113 labels)
```

```
#0260  click Saxony  ->  ok
  (clicked at (1825, 620))
view: <run>\frames\0260_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY — Saxony
   DP: 7
   TALLEYRAND'S ASSESSMENT — SAXONY / Status: Open Borders   Relation: -21 (Wary) /  / "Our borders with Saxony are open, but trust remains shallow. A non-aggression pact would formalize the thaw." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. /  / KEY FACTORS /   + Diplomatic skill advantage (+12) /   + Base wi …
   Relations with Saxony stand at -21; a Non-Aggression needs 0.
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Non-Aggression (1 DP)  —  Doubtful — may counter](disabled: Relations with Saxony stand at -21; a Non-Aggression needs 0.)  [Propose Vassal (3 DP)  —  Hopeless]  [Declare War (1 DP)]  [Break Treaty (1 DP)]  [Downgrade (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Oudinot awaits a commission at 3,500g."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: At War → Armistice with Prussia.
map: unchanged (113 labels)
```

```
#0261  click Cancel  ->  ok
  (clicked at (1884, 740))
view: <run>\frames\0261_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Oudinot awaits a commission at 3,500g."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: At War → Armistice with Prussia.
map: unchanged (113 labels)
```

```
#0262  type Talleyrand, improve relations with Saxony  ->  ok
  (typed and Enter)
view: <run>\frames\0262_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Talleyrand, improve relations with Saxony
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
map: unchanged (113 labels)
```

```
#0263  type Davout, move to Dresden  ->  ok
  (typed and Enter)
view: <run>\frames\0263_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Posen to Dresden (167 lost to march)
Bohemia, Vienna lie undefended — an attack takes any of them.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/5
   Admin:
   2/2
   Gold:
   9,571
   Inf:
   81,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, move to Dresden
   → Davout moves from Posen to Dresden (167 lost to march)
   Bohemia, Vienna lie undefended — an attack takes any of them.
   [4/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,558)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2376,248)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  ?(2798,303)  Buxhowden(2798,269)  Brunswick(2126,127)  ?(2666,499)  Kutuzov(2666,465)  Ney(2379,0)  Murat(1898,455)  Bernadotte(1305,564)  ?(811,816)  Castanos(811,782)  ?(2066,18)  Armfelt(2066,-16)  Amey(1691,591)  10k(2376,360)  375(2089,538)  4k(2470,651)  ?(2798,413)  25k(2126,239)  3k(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  12k(1571,330)
```

```
#0264  type Massena, move to Dresden  ->  ok
  (typed and Enter)
view: <run>\frames\0264_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Massena moves from Posen to Dresden (184 lost to march)
Bohemia, Vienna lie undefended — an attack takes any of them.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   9,571
   Inf:
   81,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, move to Dresden
   → Massena moves from Posen to Dresden (184 lost to march)
   Bohemia, Vienna lie undefended — an attack takes any of them.
   [3/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,558)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2348,248)  Massena(2405,214)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  ?(2798,303)  Buxhowden(2798,269)  Brunswick(2126,127)  ?(2666,499)  Kutuzov(2666,465)  Ney(2379,0)  Murat(1898,455)  Bernadotte(1305,564)  ?(811,816)  Castanos(811,782)  ?(2066,18)  Armfelt(2066,-16)  Amey(1691,591)  10k(2376,360)  375(2089,538)  4k(2470,651)  ?(2798,413)  25k(2126,239)  3k(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  12k(1571,330)
```

```
#0265  type Davout, retake Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0265_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['objection'], region_panel=no
reply: ok Davout firmly objects: 'Sire, the enemy is too strong. We need reinforcements.' (Trust him and he will fortify current position instead.)
── ObjectionDialog (layer 108) ──
   DAVOUT'S CONCERN
   "Davout firmly objects: 'Sire, the enemy is too strong. We need reinforcements.' (Trust him and he will fortify current position instead.)"
   Personality: Cautious
   Trust: 74 (Reliable)
   Track record: Neutral
   Authority: 80
   controls: [Trust Davout: fortify current position (+5 trust)]  [Proceed as Ordered (-10 trust)]  [Compromise: defend at Dresden (+3 trust)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 77 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   9,571
   Inf:
   81,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Berthier notes that Davout's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   Lannes is no longer the army's most celebrated commander — the laurels have passed to Davout.
   PRISONERS OF WAR
   Lannes — held by Prussia since turn 13.
   DIPLOMATIC EVENTS
   THE LAWS: Austria enacts the Generalissimus — every levy costs 10% less (×0.9).
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand warns: a coalition may be forming against France.
   The court of Sweden takes up a new design: Scourge of the Usurper.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Prussia — Armistice Losing
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 36 of 45 titled (3 held, unsettled: Brandenburg, Posen, Silesia) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-9)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 77/100 [Brewing]
   Coalition forming in 3 turns!
   The courts consult now and declare on turn 17: Britain, Austria and 9 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Oudinot awaits a commission at 3,500g."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: At War → Armistice with Prussia.
   ► Talleyrand, improve relations with Saxony
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
   ► Davout, move to Dresden
   → Davout moves from Posen to Dresden (167 lost to march)
   Bohemia, Vienna lie undefended — an attack takes any of them.
   [4/5 actions remaining]
   ► Massena, move to Dresden
   → Massena moves from Posen to Dresden (184 lost to march)
   Bohemia, Vienna lie undefended — an attack takes any of them.
   [3/5 actions remaining]
   ► Davout, retake Vienna
   ⚠ Marshal Davout raises concerns...
map: unchanged (115 labels)
```

```
#0266  click Compromise  ->  ok
  (clicked at (2101, 618))
view: <run>\frames\0266_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 77 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Coalition Brewing — 3 turns @(3351,64)]  [icon: Armistice Collapsed @(3393,64)]  [icon: Ney orders lost @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Bavaria Joins Offensive! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Russia
   -9
   T:2
   controls: [Russia]  [Prussia  5t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   9,571
   Inf:
   81,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► You seek a middle ground with your marshal.
   You find middle ground with Davout.
   Davout executes the compromise plan.
   Davout fortifies position at Dresden. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
   [2/5 actions remaining]
map: unchanged (115 labels)
```

```
#0267  type Massena, retake Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0267_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok The last 4,000 of the garrison at Vienna give way. Massena marches from Dresden into Vienna unopposed! (140 lost to march) Captured: Russia → France
Your forces have taken Vienna. Plunder it for 1,200 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Massena has taken Vienna
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+1,200 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 79 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   1/5
   Admin:
   2/2
   Gold:
   9,571
   Inf:
   81,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Massena, retake Vienna
   ⚑ The last 4,000 of the garrison at Vienna give way. Massena marches from Dresden into Vienna unopposed! (140 lost to march) Captured: Russia → France
   Your forces have taken Vienna. Plunder it for 1,200 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [1/5 actions remaining]
   Your forces await orders: Plunder or Secure?
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,558)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2376,248)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Massena(2471,539)  ?(2798,303)  Buxhowden(2798,269)  Brunswick(2126,127)  ?(2666,499)  Kutuzov(2666,465)  Ney(2379,0)  Murat(1898,455)  Bernadotte(1305,564)  ?(811,816)  Castanos(811,782)  ?(2066,18)  Armfelt(2066,-16)  Amey(1691,591)  10k(2376,360)  375(2089,538)  ?(2798,413)  25k(2126,239)  3k(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  12k(1571,330)
```

```
#0268  click SECURE  ->  ok
  (clicked at (2000, 598))
view: <run>\frames\0268_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 79 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Coalition Brewing — 3 turns @(3351,64)]  [icon: Armistice Collapsed @(3393,64)]  [icon: Ney orders lost @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Bavaria Joins Offensive! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Russia
   -7
   T:2
   controls: [Russia]  [Prussia  5t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   1/5
   Admin:
   2/2
   Gold:
   9,571
   Inf:
   81,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   You order your troops to secure the region.
   Massena secures Vienna. Stability set to 25. Order is maintained.
map: unchanged (113 labels)
```

```
#0269  type Massena, move to Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0269_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok Massena moves from Vienna to Bohemia. Bohemia falls to France! (was Russia) (138 lost to march)
Your forces have taken Bohemia. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Massena has taken Bohemia
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+800 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 81 / 100
   Turn 14 — Early April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   0/5
   Admin:
   2/2
   Gold:
   9,571
   Inf:
   81,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-9)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 77/100 [Brewing]
   Coalition forming in 3 turns!
   The courts consult now and declare on turn 17: Britain, Austria and 9 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Oudinot awaits a commission at 3,500g."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: At War → Armistice with Prussia.
   ► Talleyrand, improve relations with Saxony
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
   ► Davout, move to Dresden
   → Davout moves from Posen to Dresden (167 lost to march)
   Bohemia, Vienna lie undefended — an attack takes any of them.
   [4/5 actions remaining]
   ► Massena, move to Dresden
   → Massena moves from Posen to Dresden (184 lost to march)
   Bohemia, Vienna lie undefended — an attack takes any of them.
   [3/5 actions remaining]
   ► Davout, retake Vienna
   ⚠ Marshal Davout raises concerns...
   ► You seek a middle ground with your marshal.
   You find middle ground with Davout.
   Davout executes the compromise plan.
   Davout fortifies position at Dresden. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
   [2/5 actions remaining]
   ► Massena, retake Vienna
   ⚑ The last 4,000 of the garrison at Vienna give way. Massena marches from Dresden into Vienna unopposed! (140 lost to march) Captured: Russia → France
   Your forces have taken Vienna. Plunder it for 1,200 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [1/5 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Massena secures Vienna. Stability set to 25. Order is maintained.
   ► Massena, move to Bohemia
   → Massena moves from Vienna to Bohemia. Bohemia falls to France! (was Russia) (138 lost to march)
   Your forces have taken Bohemia. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [0/5 actions remaining]
   Your forces await orders: Plunder or Secure?
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,558)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2376,248)  Massena(2277,485)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  ?(2798,303)  Buxhowden(2798,269)  Brunswick(2126,127)  ?(2666,499)  Kutuzov(2666,465)  ?(2519,711)  Bennigsen(2519,677)  Ney(2379,0)  Murat(1898,455)  Bernadotte(1305,564)  ?(811,816)  Castanos(811,782)  ?(2066,18)  Armfelt(2066,-16)  Amey(1691,591)  10k(2376,360)  375(2089,538)  ?(2798,413)  25k(2126,239)  3k(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  12k(1571,330)
```

```
#0270  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0270_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 81 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Coalition Brewing — 3 turns @(3351,64)]  [icon: Armistice Collapsed @(3393,64)]  [icon: Ney orders lost @(3435,64)]  [icon: Bernadotte arrived @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: Bavaria Joins Offensive! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Russia
   -5
   T:2
   controls: [Russia]  [Prussia  5t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   0/5
   Admin:
   2/2
   Gold:
   9,571
   Inf:
   81,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   You order your troops to secure the region.
   Massena secures Bohemia. Stability set to 25. Order is maintained.
map: unchanged (115 labels)
```

```
#0271  type recruit infantry for Bernadotte  ->  ok
  (typed and Enter)
view: <run>\frames\0271_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Bernadotte recruits 3,000 infantry at Limousin (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
Infantry pool: 81,457 -> 78,457 [WARNING] Morale dropped to 32% — consider drilling before battle.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   0/5
   Admin:
   1/2
   Gold:
   8,971
   Inf:
   78,457
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Limousin (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
   Infantry pool: 81,457 -> 78,457 [WARNING] Morale dropped to 32% — consider drilling before battle.
   [0/5 actions remaining]
map: unchanged (115 labels)
```

```
#0272  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0272_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 14
   RUSSIA / ──────────────────────────── / - Buxhowden attacks Davout /     Second Battle of Dresden /     Buxhowden: 1,582 casualties, 23,216 remaining /     Davout: 1,512 casualties, 11,207 remaining /     Result: Bloody stalemate /     ⚔ View the field /     Fort degraded: 7% -> 2% /     --- Berthier's Report --- /     Attack: Buxhowden (Defensive stance -10%) /     Defense: Davout (Defensive stan …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 80 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   10,623
   Inf:
   80,244
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [1/5 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Massena secures Vienna. Stability set to 25. Order is maintained.
   ► Massena, move to Bohemia
   → Massena moves from Vienna to Bohemia. Bohemia falls to France! (was Russia) (138 lost to march)
   Your forces have taken Bohemia. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [0/5 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Massena secures Bohemia. Stability set to 25. Order is maintained.
   ► recruit infantry for Bernadotte
   + Bernadotte recruits 3,000 infantry at Limousin (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 32%
   Infantry pool: 81,457 -> 78,457 [WARNING] Morale dropped to 32% — consider drilling before battle.
   [0/5 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 15 BEGINS
   ═══════════════════════════════════════
   Income: 2963g | Requisitions: +75g | Occupation: -280g | Charges of Empire: -756g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Blockade: -289g | Materiel: -170g | Other: +1311g | Upkeep: -792g | Net: +1652g | Spent: 600g
   Treasury: 10,623g
   Actions refreshed: 5/5
   Davout's resolve hardens behind his earthworks (1/3) — his next assault will strike +8% harder. (Iron Resolve)
   Davout's fortifications strengthen: +3% defense (max 12%)
   Soult's army has fully recovered and is combat ready.
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Burgundy: Bernadotte loses 381 troops
   Garrison at Vienna reinforced: 0 -> 2,000
   Garrison at Berlin reinforced: 0 -> 2,000
   Holland loyalty 56 (-6): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them. Holland is no longer a willing ally, Sire — it has lost the standing to petition you until its loyalty is mended.
   Kingdom of Italy loyalty 84 (-4): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 77 (-4): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Amey's contingent comes home — 3,500 of 3,500 men.
   The Fourth British Coalition declared! (Instant — threat 80)
   Berthier reports that Murat resents Ney's laurels for the third time — he has grown restless for glory.
   The rivalry between Murat and Ney has become entrenched. The wound will not close on its own.
   Berthier reports that Bernadotte resents Ney's laurels again, 3 turns after the last — he has grown quiet in the way the staff have learned to read.
   Berthier: Enemy forces spotted near Vienna! Kutuzov (22,426 troops) at Moravia.
   Berthier: Enemy forces spotted near Vienna! Buxhowden (22,835 troops) at Moravia.
   Berthier: Enemy forces spotted near Vienna! Bennigsen (4,117 troops) at Hungary.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2348,248)  Murat(2404,214)  Massena(2277,485)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Deroy(2127,127)  ?(2648,499)  Kutuzov(2648,465)  ?(2684,499)  Buxhowden(2684,431)  ?(2519,711)  Bennigsen(2519,677)  Ney(2379,0)  ?(811,816)  Castanos(811,782)  Bernadotte(1499,526)  ?(2066,18)  Armfelt(2066,-16)  10k(2376,360)  375(2089,538)  2k(2470,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)
```

```
#0273  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0273_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   RUSSIA LOSSES
   0
   0
   ⚔
   Davout ◆
   Buxhowden ◆
   12,719 → 11,207
   24,798 → 23,216
   Ney — could not reach the field
   Massena — could not reach the field
   SECOND BATTLE OF DRESDEN
   click anywhere to skip ▸
   DRESDEN · TURN 14
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   BLOCKADE: Britain closes Spain's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
   THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
   THE STRAIT: the London–Normandy crossing is shut — Britain commands the water.
   THE LAWS: Prussia cannot pay for the Articles of War — the law lapses.
   The court of Prussia takes up a new design: its own survival.
   Relations with Britain have worsened significantly (-29 this turn).
   Relations with Austria have worsened significantly (-29 this turn).
   Relations with the Ottoman Empire have worsened significantly (-29 this turn).
   Relations with Sweden have worsened significantly (-29 this turn).
   Relations with Naples have worsened significantly (-29 this turn).
   Relations with Portugal have worsened significantly (-29 this turn).
   Relations with Saxony have worsened significantly (-29 this turn).
   Relations with Hanover have worsened significantly (-29 this turn).
   Relations with the Papal States have worsened significantly (-29 this turn).
   Relations with Sardinia have worsened significantly (-29 this turn).
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Kingdom of Italy — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (6 held, unsettled: Bohemia, Brandenburg, Posen …) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-8)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Ottoman — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sweden — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Naples — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 80/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
map: unchanged (117 labels)
```

```
#0274  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Davout ◆' (Control, layer 121))
view: <run>\frames\0274_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   A BLOODY STALEMATE
   FRANCE LOSSES
   RUSSIA LOSSES
   1,512
   1,582
   ⚔
   Davout ◆
   Buxhowden ◆
   12,719 → 11,207
   24,798 → 23,216
   Ney — could not reach the field
   Massena — could not reach the field
   Berthier: “The Emperor watched this field. Davout stood alone, Sire. Ney, Massena and Napoleon never came.” / Buxhowden: "Both lines remain. The report writes itself."
   SECOND BATTLE OF DRESDEN
   DRESDEN · TURN 14
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 80/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
map: unchanged (117 labels)
```

```
#0275  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0275_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114) ──
   MURAT — A rivalry among the marshals
   "I ask once more, Sire. A command. Any command." /  / Sire, Murat has refused to attend council where Ney is present. The breach may be beyond repair.
   Free. 80% they settle into cold war; 20% the hotter head turns openly discontent — -3 trust, and his defiance cooldown lifts at once.
   A public gamble. 30% the breach eases to a rivalry, 50% nothing, 20% it costs you 3 authority.
   controls: [Accept the Breach]  [Force Reconciliation   [2 AP]]  [Separate Them]  [Later (he will return)]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 80/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
map: unchanged (117 labels)
```

```
#0276  click Envoys  ->  ERROR: no visible control's text holds "Envoys"
view: <run>\frames\0276_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 80/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
map: unchanged (117 labels)
```

```
#0277  click Separate Them  ->  ok
  (clicked at (1825, 660))
view: <run>\frames\0277_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Marescalchi (Loyalist) of Kingdom of Italy /  / The petition: /   - Grant it, and Bohemia passes to the Kingdom of Italy: loyalty +11, its bond with us rises 5 → 25 (worth +1 a turn in loyalty, now +0), for 1 DP. Our net rises by 58g a turn — 50g of income forfeited, 70g of occupation relieved, 38g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cos …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Murat and Ney: Noted. Berthier will warn you whenever their commands stand together.
map: unchanged (117 labels)
```

```
#0278  click Not Now  ->  ok
  (clicked at (1979, 687))
view: <run>\frames\0278_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   10,623
   Inf:
   80,244
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Setting aside Kingdom of Italy's proposal. Click the envoy badge to revisit.
map: unchanged (117 labels)
```

```
#0279  type status  ->  ok
  (typed and Enter)
view: <run>\frames\0279_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok === BERTHIER'S INTELLIGENCE REPORT ===

YOUR FORCES:
  Ney (Posen): 6,542 troops, morale 0, neutral stance
  Davout (Dresden): 9,290 troops, morale 38, defensive stance
  Soult (Brandenburg): 8,407 troops, morale 23, neutral stance
  Murat (Dresden): 21,168 troops, morale 68, neutral stance
  Bernadotte (Burgundy): 37,306 troops, morale 32, neutral stance, [MOVE_TO]
  Massena (Bohemia): 13,734 troops, morale 26, neutral stance
  Napoleon (Posen): 5,214 troops, morale 50, neutral stance

PRISONERS:
  Lannes: held by Prussia at Berlin since T13.

CONFIRMED INTELLIGENCE:
  Dresden (Saxony): garrison of 10,000 holds the works
  Deroy (Bavaria): 18,113 troops at Berlin, defensive stance, morale 92

RECENT REPORTS:
  Archduke Charles, Archduke John: large force near Carniola
  Podolia (Russia): garrison — screening force holds the works
  Kutuzov, Buxhowden: large force near Moravia
  Bennigsen: screening force near Hungary
  Castanos: small force near Bordelais
  Armfelt: substantial force near Stralsund [4 turns ago]

NO INTELLIGENCE: No word from 66 provinces beyond the frontiers of Estonia, Volhynia, Albania, Aragon, Croatia, Rome, Ukraine, Norrland.

── TopBar (layer 75) ──
   DP: 7/7
   Threat 80 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Coalition Brewing — 3 turns @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Ney orders lost @(3477,64)]  [icon: Davout — free attack! @(3519,64)]  [icon: Petition from the Kingdom of Italy @(3561,64)]  [+43]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +40
   T:0
   Russia
   -8
   T:3
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  4t]
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Posen): 6,542 troops, morale 0, neutral stance
   Davout (Dresden): 9,290 troops, morale 38, defensive stance
   Soult (Brandenburg): 8,407 troops, morale 23, neutral stance
   Murat (Dresden): 21,168 troops, morale 68, neutral stance
   Bernadotte (Burgundy): 37,306 troops, morale 32, neutral stance, [MOVE_TO]
   Massena (Bohemia): 13,734 troops, morale 26, neutral stance
   Napoleon (Posen): 5,214 troops, morale 50, neutral stance
   PRISONERS:
   Lannes: held by Prussia at Berlin since T13.
   CONFIRMED INTELLIGENCE:
   Dresden (Saxony): garrison of 10,000 holds the works
   Deroy (Bavaria): 18,113 troops at Berlin, defensive stance, morale 92
   RECENT REPORTS:
   Archduke Charles, Archduke John: large force near Carniola
   Podolia (Russia): garrison — screening force holds the works
   Kutuzov, Buxhowden: large force near Moravia
   Bennigsen: screening force near Hungary
   Castanos: small force near Bordelais
   Armfelt: substantial force near Stralsund [4 turns ago]
   NO INTELLIGENCE: No word from 66 provinces beyond the frontiers of Estonia, Volhynia, Albania, Aragon, Croatia, Rome, Ukraine, Norrland.
map: unchanged (117 labels)
```

```
#0280  type Davout, unfortify  ->  ok
  (typed and Enter)
view: <run>\frames\0280_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, unfortify
   Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
map: unchanged (117 labels)
```

```
#0281  type Davout, move to Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0281_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Dresden to Vienna (92 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/5
   Admin:
   2/2
   Gold:
   10,623
   Inf:
   80,244
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, move to Vienna
   → Davout moves from Dresden to Vienna (92 lost to march)
   [4/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Murat(2376,248)  Massena(2277,485)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2470,539)  Deroy(2127,127)  ?(2648,499)  Kutuzov(2648,465)  ?(2684,499)  Buxhowden(2684,431)  ?(2519,711)  Bennigsen(2519,677)  Ney(2379,0)  ?(811,816)  Castanos(811,782)  Bernadotte(1499,526)  ?(2066,18)  Armfelt(2066,-16)  10k(2376,360)  375(2089,538)  2k(2470,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)
```

```
#0282  type Murat, move to Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0282_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat moves from Dresden to Vienna (261 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +30
   T:0
   Russia
   -8
   T:3
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  4t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   10,623
   Inf:
   80,244
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, move to Vienna
   → Murat moves from Dresden to Vienna (261 lost to march)
   [3/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Massena(2277,485)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Murat(2498,505)  Deroy(2127,127)  ?(2648,499)  Kutuzov(2648,465)  ?(2684,499)  Buxhowden(2684,431)  ?(2519,711)  Bennigsen(2519,677)  Ney(2379,0)  ?(811,816)  Castanos(811,782)  Bernadotte(1499,526)  ?(2066,18)  Armfelt(2066,-16)  10k(2376,360)  375(2089,538)  2k(2470,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)
```

```
#0283  type Napoleon, move to Silesia  ->  ok
  (typed and Enter)
view: <run>\frames\0283_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon moves from Posen to Silesia (52 lost to march)
Lithuania, Samogitia lie undefended — an attack takes any of them.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   10,623
   Inf:
   80,244
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "Men remember being raised, Sire, and they remember being left."
   ════════════════════════════════════
   Murat and Ney: Noted. Berthier will warn you whenever their commands stand together.
   Setting aside Kingdom of Italy's proposal. Click the envoy badge to revisit.
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Ney (Posen): 6,542 troops, morale 0, neutral stance
   Davout (Dresden): 9,290 troops, morale 38, defensive stance
   Soult (Brandenburg): 8,407 troops, morale 23, neutral stance
   Murat (Dresden): 21,168 troops, morale 68, neutral stance
   Bernadotte (Burgundy): 37,306 troops, morale 32, neutral stance, [MOVE_TO]
   Massena (Bohemia): 13,734 troops, morale 26, neutral stance
   Napoleon (Posen): 5,214 troops, morale 50, neutral stance
   PRISONERS:
   Lannes: held by Prussia at Berlin since T13.
   CONFIRMED INTELLIGENCE:
   Dresden (Saxony): garrison of 10,000 holds the works
   Deroy (Bavaria): 18,113 troops at Berlin, defensive stance, morale 92
   RECENT REPORTS:
   Archduke Charles, Archduke John: large force near Carniola
   Podolia (Russia): garrison — screening force holds the works
   Kutuzov, Buxhowden: large force near Moravia
   Bennigsen: screening force near Hungary
   Castanos: small force near Bordelais
   Armfelt: substantial force near Stralsund [4 turns ago]
   NO INTELLIGENCE: No word from 66 provinces beyond the frontiers of Estonia, Volhynia, Albania, Aragon, Croatia, Rome, Ukraine, Norrland.
   ► Davout, unfortify
   Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
   ► Davout, move to Vienna
   → Davout moves from Dresden to Vienna (92 lost to march)
   [4/5 actions remaining]
   ► Murat, move to Vienna
   → Murat moves from Dresden to Vienna (261 lost to march)
   [3/5 actions remaining]
   ► Napoleon, move to Silesia
   → Napoleon moves from Posen to Silesia (52 lost to march)
   Lithuania, Samogitia lie undefended — an attack takes any of them.
   [2/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Napoleon(2673,149)  Massena(2277,485)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Murat(2498,505)  Deroy(2127,127)  ?(2648,499)  Kutuzov(2648,465)  ?(2684,499)  Buxhowden(2684,431)  ?(2519,711)  Bennigsen(2519,677)  Ney(2407,0)  ?(811,816)  Castanos(811,782)  Bernadotte(1499,526)  ?(2066,18)  Armfelt(2066,-16)  10k(2376,360)  375(2089,538)  2k(2470,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)
```

```
#0284  type Ney, move to Silesia  ->  ok
  (typed and Enter)
view: <run>\frames\0284_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney moves from Posen to Silesia (65 lost to march)
Lithuania, Samogitia lie undefended — an attack takes any of them.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   1/5
   Admin:
   2/2
   Gold:
   10,623
   Inf:
   80,244
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, move to Silesia
   → Ney moves from Posen to Silesia (65 lost to march)
   Lithuania, Samogitia lie undefended — an attack takes any of them.
   [1/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Ney(2645,149)  Napoleon(2701,115)  Massena(2277,485)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Murat(2498,505)  Deroy(2127,127)  ?(2648,499)  Kutuzov(2648,465)  ?(2684,499)  Buxhowden(2684,431)  ?(2519,711)  Bennigsen(2519,677)  ?(811,816)  Castanos(811,782)  Bernadotte(1499,526)  ?(2066,18)  Armfelt(2066,-16)  10k(2376,360)  375(2089,538)  2k(2470,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)
```

```
#0285  type Ney, move to Lithuania  ->  ok
  (typed and Enter)
view: <run>\frames\0285_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok Ney moves from Silesia to Lithuania. Lithuania falls to France! (was Russia) (64 lost to march)
Volhynia, Samogitia, Ukraine lie undefended — an attack takes any of them.
Your forces have taken Lithuania. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Ney has taken Lithuania
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+800 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 82 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   0/5
   Admin:
   2/2
   Gold:
   10,623
   Inf:
   80,244
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Ney, move to Lithuania
   → Ney moves from Silesia to Lithuania. Lithuania falls to France! (was Russia) (64 lost to march)
   Volhynia, Samogitia, Ukraine lie undefended — an attack takes any of them.
   Your forces have taken Lithuania. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [0/5 actions remaining]
   Your forces await orders: Plunder or Secure?
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Gelderland(1789,256)  Champagne(1416,432)  Paris(1294,458)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Napoleon(2673,149)  Ney(2925,69)  Massena(2277,485)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Murat(2498,505)  Deroy(2127,127)  ?(2648,499)  Kutuzov(2648,465)  ?(2684,499)  Buxhowden(2684,431)  ?(2519,711)  Bennigsen(2519,677)  ?(811,816)  Castanos(811,782)  Bernadotte(1499,526)  ?(2066,18)  Armfelt(2066,-16)  10k(2376,360)  375(2089,538)  2k(2470,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)
```

```
#0286  click PLUNDER  ->  ok
  (clicked at (1653, 598))
view: <run>\frames\0286_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 82 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Coalition Brewing — 3 turns @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Ney orders lost @(3477,64)]  [icon: Davout — free attack! @(3519,64)]  [icon: Petition from the Kingdom of Italy @(3561,64)]  [+43]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +30
   T:0
   Russia
   -1
   T:3
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  4t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   0/5
   Admin:
   2/2
   Gold:
   11,423
   Inf:
   80,244
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   You order your troops to plunder the region!
   Ney's troops plunder Lithuania! Gained 800 gold. Buildings destroyed. Stability set to 10.
map: unchanged (117 labels)
```

```
#0287  click Generals  ->  ok
  (clicked at (219, 18))
view: <run>\frames\0287_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) ──
   GENERALS
   Your marshals — loyalty, glory, and grievance. Gold answers loyalty; only glory answers envy. Press G to close. /  / A PRISONER — Lannes: PRISONER of Prussia since T13. /   / [4] Lannes  [Infantry]  France / V Corps - crossed at Kehl on September 25, pressing the Black Forest feint. / Aggressive: +15% attack, +5% more in aggressive stance. Fortify capped at 10%. Grows restless if idle too long. /  …
   controls: [Pin]  [icon @(2213,236)]  <Commission a Marshal…>  <Reward — estate or rente…>  <Reward — estate or rente…>
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/5 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to plunder the region!
   Ney's troops plunder Lithuania! Gained 800 gold. Buildings destroyed. Stability set to 10.
map: unchanged (117 labels)
```

```
#0288  click Commission a Marshal  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0288_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) ──
   GENERALS
   ← Back to the Marshalate   /  /   COMMISSION A MARSHAL / Treasury: 11,423g | Pools: 80,244 foot · 30,000 horse · 18,400 guns | A commission raises his corps at the capital from his own arm's pool (1 admin AP + the candidate's price). /  /   / Mortier  [Cautious]  [Infantry] a corps of 5,000 foot  4,000g / Edouard Mortier - steady, imperturbable, and universally liked - one of the few marshals who  …
   controls: [Pin]  [icon @(2213,236)]  <← Back to the Marshalate>  <Commission Mortier — 4,000g>  <Commission Grouchy — 4,500g>  <Commission Suchet — 5,500g>  <Commission Oudinot — 3,500g>  <Commission Augereau — 3,500g>  <Commission Marmont — 4,500g>  <Commission Senarmont — 4,500g>
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/5 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to plunder the region!
   Ney's troops plunder Lithuania! Gained 800 gold. Buildings destroyed. Stability set to 10.
map: unchanged (117 labels)
```

```
#0289  click Commission Oudinot  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0289_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 82 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Coalition Brewing — 3 turns @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Ney orders lost @(3477,64)]  [icon: Davout — free attack! @(3519,64)]  [icon: Petition from the Kingdom of Italy @(3561,64)]  [+44]
── MarshalManagement (layer 50) ──
   GENERALS
   ← Back to the Marshalate   /  /   COMMISSION A MARSHAL / Treasury: 7,923g | Pools: 75,244 foot · 30,000 horse · 18,400 guns | A commission raises his corps at the capital from his own arm's pool (1 admin AP + the candidate's price). /  /   / Mortier  [Cautious]  [Infantry] a corps of 5,000 foot  4,000g / Edouard Mortier - steady, imperturbable, and universally liked - one of the few marshals who h …
   controls: [Pin]  [icon @(2213,236)]  <← Back to the Marshalate>  <Commission Mortier — 4,000g>  <Commission Grouchy — 4,500g>  <Commission Suchet — 5,500g>  <Commission Augereau — 3,500g>  <Commission Marmont — 4,500g>  <Commission Senarmont — 4,500g>
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   0/5
   Admin:
   1/2
   Gold:
   7,923
   Inf:
   75,244
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   PRISONERS:
   Lannes: held by Prussia at Berlin since T13.
   CONFIRMED INTELLIGENCE:
   Dresden (Saxony): garrison of 10,000 holds the works
   Deroy (Bavaria): 18,113 troops at Berlin, defensive stance, morale 92
   RECENT REPORTS:
   Archduke Charles, Archduke John: large force near Carniola
   Podolia (Russia): garrison — screening force holds the works
   Kutuzov, Buxhowden: large force near Moravia
   Bennigsen: screening force near Hungary
   Castanos: small force near Bordelais
   Armfelt: substantial force near Stralsund [4 turns ago]
   NO INTELLIGENCE: No word from 66 provinces beyond the frontiers of Estonia, Volhynia, Albania, Aragon, Croatia, Rome, Ukraine, Norrland.
   ► Davout, unfortify
   Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
   ► Davout, move to Vienna
   → Davout moves from Dresden to Vienna (92 lost to march)
   [4/5 actions remaining]
   ► Murat, move to Vienna
   → Murat moves from Dresden to Vienna (261 lost to march)
   [3/5 actions remaining]
   ► Napoleon, move to Silesia
   → Napoleon moves from Posen to Silesia (52 lost to march)
   Lithuania, Samogitia lie undefended — an attack takes any of them.
   [2/5 actions remaining]
   ► Ney, move to Silesia
   → Ney moves from Posen to Silesia (65 lost to march)
   Lithuania, Samogitia lie undefended — an attack takes any of them.
   [1/5 actions remaining]
   ► Ney, move to Lithuania
   → Ney moves from Silesia to Lithuania. Lithuania falls to France! (was Russia) (64 lost to march)
   Volhynia, Samogitia, Ukraine lie undefended — an attack takes any of them.
   Your forces have taken Lithuania. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [0/5 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to plunder the region!
   Ney's troops plunder Lithuania! Gained 800 gold. Buildings destroyed. Stability set to 10.
   ► commission Oudinot
   Marshal Oudinot accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Lannes (Friendly).
   [0/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Napoleon(2673,149)  Ney(2925,69)  Massena(2277,485)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Murat(2498,505)  Deroy(2127,127)  ?(2648,499)  Kutuzov(2648,465)  ?(2684,499)  Buxhowden(2684,431)  ?(2519,711)  Bennigsen(2519,677)  ?(811,816)  Castanos(811,782)  Bernadotte(1499,526)  Oudinot(1295,404)  ?(2066,18)  Armfelt(2066,-16)  10k(2376,360)  375(2089,538)  2k(2470,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)
```

```
#0290  click Commission Augereau  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0290_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50) ──
   GENERALS
   ← Back to the Marshalate   /  /   COMMISSION A MARSHAL / Treasury: 4,423g | Pools: 70,244 foot · 30,000 horse · 18,400 guns | A commission raises his corps at the capital from his own arm's pool (1 admin AP + the candidate's price). /  /   / Mortier  [Cautious]  [Infantry] a corps of 5,000 foot  4,000g / Edouard Mortier - steady, imperturbable, and universally liked - one of the few marshals who h …
   controls: [Pin]  [icon @(2213,236)]  <← Back to the Marshalate>  <Commission Mortier — 4,000g>
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   0/5
   Admin:
   0/2
   Gold:
   4,423
   Inf:
   70,244
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E) ▸]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► commission Augereau
   Marshal Augereau accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Massena (Friendly). That was the last order the day could take, Sire — the turn ends when you say so.
   [0/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  Amsterdam(1660,247)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,179)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Milan(2015,797)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Napoleon(2673,149)  Ney(2925,69)  Massena(2277,485)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2442,539)  Murat(2498,505)  Deroy(2127,127)  ?(2648,499)  Kutuzov(2648,465)  ?(2684,499)  Buxhowden(2684,431)  ?(2519,711)  Bennigsen(2519,677)  ?(811,816)  Castanos(811,782)  Bernadotte(1499,526)  Oudinot(1267,404)  Augereau(1323,370)  ?(2066,18)  Armfelt(2066,-16)  10k(2376,360)  375(2089,538)  2k(2470,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,730)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  12k(1571,330)
```

```
#0291  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0291_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=['generals'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── MarshalManagement (layer 50): unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   [0/5 actions remaining]
   ► commission Augereau
   Marshal Augereau accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Massena (Friendly). That was the last order the day could take, Sire — the turn ends when you say so.
   [0/5 actions remaining]
map: unchanged (118 labels)
```

```
#0292  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0292_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +30
   T:0
   Russia
   -1
   T:3
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  4t]
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   [0/5 actions remaining]
   ► commission Augereau
   Marshal Augereau accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Massena (Friendly). That was the last order the day could take, Sire — the turn ends when you say so.
   [0/5 actions remaining]
map: unchanged (118 labels)
```

```
#0293  click End Turn  ->  ok
  (clicked at (929, 978))
view: <run>\frames\0293_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   0/5
   Admin:
   0/2
   Gold:
   4,423
   Inf:
   70,244
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E) ▸]  [Open Envoys (1)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ⚠ You have 1 unanswered envoy that will lapse if you end the turn now. 1 petition will be REFUSED if you end the turn: The Kingdom of Italy — −10 loyalty / −20 bond (a lapse is a refusal).
   Click Open Envoys to review now, or press End Turn again, Enter, or type end turn again to confirm the lapse.
map: unchanged (118 labels)
```

```
#0294  click End Turn  ->  ok
  (clicked at (809, 978))
view: <run>\frames\0294_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 15
   RUSSIA / ──────────────────────────── / - Buxhowden attacks Davout /     Battle of Vienna /     Buxhowden: 3,364 casualties, 19,471 remaining /     Davout's army: 1,503 casualties — Davout's own corps: 8,737 remaining /     Result: Defender tactical victory (Davout victorious) /     ⚔ View the field /     --- Berthier's Report --- /     Attack: Buxhowden (Defensive stance -10%) /     Defense: Davo …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 80 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,403
   Inf:
   71,893
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Ney, move to Lithuania
   → Ney moves from Silesia to Lithuania. Lithuania falls to France! (was Russia) (64 lost to march)
   Volhynia, Samogitia, Ukraine lie undefended — an attack takes any of them.
   Your forces have taken Lithuania. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   [0/5 actions remaining]
   Your forces await orders: Plunder or Secure?
   You order your troops to plunder the region!
   Ney's troops plunder Lithuania! Gained 800 gold. Buildings destroyed. Stability set to 10.
   ► commission Oudinot
   Marshal Oudinot accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Lannes (Friendly).
   [0/5 actions remaining]
   ► commission Augereau
   Marshal Augereau accepts his commission and raises a corps of 5,000 at Paris — 3500g. He arrives with a history: Massena (Friendly). That was the last order the day could take, Sire — the turn ends when you say so.
   [0/5 actions remaining]
   ⚠ You have 1 unanswered envoy that will lapse if you end the turn now. 1 petition will be REFUSED if you end the turn: The Kingdom of Italy — −10 loyalty / −20 bond (a lapse is a refusal).
   Click Open Envoys to review now, or press End Turn again, Enter, or type end turn again to confirm the lapse.
   ► end turn
   ═══════════════════════════════════════
   TURN 16 BEGINS
   ═══════════════════════════════════════
   Income: 2912g | Occupation: -310g | Charges of Empire: -257g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Blockade: -289g | Materiel: -249g | Other: +1399g | Upkeep: -816g | Net: +1980g | Spent: 7000g
   Treasury: 6,403g
   Actions refreshed: 5/5
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   Garrison at Dresden reinforced: 5,922 -> 7,922
   Garrison at Vienna reinforced: 2,000 -> 4,000
   Garrison at Berlin reinforced: 2,000 -> 4,000
   Garrison at Lisbon reinforced: 5,770 -> 7,770
   Holland loyalty 71 (+15): a common enemy, the lord's victories
   The Kingdom of Italy's petition for Bohemia went unanswered and lapses as a refusal: loyalty −10 (84 → 74); bond 5 → -15 (-1 a turn). Nothing is charged.
   Kingdom of Italy loyalty 90 (+6): refused petition, a common enemy, the lord's victories
   Switzerland loyalty 94 (+17): a common enemy, the lord's victories
   Holland sends 4,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Orleanais. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 6,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Davout at Vienna. The Kingdom of Italy pays them; their dead will be its grief.
   Britain subsidizes Naples with 300 gold.
   Marshal Oudinot accepts his commission — he raises a corps of 5,000 at Paris.
   Marshal Augereau accepts his commission — he raises a corps of 5,000 at Paris.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Berthier: Enemy forces spotted near Vienna! Archduke John (11,607 troops) at Bohemia.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Ardennes(1486,378)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Napoleon(2673,149)  Ney(2897,69)  Kutuzov(2953,35)  Archduke John(2276,485)  Deroy(2090,426)  ?(2257,819)  Archduke Charles(2257,785)  Davout(2442,539)  Murat(2470,505)  Massena(2499,471)  ?(2666,499)  Buxhowden(2666,465)  ?(2519,711)  Bennigsen(2519,677)  ?(1834,103)  Brunswick(1834,51)  Bernadotte(1525,411)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  7k(2376,360)  4k(2470,645)  ?(2798,413)  4k(2126,239)  ?(1899,567)  ?(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0295  scroll 1828 548 down 6  ->  ok
  (scrolled down 6 at (1828, 548))
view: <run>\frames\0295_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Marshal Oudinot accepts his commission — he raises a corps of 5,000 at Paris.
   Marshal Augereau accepts his commission — he raises a corps of 5,000 at Paris.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Berthier: Enemy forces spotted near Vienna! Archduke John (11,607 troops) at Bohemia.
map: unchanged (116 labels)
```

```
#0296  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0296_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt'], region_panel=no
── InterruptPopup (layer 103) ──
   NEY REPORTS
   "Ney is cornered at Lithuania with 4,231 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout."
   controls: [Fight to the Last]  [Attempt a Breakout]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   --- Strategic Order Updates ---
   Bernadotte: Bernadotte marches to Orleanais. 3 regions to Franconia.
   Ney: Ney is cornered at Lithuania with 4,231 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
   Ney awaits your orders!
map: unchanged (116 labels)
```

```
#0297  click Fight to the Last  ->  ok
  (clicked at (1686, 590))
view: <run>\frames\0297_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   RUSSIA LOSSES
   0
   0
   Massena
   13,734 → 13,321
   Murat
   20,907 → 20,278
   ⚔
   Davout ◆
   Buxhowden ◆
   9,198 → 8,737
   22,835 → 19,471
   marched to the guns
   BATTLE OF VIENNA
   click anywhere to skip ▸
   VIENNA · TURN 15
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 80 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Ney is cornered @(3393,64)]  [icon: Coalition Brewing — 3 turns @(3435,64)]  [icon: Armistice Collapsed @(3477,64)]  [icon: Ney orders lost @(3519,64)]  [icon: Davout — free attack! @(3561,64)]  [+44]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +30
   T:0
   Russia
   -1
   T:3
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  4t]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,403
   Inf:
   74,008
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   3 satellites steadied — Holland, Kingdom of Italy and Switzerland.
   The Kingdom of Italy's petition for Bohemia went unanswered and lapses as a refusal: loyalty −10 (84 → 74); bond 5 → -15 (-1 a turn). Nothing is charged.
   Marshal Oudinot accepts his commission — he raises a corps of 5,000 at Paris.
   Marshal Augereau accepts his commission — he raises a corps of 5,000 at Paris.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   PRISONERS OF WAR
   Lannes — held by Prussia since turn 13.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Commissariat — fed provinces feed 25% more men (×1.25).
   War exhaustion grows — France nears breaking point (exhaustion: 60).
   War exhaustion grows — Prussia nears breaking point (exhaustion: 60).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 4,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Orleanais. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 6,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Davout at Vienna. The Kingdom of Italy pays them; their dead will be its grief.
   Britain's gold reaches Naples — the subsidy stands at 300 this season.
   LAPSED ENVOYS
   The Kingdom of Italy's petition for Bohemia went unanswered and lapses as a refusal: loyalty −10 (84 → 74); bond 5 → -15 (-1 a turn). Nothing is charged.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (5 held, unsettled: Brandenburg, Lithuania, Posen …) · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-2)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms (+22)
   War Purpose: Defense vs Ottoman — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sweden — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Naples — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 80/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Ardennes(1486,378)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Napoleon(2673,149)  Kutuzov(2925,69)  Archduke John(2276,485)  Deroy(2090,426)  ?(2257,819)  Archduke Charles(2257,785)  Davout(2442,539)  Murat(2470,505)  Massena(2499,471)  ?(2666,499)  Buxhowden(2666,465)  ?(2519,711)  Bennigsen(2519,677)  ?(1834,103)  Brunswick(1834,51)  Bernadotte(1525,411)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  7k(2376,360)  4k(2470,645)  ?(2798,413)  4k(2126,239)  ?(1899,567)  ?(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0298  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Davout ◆' (Control, layer 121))
view: <run>\frames\0298_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS OURS
   FRANCE LOSSES
   RUSSIA LOSSES
   1,503
   3,364
   Massena
   13,734 → 13,321
   Murat
   20,907 → 20,278
   ⚔
   Davout ◆
   Buxhowden ◆
   9,198 → 8,737
   22,835 → 19,471
   marched to the guns
   Berthier: “Massena arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire.” / Buxhowden: "Losses are recorded. Blame is a separate column."
   BATTLE OF VIENNA
   VIENNA · TURN 15
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 80/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0299  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0299_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,403
   Inf:
   74,008
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 80/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0300  type where is Ney  ->  ok
  (typed and Enter)
view: <run>\frames\0300_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."

What I CAN do today:
  Davout, attack Archduke John
  Soult, march to Dresden
  enact the Artillery Reserve — 3,000g, then 150g a turn (artillery levies cost 15% less (×0.85)); the Charges of Empire fall by 365g a turn
  recruit infantry in Paris — 518g for 10,000 men under Oudinot

For any matter of state, press F1 for the Cabinet.
Type 'help' for the full command reference.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 80 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Coalition Brewing — 3 turns @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Ney orders lost @(3477,64)]  [icon: Davout — free attack! @(3519,64)]  [icon: Marshal Davout grows bitter @(3561,64)]  [+43]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +22
   T:1
   Russia
   -3
   T:4
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  3t]
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   War exhaustion grows — France nears breaking point (exhaustion: 60).
   War exhaustion grows — Prussia nears breaking point (exhaustion: 60).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Holland sends 4,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Bernadotte at Orleanais. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 6,500 men under Teulie to the colours at Milan — they await the orders of France. The nearest host is Davout at Vienna. The Kingdom of Italy pays them; their dead will be its grief.
   Britain's gold reaches Naples — the subsidy stands at 300 this season.
   LAPSED ENVOYS
   The Kingdom of Italy's petition for Bohemia went unanswered and lapses as a refusal: loyalty −10 (84 → 74); bond 5 → -15 (-1 a turn). Nothing is charged.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (5 held, unsettled: Brandenburg, Lithuania, Posen …) · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-2)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms (+22)
   War Purpose: Defense vs Ottoman — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sweden — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Naples — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 80/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   ► where is Ney
   Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
   What I CAN do today:
   Davout, attack Archduke John
   Soult, march to Dresden
   enact the Artillery Reserve — 3,000g, then 150g a turn (artillery levies cost 15% less (×0.85)); the Charges of Empire fall by 365g a turn
   recruit infantry in Paris — 518g for 10,000 men under Oudinot
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
map: unchanged (115 labels)
```

```
#0301  type status  ->  ok
  (typed and Enter)
view: <run>\frames\0301_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok === BERTHIER'S INTELLIGENCE REPORT ===

YOUR FORCES:
  Davout (Vienna): 8,737 troops, morale 33, defensive stance
  Soult (Brandenburg): 8,407 troops, morale 23, neutral stance
  Murat (Vienna): 20,278 troops, morale 63, neutral stance
  Bernadotte (Orleanais): 37,306 troops, morale 32, neutral stance, [MOVE_TO]
  Massena (Vienna): 13,321 troops, morale 21, neutral stance
  Napoleon (Silesia): 2,679 troops, morale 0, neutral stance, retreating
  Oudinot (Paris): 5,000 troops, morale 100, neutral stance
  Augereau (Paris): 5,000 troops, morale 100, neutral stance
  Dumonceau (Amsterdam): 4,500 troops, morale 100, neutral stance
  Teulie (Milan): 6,500 troops, morale 100, neutral stance

PRISONERS:
  Ney: held by Russia at Vilna since T16.
  Lannes: held by Prussia at Berlin since T13.

CONFIRMED INTELLIGENCE:
  Dresden (Saxony): garrison of 7,922 holds the works
  Kutuzov (Russia): 20,457 troops at Lithuania, defensive stance, morale 95 — famed for 'The Old Fox'
  Archduke John (Austria): 11,607 troops at Bohemia, defensive stance, morale 95
  Deroy (Bavaria): 12,431 troops at Franconia, defensive stance, morale 92
  Lisbon (Portugal): garrison of 7,770 holds the works

RECENT REPORTS:
  Archduke Charles: large force near Carniola
  Podolia (Russia): garrison — screening force holds the works
  Buxhowden: substantial force near Moravia
  Bennigsen: screening force near Hungary
  Brunswick: substantial force near Brunswick
  Vilna (Russia): garrison — substantial force holds th
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► status
   === BERTHIER'S INTELLIGENCE REPORT ===
   YOUR FORCES:
   Davout (Vienna): 8,737 troops, morale 33, defensive stance
   Soult (Brandenburg): 8,407 troops, morale 23, neutral stance
   Murat (Vienna): 20,278 troops, morale 63, neutral stance
   Bernadotte (Orleanais): 37,306 troops, morale 32, neutral stance, [MOVE_TO]
   Massena (Vienna): 13,321 troops, morale 21, neutral stance
   Napoleon (Silesia): 2,679 troops, morale 0, neutral stance, retreating
   Oudinot (Paris): 5,000 troops, morale 100, neutral stance
   Augereau (Paris): 5,000 troops, morale 100, neutral stance
   Dumonceau (Amsterdam): 4,500 troops, morale 100, neutral stance
   Teulie (Milan): 6,500 troops, morale 100, neutral stance
   PRISONERS:
   Ney: held by Russia at Vilna since T16.
   Lannes: held by Prussia at Berlin since T13.
   CONFIRMED INTELLIGENCE:
   Dresden (Saxony): garrison of 7,922 holds the works
   Kutuzov (Russia): 20,457 troops at Lithuania, defensive stance, morale 95 — famed for 'The Old Fox'
   Archduke John (Austria): 11,607 troops at Bohemia, defensive stance, morale 95
   Deroy (Bavaria): 12,431 troops at Franconia, defensive stance, morale 92
   Lisbon (Portugal): garrison of 7,770 holds the works
   RECENT REPORTS:
   Archduke Charles: large force near Carniola
   Podolia (Russia): garrison — screening force holds the works
   Buxhowden: substantial force near Moravia
   Bennigsen: screening force near Hungary
   Brunswick: substantial force near Brunswick
   Vilna (Russia): garrison — substantial force holds the works
   LAST KNOWN:
   Armfelt: last seen near Stralsund, 5 turns ago
   NO INTELLIGENCE: No word from 62 provinces beyond the frontiers of White Russia, Estonia, Albania, Aragon, Croatia, Leon, Rome, Beira.
map: unchanged (115 labels)
```

```
#0302  type Napoleon, march to Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0302_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Napoleon is recovering from retreat (2 turns remaining) and cannot accept strategic orders.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, march to Vienna
   Napoleon is recovering from retreat (2 turns remaining) and cannot accept strategic orders.
map: unchanged (115 labels)
```

```
#0303  type Napoleon, move to Posen  ->  ok
  (typed and Enter)
view: <run>\frames\0303_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon moves from Silesia to Posen (26 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/5
   Admin:
   2/2
   Gold:
   6,403
   Inf:
   74,008
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, move to Posen
   → Napoleon moves from Silesia to Posen (26 lost to march)
   [4/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Ardennes(1486,378)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Kutuzov(2925,69)  Archduke John(2276,485)  Deroy(2090,426)  ?(2257,819)  Archduke Charles(2257,785)  Davout(2442,539)  Murat(2470,505)  Massena(2499,471)  ?(2666,499)  Buxhowden(2666,465)  ?(2519,711)  Bennigsen(2519,677)  Napoleon(2407,0)  ?(1834,103)  Brunswick(1834,51)  Bernadotte(1525,411)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  7k(2376,360)  4k(2470,645)  ?(2798,413)  4k(2126,239)  ?(1899,567)  ?(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0304  type Murat, attack Archduke John in Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0304_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Murat (20,278; expect about 31,639 with the corps likely to arrive, up to 32,170 if all march) vs Archduke John (11,607 men) at Bohemia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  The band weighs more than the men: Archduke John stands +33% on the defense (his stance, his character and his works).
  Bohemia feeds 40,000 — the whole muster standing there would lose ~883 men a turn to short supply.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.


[Combat] Murat leads the charge! (Aggressive: +15% attack)
[Shield] Archduke John's DEFENSIVE stance strengthens the line! (+15% defense)
[Shield] Archduke John's methodical defense is exemplary! (Cautious: +20% total) Outnumbered bonus: +10%
[Cavalry] Murat's cavalry thrives on Plains terrain! (120% effectiveness)
[Combat] Murat's combined arms coordination! (+10% attack)
Murat attacks with overwhelming force. Murat gains the advantage over Archduke John. Casualties: Murat's army 2,511, Archduke John 4,578. Both armies remain in the field. Murat advances into Bohemia. (
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Davout
   8,737 → 8,537
   Massena
   13,321 → 12,559
   ⚔
   Murat ◆
   Archduke John ◆
   20,278 → 18,729 → 18,542 after the advance
   11,607 → 7,029
   marched to the guns
   marched to the guns
   SECOND BATTLE OF BOHEMIA
   click anywhere to skip ▸
   BOHEMIA · TURN 16
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 83 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Coalition Brewing — 3 turns @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Ney orders lost @(3477,64)]  [icon: Davout — free attack! @(3519,64)]  [icon: Marshal Davout grows bitter @(3561,64)]  [+43]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +25
   T:1
   Russia
   -3
   T:4
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  3t]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   6,278
   Inf:
   74,008
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Napoleon, move to Posen
   → Napoleon moves from Silesia to Posen (26 lost to march)
   [4/5 actions remaining]
   ► Murat, attack Archduke John in Bohemia
   ⚔ Second Battle of Bohemia ⚔
   MUSTER — Murat (20,278; expect about 31,639 with the corps likely to arrive, up to 32,170 if all march) vs Archduke John (11,607 men) at Bohemia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
   WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   The band weighs more than the men: Archduke John stands +33% on the defense (his stance, his character and his works).
   Bohemia feeds 40,000 — the whole muster standing there would lose ~883 men a turn to short supply.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Shield] Archduke John's DEFENSIVE stance strengthens the line! (+15% defense)
   [Shield] Archduke John's methodical defense is exemplary! (Cautious: +20% total) Outnumbered bonus: +10%
   [Cavalry] Murat's cavalry thrives on Plains terrain! (120% effectiveness)
   [Combat] Murat's combined arms coordination! (+10% attack)
   Murat attacks with overwhelming force. Murat gains the advantage over Archduke John. Casualties: Murat's army 2,511, Archduke John 4,578. Both armies remain in the field. Murat advances into Bohemia. (187 lost to march)
   [Materiel] Guns, horses and stores lost with the fallen: France -125g, Austria -228g.
   🐴 Murat's cavalry thrives on Plains terrain! (120% effectiveness)
   ⚔ View the field
   [3/5 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 20,278 (lead) + 11,892 committed (Davout, Massena) = 32,170.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 962 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Murat: "A hard charge settles most arguments. It settled this one."
   Attack: Murat (Personality (aggressive) +15%, Recklessness +10%, Cavalry terrain (plains) +20%)
   Defense: Archduke John (Defensive stance +15%, Personality (cautious) +5%, Outnumbered (cautious) +10%)
   Casualties: Murat's own corps 1,549 | Archduke John 4,578
   Strength: Murat 20,278 → 18,729 → 18,542 after the advance | Archduke John 11,607 → 7,029
   Berthier: "Reinforcements! Davout and Massena marched onto the field beside Murat. The enemy's advantage melted away."
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Ardennes(1486,378)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Kutuzov(2925,69)  Davout(2248,485)  Murat(2248,451)  Massena(2305,416)  Archduke John(2304,382)  Deroy(2090,426)  ?(2257,819)  Archduke Charles(2257,785)  ?(2666,499)  Buxhowden(2666,465)  ?(2519,711)  Bennigsen(2519,677)  Napoleon(2407,0)  ?(1834,103)  Brunswick(1834,51)  Bernadotte(1525,411)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  7k(2376,351)  4k(2470,645)  ?(2798,413)  4k(2126,239)  ?(1899,567)  ?(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0305  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Murat ◆' (Control, layer 121))
view: <run>\frames\0305_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS OURS
   FRANCE LOSSES
   AUSTRIA LOSSES
   2,511
   4,578
   Davout
   8,737 → 8,537
   Massena
   13,321 → 12,559
   ⚔
   Murat ◆
   Archduke John ◆
   20,278 → 18,729 → 18,542 after the advance
   11,607 → 7,029
   marched to the guns
   marched to the guns
   Berthier: “Reinforcements! Davout and Massena marched onto the field beside Murat. The enemy's advantage melted away.” / Archduke John: "Noted. The next position will cost you double."
   SECOND BATTLE OF BOHEMIA
   BOHEMIA · TURN 16
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Archduke John (Defensive stance +15%, Personality (cautious) +5%, Outnumbered (cautious) +10%)
   Casualties: Murat's own corps 1,549 | Archduke John 4,578
   Strength: Murat 20,278 → 18,729 → 18,542 after the advance | Archduke John 11,607 → 7,029
   Berthier: "Reinforcements! Davout and Massena marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (116 labels)
```

```
#0306  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0306_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Archduke John (Defensive stance +15%, Personality (cautious) +5%, Outnumbered (cautious) +10%)
   Casualties: Murat's own corps 1,549 | Archduke John 4,578
   Strength: Murat 20,278 → 18,729 → 18,542 after the advance | Archduke John 11,607 → 7,029
   Berthier: "Reinforcements! Davout and Massena marched onto the field beside Murat. The enemy's advantage melted away."
map: unchanged (116 labels)
```

```
#0307  type Massena, attack Archduke John  ->  ok
  (typed and Enter)
view: <run>\frames\0307_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['capture_choice'], region_panel=no
reply: ok MUSTER — Massena (12,559; expect about 38,060 with the corps likely to arrive) vs Archduke John (7,029 men) at Bohemia — the balance of force looks favorable.
  WILL JOIN — Davout: stands on the field and will fight beside him
  WILL JOIN — Murat: stands on the field and will fight beside him
  The band weighs more than the men: Archduke John stands +33% on the defense (his stance, his character and his works).
  Bohemia feeds 32,000 — the whole muster standing there would lose ~934 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
  Murat shares the field at Bohemia — his men will absorb part of any losses.


Massena holds them at Bohemia while allies attack from Vienna! (+1 coordination)

[Combat] Massena leads the charge! (Aggressive: +15% attack)
[Shield] Archduke John's DEFENSIVE stance strengthens the line! (+15% defense)
[Shield] Archduke John's methodical defense is exemplary! (Cautious: +20% total) Outnumbered bonus: +10%
[Combat] Massena's combined arms coordination! (+10% attack)
Massena launches a decisive assault. Massena gains the advantage over Archduke John. Casualties: Massena's army 811, Archduke John 4,575. Both armies remain in the field. Bohemia has been captured by France!
[Materiel] Guns, horses and stores lost 
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Massena has taken Bohemia
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+800 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 88 / 100
   Turn 16 — Early May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   6,238
   Inf:
   74,008
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Attack: Murat (Personality (aggressive) +15%, Recklessness +10%, Cavalry terrain (plains) +20%)
   Defense: Archduke John (Defensive stance +15%, Personality (cautious) +5%, Outnumbered (cautious) +10%)
   Casualties: Murat's own corps 1,549 | Archduke John 4,578
   Strength: Murat 20,278 → 18,729 → 18,542 after the advance | Archduke John 11,607 → 7,029
   Berthier: "Reinforcements! Davout and Massena marched onto the field beside Murat. The enemy's advantage melted away."
   ► Massena, attack Archduke John
   ⚔ Third Battle of Bohemia ⚔
   MUSTER — Massena (12,559; expect about 38,060 with the corps likely to arrive) vs Archduke John (7,029 men) at Bohemia — the balance of force looks favorable.
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him
   The band weighs more than the men: Archduke John stands +33% on the defense (his stance, his character and his works).
   Bohemia feeds 32,000 — the whole muster standing there would lose ~934 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Murat shares the field at Bohemia — his men will absorb part of any losses.
   Massena holds them at Bohemia while allies attack from Vienna! (+1 coordination)
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Shield] Archduke John's DEFENSIVE stance strengthens the line! (+15% defense)
   [Shield] Archduke John's methodical defense is exemplary! (Cautious: +20% total) Outnumbered bonus: +10%
   [Combat] Massena's combined arms coordination! (+10% attack)
   Massena launches a decisive assault. Massena gains the advantage over Archduke John. Casualties: Massena's army 811, Archduke John 4,575. Both armies remain in the field. Bohemia has been captured by France!
   [Materiel] Guns, horses and stores lost with the fallen: France -40g, Austria -228g.
   [!] Archduke John's broken army flees to Carniola! (recovering for 3 turns)
   Your forces have taken Bohemia. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   ⚑ Bohemia captured! ⚑
   ⚔ View the field
   [2/5 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Massena fought with Davout and Murat beside him — massed effective strength: 12,559 (lead) + 25,501 committed (Davout, Murat) = 38,060.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's supporting allies lost 471 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "They broke like green wood, Sire. I want the pursuit."
   Attack: Massena (Personality (aggressive) +15%, Flanking +1%)
   Defense: Archduke John (Defensive stance +15%, Personality (cautious) +5%, Outnumbered (cautious) +10%)
   Casualties: Massena's own corps 340 | Archduke John 4,575
   Strength: Massena 12,559 → 12,219 | Archduke John 7,029 → 2,454
   Berthier: "A costly day for Archduke John: the losses ran two to one in Massena's favour, and Archduke John is still in the field."
   Your forces await orders: Plunder or Secure?
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Ardennes(1486,378)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Kutuzov(2925,69)  Davout(2248,485)  Murat(2276,451)  Massena(2305,416)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  ?(2666,499)  Buxhowden(2666,465)  ?(2519,711)  Bennigsen(2519,677)  Napoleon(2407,0)  ?(1834,103)  Brunswick(1834,51)  Bernadotte(1525,411)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  7k(2376,360)  4k(2470,645)  ?(2798,413)  4k(2126,239)  ?(1899,567)  ?(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0308  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0308_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Davout
   8,537 → 8,365
   Murat
   18,542 → 18,243
   ⚔
   Massena ◆
   Archduke John ◆
   12,559 → 12,219
   7,029 → 2,454
   THIRD BATTLE OF BOHEMIA
   click anywhere to skip ▸
   BOHEMIA · TURN 16
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 88 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Coalition Brewing — 3 turns @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Ney orders lost @(3477,64)]  [icon: Davout — free attack! @(3519,64)]  [icon: Marshal Davout grows bitter @(3561,64)]  [+43]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +37
   T:1
   Russia
   -3
   T:4
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  3t]
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You order your troops to secure the region.
   Massena secures Bohemia. Stability set to 25. Order is maintained.
map: unchanged (117 labels)
```

```
#0309  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Massena ◆' (Control, layer 121))
view: <run>\frames\0309_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS OURS
   FRANCE LOSSES
   AUSTRIA LOSSES
   811
   4,575
   Bohemia falls to France.
   Davout
   8,537 → 8,365
   Murat
   18,542 → 18,243
   ⚔
   Massena ◆
   Archduke John ◆
   12,559 → 12,219
   7,029 → 2,454
   ROUTED
   Berthier: “A costly day for Archduke John: the losses ran two to one in Massena's favour, and Archduke John is still in the field.” / Archduke John: "I trade ground for time. Time is on my side."
   THIRD BATTLE OF BOHEMIA
   BOHEMIA · TURN 16
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "A costly day for Archduke John: the losses ran two to one in Massena's favour, and Archduke John is still in the field."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Massena secures Bohemia. Stability set to 25. Order is maintained.
map: unchanged (117 labels)
```

```
#0310  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0310_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   6,238
   Inf:
   74,008
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "A costly day for Archduke John: the losses ran two to one in Massena's favour, and Archduke John is still in the field."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Massena secures Bohemia. Stability set to 25. Order is maintained.
map: unchanged (117 labels)
```

```
#0311  type Davout, move to Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0311_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Bohemia to Vienna (83 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/5
   Admin:
   2/2
   Gold:
   6,238
   Inf:
   74,008
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, attack Archduke John
   ⚔ Third Battle of Bohemia ⚔
   MUSTER — Massena (12,559; expect about 38,060 with the corps likely to arrive) vs Archduke John (7,029 men) at Bohemia — the balance of force looks favorable.
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him
   The band weighs more than the men: Archduke John stands +33% on the defense (his stance, his character and his works).
   Bohemia feeds 32,000 — the whole muster standing there would lose ~934 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Murat shares the field at Bohemia — his men will absorb part of any losses.
   Massena holds them at Bohemia while allies attack from Vienna! (+1 coordination)
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Shield] Archduke John's DEFENSIVE stance strengthens the line! (+15% defense)
   [Shield] Archduke John's methodical defense is exemplary! (Cautious: +20% total) Outnumbered bonus: +10%
   [Combat] Massena's combined arms coordination! (+10% attack)
   Massena launches a decisive assault. Massena gains the advantage over Archduke John. Casualties: Massena's army 811, Archduke John 4,575. Both armies remain in the field. Bohemia has been captured by France!
   [Materiel] Guns, horses and stores lost with the fallen: France -40g, Austria -228g.
   [!] Archduke John's broken army flees to Carniola! (recovering for 3 turns)
   Your forces have taken Bohemia. Plunder it for 800 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   ⚑ Bohemia captured! ⚑
   ⚔ View the field
   [2/5 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Massena fought with Davout and Murat beside him — massed effective strength: 12,559 (lead) + 25,501 committed (Davout, Murat) = 38,060.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massena's supporting allies lost 471 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Massena: "They broke like green wood, Sire. I want the pursuit."
   Attack: Massena (Personality (aggressive) +15%, Flanking +1%)
   Defense: Archduke John (Defensive stance +15%, Personality (cautious) +5%, Outnumbered (cautious) +10%)
   Casualties: Massena's own corps 340 | Archduke John 4,575
   Strength: Massena 12,559 → 12,219 | Archduke John 7,029 → 2,454
   Berthier: "A costly day for Archduke John: the losses ran two to one in Massena's favour, and Archduke John is still in the field."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Massena secures Bohemia. Stability set to 25. Order is maintained.
   ► Davout, move to Vienna
   → Davout moves from Bohemia to Vienna (83 lost to march)
   [1/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Ardennes(1486,378)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Kutuzov(2925,69)  Murat(2248,485)  Massena(2305,451)  Deroy(2090,426)  ?(2240,819)  Archduke Charles(2240,785)  ?(2275,819)  Archduke John(2275,751)  Davout(2470,539)  ?(2666,499)  Buxhowden(2666,465)  ?(2519,711)  Bennigsen(2519,677)  Napoleon(2407,0)  ?(1834,103)  Brunswick(1834,51)  Bernadotte(1525,411)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  7k(2376,360)  4k(2470,645)  ?(2798,413)  4k(2126,239)  ?(1899,567)  ?(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0312  type recruit infantry in Paris  ->  ok
  (typed and Enter)
view: <run>\frames\0312_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Oudinot recruits 10,000 infantry for Paris (0 regions away) - Cost: 518 gold (capital discount) (×3 at war) (Oudinot's intendance: +15%). Morale: 100% -> 60%
Infantry pool: 74,008 -> 64,008
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/5
   Admin:
   1/2
   Gold:
   5,720
   Inf:
   64,008
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry in Paris
   + Oudinot recruits 10,000 infantry for Paris (0 regions away) - Cost: 518 gold (capital discount) (×3 at war) (Oudinot's intendance: +15%). Morale: 100% -> 60%
   Infantry pool: 74,008 -> 64,008
   [1/5 actions remaining]
map: unchanged (116 labels)
```

```
#0313  type recruit infantry for Augereau  ->  ok
  (typed and Enter)
view: <run>\frames\0313_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 100% -> 60%
Infantry pool: 64,008 -> 54,008
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   1/5
   Admin:
   0/2
   Gold:
   5,202
   Inf:
   54,008
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry for Augereau
   + Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 100% -> 60%
   Infantry pool: 64,008 -> 54,008
   [1/5 actions remaining]
   ▸ The administration is spent: the order that spends your last action ends the turn at once.
map: unchanged (116 labels)
```

```
#0314  type Soult, move to Posen  ->  ok
  (typed and Enter)
view: <run>\frames\0314_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
reply: ok Soult moves from Brandenburg to Posen (84 lost to march)

Income: 2775g | Occupation: -135g | Charges of Empire: -387g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Blockade: -289g | Materiel: -73g | Other: +1399g | Upkeep: -904g | Net: +1976g | Spent: 1036g | Treasury: 7,178g
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 17
   RUSSIA / ──────────────────────────── / - Buxhowden breaks from square / - Kutuzov attacks Lithuania /     Region captured: Lithuania (was France) (secured) / - Buxhowden attacks Davout /     Second Battle of Vienna /     Buxhowden: 2,189 casualties, 17,282 remaining /     Davout's army: 1,461 casualties — Davout's own corps: 7,653 remaining /     Result: Bloody stalemate /     Vienna CAPTURED! (w …
   controls: <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 86 / 100
   Turn 17 — Late May 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   7,178
   Inf:
   55,558
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Massena secures Bohemia. Stability set to 25. Order is maintained.
   ► Davout, move to Vienna
   → Davout moves from Bohemia to Vienna (83 lost to march)
   [1/5 actions remaining]
   ► recruit infantry in Paris
   + Oudinot recruits 10,000 infantry for Paris (0 regions away) - Cost: 518 gold (capital discount) (×3 at war) (Oudinot's intendance: +15%). Morale: 100% -> 60%
   Infantry pool: 74,008 -> 64,008
   [1/5 actions remaining]
   ► recruit infantry for Augereau
   + Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 100% -> 60%
   Infantry pool: 64,008 -> 54,008
   [1/5 actions remaining]
   ▸ The administration is spent: the order that spends your last action ends the turn at once.
   ► Soult, move to Posen
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 2775g | Occupation: -135g | Charges of Empire: -387g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Blockade: -289g | Materiel: -73g | Other: +1399g | Upkeep: -904g | Net: +1976g | Spent: 1036g
   Treasury: 7,178g
   Actions refreshed: 5/5
   ═══════════════════════════════════════
   Actions exhausted — Turn 17 begins
   ═══════════════════════════════════════
   Davout's army is recovering. Effectiveness penalty: -15%. Davout rallies the survivors — the ranks reform ahead of schedule.
   Napoleon's army has fully recovered and is combat ready.
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   Garrison at Dresden reinforced: 7,922 -> 9,922
   Garrison at Vienna reinforced: 0 -> 2,000
   Garrison at Berlin reinforced: 0 -> 2,000
   Garrison at Lisbon reinforced: 0 -> 2,000
   Holland loyalty 89 (+18): a common enemy, the lord's victories
   Kingdom of Italy loyalty 100 (+10): a common enemy, the lord's victories
   Switzerland loyalty 100 (+6): a common enemy, the lord's victories
   Britain subsidizes Naples with 300 gold.
   Berthier reports that Soult resents Massena's laurels again, 8 turns after the last — he has grown scrupulous to the point of reproach.
   Berthier reports that Oudinot appears envious of Murat's laurels — he has grown impatient for something worth the doing.
   Oudinot seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Kutuzov(2673,149)  Davout(2248,485)  Murat(2276,451)  Massena(2305,416)  Brunswick(2090,426)  ?(2257,819)  Archduke John(2257,785)  Buxhowden(2471,539)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Bennigsen(2536,642)  Soult(2379,0)  Bernadotte(1655,391)  ?(1994,621)  Deroy(1995,587)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  9k(2376,360)  2k(2461,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0315  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0315_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   RUSSIA LOSSES
   0
   0
   Murat
   18,243 → 17,411
   ⚔
   Davout ◆
   Buxhowden ◆
   8,282 → 7,653
   19,471 → 17,282 → 17,110 after the advance
   marched to the guns
   SECOND BATTLE OF VIENNA
   click anywhere to skip ▸
   VIENNA · TURN 16
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Vilna garrison — Vilna — garrison — substantial force [partial]
   TURN EVENTS
   Davout's army is recovering. Effectiveness penalty: -15%. Davout rallies the survivors — the ranks reform ahead of schedule.
   Napoleon's army has fully recovered and is combat ready.
   Dresden's garrison regains 2,000: 7,922 -> 9,922.
   Vienna's garrison regains 2,000: 0 -> 2,000.
   3 satellites steadied — Holland, Kingdom of Italy and Switzerland.
   Berthier reports that Soult resents Massena's laurels again, 8 turns after the last — he has grown scrupulous to the point of reproach.
   Berthier reports that Oudinot appears envious of Murat's laurels — he has grown impatient for something worth the doing.
   Oudinot seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   PRISONERS OF WAR
   Ney — held by Russia since turn 16.
   Lannes — held by Prussia since turn 13.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Naples — the subsidy stands at 300 this season.
   REVANCHE: Portugal will not forgive Spain the loss of Beira and 2 more provinces. A new design hardens in their court.
   The court of Prussia takes up a new design: Revanche.
   The court of Portugal takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (3 held, unsettled: Bohemia, Brandenburg, Posen) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-12)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+11)
   War Purpose: Defense vs Ottoman — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sweden — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Naples — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 86/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Mortier awaits a commission at 4,000g."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0316  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Davout ◆' (Control, layer 121))
view: <run>\frames\0316_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   A BLOODY STALEMATE
   FRANCE LOSSES
   RUSSIA LOSSES
   1,461
   2,189
   Vienna changes hands.
   Murat
   18,243 → 17,411
   ⚔
   Davout ◆
   Buxhowden ◆
   8,282 → 7,653
   19,471 → 17,282 → 17,110 after the advance
   marched to the guns
   ROUTED
   Berthier: “Reinforcement from Murat kept Davout standing, Sire — but neither side yielded the ground.” / Buxhowden: "No result. The returns are complete."
   SECOND BATTLE OF VIENNA
   VIENNA · TURN 16
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 86/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Mortier awaits a commission at 4,000g."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0317  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0317_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   7,178
   Inf:
   55,558
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 86/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Mortier awaits a commission at 4,000g."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0318  type Murat, attack Buxhowden at Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0318_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['glorious_charge'], region_panel=no
reply: [Cavalry] Murat's blood is up! (Recklessness: 3)

Choose:
• CHARGE: Execute Glorious Charge (2x damage dealt AND taken, resets recklessness)
• RESTRAIN: Normal attack (marshal may object next time)
── GloriousChargeDialog (layer 106) ──
   GLORIOUS CHARGE!
   Murat's blood is up!
   Recklessness: |||. (3/4)
   Glorious Charge deals 2x damage but also TAKES 2x damage! / Target: Buxhowden
   controls: [CHARGE! (2x damage dealt AND taken)]  [Restrain - Normal Attack]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   7,178
   Inf:
   55,558
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Murat, attack Buxhowden at Vienna
   🐴 Murat's blood is up!
   Recklessness at 3/4 - Glorious Charge available!
map: unchanged (115 labels)
```

```
#0319  click CHARGE  ->  ok
  (clicked at (1710, 607))
view: <run>\frames\0319_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 86 / 100
   Turn 17 — Late May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Coalition Brewing — 3 turns @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Ney orders lost @(3477,64)]  [icon: Davout — free attack! @(3519,64)]  [icon: Marshal Davout grows bitter @(3561,64)]  [+44]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +11
   T:2
   Russia
   -12
   T:5
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  2t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,717
   Inf:
   55,558
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-12)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+11)
   War Purpose: Defense vs Ottoman — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sweden — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Naples — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 86/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Mortier awaits a commission at 4,000g."
   ════════════════════════════════════
   ► Murat, attack Buxhowden at Vienna
   🐴 Murat's blood is up!
   Recklessness at 3/4 - Glorious Charge available!
   🐴⚔ Murat unleashes a GLORIOUS CHARGE! ⚔🐴
   [Cavalry][Combat] GLORIOUS CHARGE! Murat leads a devastating cavalry assault!
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Shield] Buxhowden's DEFENSIVE stance strengthens the line! (+15% defense)
   [Fort] Buxhowden's fortified position provides +7% defense!
   [Cavalry] Murat's cavalry thrives on Plains terrain! (120% effectiveness)
   [Cavalry][Combat] GLORIOUS CHARGE! Murat's cavalry deals devastating damage - but exposes themselves! (2x casualties both ways)
   [Combat] Murat's combined arms coordination! (+10% attack)
   Murat executes a brilliant maneuver! Buxhowden holds the line. Casualties: Murat 9,226, Buxhowden 4,664. Both armies remain in the field.
   [!] Murat's troops are BROKEN (morale 18%)! FORCED RETREAT!
   Murat's recklessness resets after Glorious Charge
   [!] Murat's broken army flees to Franconia! (40 lost to march) (recovering for 3 turns)
   [Materiel] Guns, horses and stores lost with the fallen: France -461g, Russia -233g.
   Recklessness reset: 3 → 0
   --- Berthier's Report ---
   Attack: Murat (Personality (aggressive) +15%, Recklessness +15%, Cavalry terrain (plains) +20%, Glorious Charge +100%)
   Defense: Buxhowden (Defensive stance +15%, Fortified position +7%)
   Casualties: Murat 9,226 | Buxhowden 4,664
   Strength: Murat 17,411 → 8,185 | Buxhowden 17,110 → 12,446
   Berthier: "The enemy fortifications proved formidable, Sire. Murat's assault was repulsed."
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Kutuzov(2673,149)  Davout(2248,485)  Massena(2305,451)  Murat(2062,426)  Brunswick(2118,392)  ?(2257,819)  Archduke John(2257,785)  Buxhowden(2471,539)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Bennigsen(2536,642)  Soult(2379,0)  Bernadotte(1655,391)  ?(1994,621)  Deroy(1995,587)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  9k(2376,360)  2k(2461,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0320  type Massena, attack Buxhowden at Vienna  ->  ok
  (typed and Enter)
view: <run>\frames\0320_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Massena (12,219) vs Buxhowden (12,446 men) at Vienna — the balance of force looks even — a hard fight that may well decide nothing.
  WILL NOT — Davout: is in no condition to fight
  The band weighs more than the men: Buxhowden stands +17% on the defense (his stance, his character and his works).
  Vienna feeds 50,000 — the whole muster can stand there fed.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.


[Combat] Massena leads the charge! (Aggressive: +15% attack)
[Shield] Buxhowden's DEFENSIVE stance strengthens the line! (+15% defense)
[Fort] Buxhowden's fortified position provides +2% defense!
Massena engages in solid combat. Buxhowden holds the line. Casualties: Massena 2,968, Buxhowden 812. Both armies remain in the field.

[!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT!
[Materiel] Guns, horses and stores lost with the fallen: France -148g, Russia -40g.
[!] Massena's broken army flees to Franconia! (46 lost to march) (recovering for 3 turns)
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   RUSSIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Buxhowden ◆
   12,219 → 9,251
   12,446 → 11,634
   THIRD BATTLE OF VIENNA
   click anywhere to skip ▸
   VIENNA · TURN 17
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +11
   T:2
   Russia
   -21
   T:5
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  2t]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/5
   Admin:
   2/2
   Gold:
   6,569
   Inf:
   55,558
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Massena, attack Buxhowden at Vienna
   ⚔ Third Battle of Vienna ⚔
   MUSTER — Massena (12,219) vs Buxhowden (12,446 men) at Vienna — the balance of force looks even — a hard fight that may well decide nothing.
   WILL NOT — Davout: is in no condition to fight
   The band weighs more than the men: Buxhowden stands +17% on the defense (his stance, his character and his works).
   Vienna feeds 50,000 — the whole muster can stand there fed.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Shield] Buxhowden's DEFENSIVE stance strengthens the line! (+15% defense)
   [Fort] Buxhowden's fortified position provides +2% defense!
   Massena engages in solid combat. Buxhowden holds the line. Casualties: Massena 2,968, Buxhowden 812. Both armies remain in the field.
   [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT!
   [Materiel] Guns, horses and stores lost with the fallen: France -148g, Russia -40g.
   [!] Massena's broken army flees to Franconia! (46 lost to march) (recovering for 3 turns)
   ⚔ View the field
   [4/5 actions remaining]
   --- Berthier's Report ---
   Massena: "Driven from a field. It is not a habit I intend to form."
   Attack: Massena (Personality (aggressive) +15%)
   Defense: Buxhowden (Defensive stance +15%, Fortified position +2%)
   Casualties: Massena 2,968 | Buxhowden 812
   Strength: Massena 12,219 → 9,251 | Buxhowden 12,446 → 11,634
   Berthier: "Attacking prepared positions cost Massena dearly. The fortifications held."
   The war's cost now stands at 44,430 of our men.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Kutuzov(2673,149)  Davout(2276,485)  Murat(2062,426)  Massena(2090,392)  Brunswick(2118,358)  ?(2257,819)  Archduke John(2257,785)  Buxhowden(2471,539)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Bennigsen(2536,642)  Soult(2379,0)  Bernadotte(1655,391)  ?(1994,621)  Deroy(1995,587)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  9k(2376,360)  2k(2461,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0321  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Massena ◆' (Control, layer 121))
view: <run>\frames\0321_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE ASSAULT FAILS
   FRANCE LOSSES
   RUSSIA LOSSES
   2,968
   812
   ⚔
   Massena ◆
   Buxhowden ◆
   12,219 → 9,251
   12,446 → 11,634
   ROUTED
   Berthier: “Attacking prepared positions cost Massena dearly. The fortifications held.” / Buxhowden: "My orders were to hold. The position is held."
   THIRD BATTLE OF VIENNA
   VIENNA · TURN 17
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Casualties: Massena 2,968 | Buxhowden 812
   Strength: Massena 12,219 → 9,251 | Buxhowden 12,446 → 11,634
   Berthier: "Attacking prepared positions cost Massena dearly. The fortifications held."
   The war's cost now stands at 44,430 of our men.
map: unchanged (115 labels)
```

```
#0322  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0322_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Casualties: Massena 2,968 | Buxhowden 812
   Strength: Massena 12,219 → 9,251 | Buxhowden 12,446 → 11,634
   Berthier: "Attacking prepared positions cost Massena dearly. The fortifications held."
   The war's cost now stands at 44,430 of our men.
map: unchanged (115 labels)
```

```
#0323  type Davout, move to Franconia  ->  ok
  (typed and Enter)
view: <run>\frames\0323_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Bohemia to Franconia (76 lost to march)
Tyrol lies undefended — an attack takes it.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   6,569
   Inf:
   55,558
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Murat executes a brilliant maneuver! Buxhowden holds the line. Casualties: Murat 9,226, Buxhowden 4,664. Both armies remain in the field.
   [!] Murat's troops are BROKEN (morale 18%)! FORCED RETREAT!
   Murat's recklessness resets after Glorious Charge
   [!] Murat's broken army flees to Franconia! (40 lost to march) (recovering for 3 turns)
   [Materiel] Guns, horses and stores lost with the fallen: France -461g, Russia -233g.
   Recklessness reset: 3 → 0
   --- Berthier's Report ---
   Attack: Murat (Personality (aggressive) +15%, Recklessness +15%, Cavalry terrain (plains) +20%, Glorious Charge +100%)
   Defense: Buxhowden (Defensive stance +15%, Fortified position +7%)
   Casualties: Murat 9,226 | Buxhowden 4,664
   Strength: Murat 17,411 → 8,185 | Buxhowden 17,110 → 12,446
   Berthier: "The enemy fortifications proved formidable, Sire. Murat's assault was repulsed."
   ► Massena, attack Buxhowden at Vienna
   ⚔ Third Battle of Vienna ⚔
   MUSTER — Massena (12,219) vs Buxhowden (12,446 men) at Vienna — the balance of force looks even — a hard fight that may well decide nothing.
   WILL NOT — Davout: is in no condition to fight
   The band weighs more than the men: Buxhowden stands +17% on the defense (his stance, his character and his works).
   Vienna feeds 50,000 — the whole muster can stand there fed.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Combat] Massena leads the charge! (Aggressive: +15% attack)
   [Shield] Buxhowden's DEFENSIVE stance strengthens the line! (+15% defense)
   [Fort] Buxhowden's fortified position provides +2% defense!
   Massena engages in solid combat. Buxhowden holds the line. Casualties: Massena 2,968, Buxhowden 812. Both armies remain in the field.
   [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT!
   [Materiel] Guns, horses and stores lost with the fallen: France -148g, Russia -40g.
   [!] Massena's broken army flees to Franconia! (46 lost to march) (recovering for 3 turns)
   ⚔ View the field
   [4/5 actions remaining]
   --- Berthier's Report ---
   Massena: "Driven from a field. It is not a habit I intend to form."
   Attack: Massena (Personality (aggressive) +15%)
   Defense: Buxhowden (Defensive stance +15%, Fortified position +2%)
   Casualties: Massena 2,968 | Buxhowden 812
   Strength: Massena 12,219 → 9,251 | Buxhowden 12,446 → 11,634
   Berthier: "Attacking prepared positions cost Massena dearly. The fortifications held."
   The war's cost now stands at 44,430 of our men.
   ► Davout, move to Franconia
   → Davout moves from Bohemia to Franconia (76 lost to march)
   Tyrol lies undefended — an attack takes it.
   [3/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Kutuzov(2673,149)  Davout(2061,426)  Murat(2062,392)  Massena(2118,358)  Brunswick(2118,324)  ?(2257,819)  Archduke John(2257,785)  Buxhowden(2471,539)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Bennigsen(2536,642)  Soult(2379,0)  Bernadotte(1655,391)  ?(1994,621)  Deroy(1995,587)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  9k(2376,360)  2k(2461,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0324  type Napoleon, move to Brandenburg  ->  ok
  (typed and Enter)
view: <run>\frames\0324_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon moves from Posen to Brandenburg (26 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   6,569
   Inf:
   55,558
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, move to Brandenburg
   → Napoleon moves from Posen to Brandenburg (26 lost to march)
   [2/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Kutuzov(2673,149)  Davout(2061,426)  Murat(2062,392)  Massena(2118,358)  Brunswick(2118,324)  ?(2257,819)  Archduke John(2257,785)  Buxhowden(2471,539)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Bennigsen(2536,642)  Soult(2407,0)  Bernadotte(1655,391)  ?(1994,621)  Deroy(1995,587)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  9k(2376,360)  2k(2461,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0325  type Soult, move to Brandenburg  ->  ok
  (typed and Enter)
view: <run>\frames\0325_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult moves from Posen to Brandenburg (83 lost to march)
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   1/5
   Admin:
   2/2
   Gold:
   6,569
   Inf:
   55,558
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, move to Brandenburg
   → Soult moves from Posen to Brandenburg (83 lost to march)
   [1/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Munich(1995,673)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-51)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2673,152)  Kutuzov(2673,118)  Davout(2061,426)  Murat(2062,392)  Massena(2118,358)  Brunswick(2118,324)  ?(2257,819)  Archduke John(2257,785)  Buxhowden(2471,539)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Bennigsen(2536,642)  Bernadotte(1655,391)  ?(1994,621)  Deroy(1995,587)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  9k(2376,360)  2k(2461,645)  ?(2798,413)  2k(2126,239)  ?(1899,567)  ?(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0326  type recruit infantry for Oudinot  ->  ok
  (typed and Enter)
view: <run>\frames\0326_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Oudinot recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Oudinot's intendance: +15%). Morale: 60% -> 52%
Infantry pool: 55,558 -> 45,558
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   1/5
   Admin:
   1/2
   Gold:
   6,051
   Inf:
   45,558
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry for Oudinot
   + Oudinot recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Oudinot's intendance: +15%). Morale: 60% -> 52%
   Infantry pool: 55,558 -> 45,558
   [1/5 actions remaining]
map: unchanged (117 labels)
```

```
#0327  type recruit infantry for Augereau  ->  ok
  (typed and Enter)
view: <run>\frames\0327_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 60% -> 52%
Infantry pool: 45,558 -> 35,558
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   1/5
   Admin:
   0/2
   Gold:
   5,533
   Inf:
   35,558
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry for Augereau
   + Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 60% -> 52%
   Infantry pool: 45,558 -> 35,558
   [1/5 actions remaining]
   ▸ The administration is spent: the order that spends your last action ends the turn at once.
map: unchanged (117 labels)
```

```
#0328  click THE FOURTH BRITISH COALITION  ->  ok
  (clicked at (3211, 895))
view: <run>\frames\0328_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) ──
   THE FOURTH BRITISH COALITION
   Britain
   BR
   0
   FR
   Austria
   AU
   +11
   FR
   Portugal
   PO
   0
   FR
   Ottoman Empire
   OT
   0
   FR
   Saxony
   SA
   0
   FR
   Papal States
   PA
   0
   FR
   Sweden
   SW
   0
   FR
   Naples
   NA
   0
   FR
   Hanover
   HA
   0
   FR
   Sardinia
   SA
   0
   FR
   Russia
   RU
   −21
   FR
   Leader: Britain   Posture: Defensive /  /   Britain  Unknown  — leads the coalition /   Austria  WE:24  ~45,000 men /   Portugal  Unknown /   Ottoman Empire  Unknown /   Saxony  Unknown /   Papal States  Unknown /   Sweden  Considerable (last seen) /   Naples  Unknown /   Hanover  Unknown /   Sardinia  Unknown /   Russia  WE:55  35,985 men /  / Coordination /   Britain-Austria: Good /   Britain-Po …
   Coalition spans multiple wars; settle each separately.
   controls: [icon @(2702,276)]  [Target Austria]  [Target Portugal]  [Target Ottoman Empire]  [Target Saxony]  [Target Papal States]  [Target Sweden]  [Target Naples]  [Target Hanover]  [Target Sardinia]  [Target Russia]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   + Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 60% -> 52%
   Infantry pool: 45,558 -> 35,558
   [1/5 actions remaining]
   ▸ The administration is spent: the order that spends your last action ends the turn at once.
map: unchanged (117 labels)
```

```
#0329  click Target Austria  ->  ok
  (clicked at (2506, 700))
view: <run>\frames\0329_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY — Austria
   DP: 7
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War   Relation: -100 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus. /  / KEY FACTORS /   + Base willingness (+20) /   + Diplomat personality ( …
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Unlikely]  [Open Settlement]  [Propose White Peace]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5]  [Undermine Alliances (2 DP)  —  -4 relation between targets/turn]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   + Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 60% -> 52%
   Infantry pool: 45,558 -> 35,558
   [1/5 actions remaining]
   ▸ The administration is spent: the order that spends your last action ends the turn at once.
map: unchanged (117 labels)
```

```
#0330  click Cancel  ->  ok
  (clicked at (1884, 739))
view: <run>\frames\0330_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   + Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 60% -> 52%
   Infantry pool: 45,558 -> 35,558
   [1/5 actions remaining]
   ▸ The administration is spent: the order that spends your last action ends the turn at once.
map: unchanged (117 labels)
```

```
#0331  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0331_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 17
   RUSSIA / ──────────────────────────── / - Buxhowden abandons fortified position / - Kutuzov attacks Posen /     Region captured: Posen (was France) (secured) / - Kutuzov attacks Soult /     Third Battle of Brandenburg /     Kutuzov: 504 casualties, 19,519 remaining /     Soult's army: 3,453 casualties — Soult's own corps: 5,453 remaining /     Result: Attacker tactical victory (Kutuzov victorious) …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 84 / 100
   Turn 18 — Early June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,824
   Inf:
   39,559
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   → Napoleon moves from Posen to Brandenburg (26 lost to march)
   [2/5 actions remaining]
   ► Soult, move to Brandenburg
   → Soult moves from Posen to Brandenburg (83 lost to march)
   [1/5 actions remaining]
   ► recruit infantry for Oudinot
   + Oudinot recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Oudinot's intendance: +15%). Morale: 60% -> 52%
   Infantry pool: 55,558 -> 45,558
   [1/5 actions remaining]
   ► recruit infantry for Augereau
   + Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 60% -> 52%
   Infantry pool: 45,558 -> 35,558
   [1/5 actions remaining]
   ▸ The administration is spent: the order that spends your last action ends the turn at once.
   ► end turn
   ═══════════════════════════════════════
   TURN 18 BEGINS
   ═══════════════════════════════════════
   Income: 2678g | Occupation: -70g | Charges of Empire: -638g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Blockade: -289g | Materiel: -203g | Other: +1399g | Upkeep: -1176g | Net: +1291g | Spent: 1036g
   Treasury: 6,824g
   Actions refreshed: 5/5
   Davout's army has fully recovered and is combat ready.
   Murat's army is recovering. Effectiveness penalty: -30%.
   Massena's army is recovering. Effectiveness penalty: -40%. The rout's disorder lingers in the ranks.
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   [!] Davout's Counter-Punch opportunity has expired! (Must use immediately after defending)
   Garrison at Dresden reinforced: 9,922 -> 10,000
   Garrison at Vienna reinforced: 2,000 -> 4,000
   Garrison at Berlin reinforced: 2,000 -> 4,000
   Garrison at Lisbon reinforced: 2,000 -> 4,000
   Garrison at Munich reinforced: 0 -> 2,000
   Holland loyalty 99 (+10): a common enemy
   Relations between France and Spain are deteriorating. Alliance may collapse in 2 turns.
   Britain subsidizes Naples with 300 gold.
   Berthier notes that Oudinot no longer presses the matter — his quarrel with Murat has cooled.
   Berthier reports that Augereau appears envious of Davout's laurels — he has grown restless for glory.
   Augereau seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Oudinot's resentment of Murat is set aside. His rival's corps is broken or falling back — there is nothing in him to envy until it rallies.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Swabia(1899,510)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Napoleon(2376,248)  Davout(2061,426)  Murat(2090,392)  Massena(2118,358)  ?(2257,819)  Archduke John(2257,785)  Buxhowden(2471,539)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Bennigsen(2536,642)  ?(1899,458)  Deroy(1899,424)  Bernadotte(1655,391)  Brunswick(1994,618)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  10k(2376,360)  4k(2461,645)  ?(2798,413)  4k(2126,239)  ?(1899,567)  2k(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0332  scroll 1828 548 down 6  ->  ok
  (scrolled down 6 at (1828, 548))
view: <run>\frames\0332_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier reports that Augereau appears envious of Davout's laurels — he has grown restless for glory.
   Augereau seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Oudinot's resentment of Murat is set aside. His rival's corps is broken or falling back — there is nothing in him to envy until it rallies.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map: unchanged (114 labels)
```

```
#0333  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0333_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt'], region_panel=no
── InterruptPopup (layer 103) ──
   BERNADOTTE REPORTS
   "Bernadotte: 'Cannon fire at Munich, Sire. Prussia and Bavaria are at war; France is not in it. Investigate?'"
   controls: [March to the Guns]  [Continue as Ordered]  [Hold Position]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   --- Strategic Order Updates ---
   Bernadotte: Bernadotte: 'Cannon fire at Munich, Sire. Prussia and Bavaria are at war; France is not in it. Investigate?'
   Napoleon: Napoleon's Guard is SPENT at Dresden — 739 men cannot buy another road, Sire. Fight to the last, or cut our way out.
   Bernadotte awaits your orders!
map: unchanged (114 labels)
```

```
#0334  click Continue as Ordered  ->  ok
  (clicked at (1829, 590))
view: <run>\frames\0334_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   PRUSSIA LOSSES
   BAVARIA LOSSES
   0
   0
   ⚔
   Brunswick ◆
   Deroy ◆
   32,103 → 30,702
   18,932 → 13,238
   SECOND BATTLE OF MUNICH
   click anywhere to skip ▸
   MUNICH · TURN 17
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Bernadotte: continue order
   Bernadotte reluctantly continues his march, ignoring cannon fire at Munich. Bernadotte marches to Swabia. 1 region to Franconia.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Napoleon(2376,248)  Davout(2061,426)  Murat(2090,392)  Massena(2118,358)  ?(2257,819)  Archduke John(2257,785)  Buxhowden(2471,539)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Bennigsen(2536,642)  Bernadotte(1871,455)  Deroy(1927,421)  Brunswick(1994,618)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  10k(2376,360)  4k(2461,645)  ?(2798,413)  4k(2126,239)  3k(1899,567)  2k(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0335  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Brunswick ◆' (Control, layer 121))
view: <run>\frames\0335_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   AN INDECISIVE ACTION
   PRUSSIA LOSSES
   BAVARIA LOSSES
   1,401
   5,694
   ⚔
   Brunswick ◆
   Deroy ◆
   32,103 → 30,702
   18,932 → 13,238
   ROUTED
   Berthier: “Even the favorable ground could not save Deroy, Sire. Brunswick overcame the terrain.”
   SECOND BATTLE OF MUNICH
   MUNICH · TURN 17
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Napoleon: Napoleon's Guard is SPENT at Dresden — 739 men cannot buy another road, Sire. Fight to the last, or cut our way out.
   Bernadotte awaits your orders!
   > Bernadotte: continue order
   Bernadotte reluctantly continues his march, ignoring cannon fire at Munich. Bernadotte marches to Swabia. 1 region to Franconia.
map: unchanged (113 labels)
```

```
#0336  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0336_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt'], region_panel=no
── InterruptPopup (layer 103) ──
   NAPOLEON REPORTS
   "Napoleon's Guard is SPENT at Dresden — 739 men cannot buy another road, Sire. Fight to the last, or cut our way out."
   controls: [Fight to the Last]  [Attempt a Breakout]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Napoleon awaits your orders!
map: unchanged (113 labels)
```

```
#0337  click Attempt a Breakout  ->  ok
  (clicked at (1971, 590))
view: <run>\frames\0337_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 84 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon's Guard is spent @(3351,64)]  [icon: The Fourth British Coalition Declared! @(3393,64)]  [icon: Coalition Brewing — 3 turns @(3435,64)]  [icon: Armistice Collapsed @(3477,64)]  [icon: Ney orders lost @(3519,64)]  [icon: Marshal Davout grows bitter @(3561,64)]  [+43]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +11
   T:2
   Russia
   -21
   T:5
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  2t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,824
   Inf:
   39,559
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [!] Davout's Counter-Punch opportunity has expired! (Must use immediately after defending)
   Dresden's garrison regains 78: 9,922 -> 10,000.
   Vienna's garrison regains 2,000: 2,000 -> 4,000.
   Holland loyalty 99 (+10): a common enemy
   Berthier notes that Oudinot no longer presses the matter — his quarrel with Murat has cooled.
   Berthier reports that Augereau appears envious of Davout's laurels — he has grown restless for glory.
   Augereau seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Oudinot's resentment of Murat is set aside. His rival's corps is broken or falling back — there is nothing in him to envy until it rallies.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   PRISONERS OF WAR
   Ney — held by Russia since turn 16.
   Soult — held by Russia since turn 17.
   Lannes — held by Prussia since turn 13.
   DIPLOMATIC EVENTS
   War exhaustion grows — France nears breaking point (exhaustion: 85).
   War exhaustion grows — Bavaria nears breaking point (exhaustion: 81).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Naples — the subsidy stands at 300 this season.
   REVANCHE: Bavaria will not forgive Prussia the loss of Franconia and 1 more province. A new design hardens in their court.
   The court of Bavaria takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Bohemia) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms — theirs to impose (-29)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+10)
   War Purpose: Defense vs Ottoman — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sweden — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Naples — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+10)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 84/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Mortier awaits a commission at 4,000g."
   ════════════════════════════════════
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Napoleon(2276,485)  Davout(2061,426)  Murat(2090,392)  Massena(2118,358)  ?(2257,819)  Archduke John(2257,785)  Buxhowden(2471,539)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Bennigsen(2536,642)  Bernadotte(1871,455)  Deroy(1927,421)  Brunswick(1994,618)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  10k(2376,360)  4k(2461,645)  ?(2798,413)  4k(2126,239)  3k(1899,567)  2k(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0338  type Napoleon, move to Franconia  ->  ok
  (typed and Enter)
view: <run>\frames\0338_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Cannot enter Franconia — it is controlled by Prussia (diplomatic state: ARMISTICE). Open borders or higher required.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 84 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Coalition Brewing — 3 turns @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Ney orders lost @(3477,64)]  [icon: Marshal Davout grows bitter @(3519,64)]  [icon: Marshal Massena grows bitter @(3561,64)]  [+42]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +9
   T:3
   Russia
   -30
   T:6
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  1t]
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, move to Franconia
   Cannot enter Franconia — it is controlled by Prussia (diplomatic state: ARMISTICE). Open borders or higher required.
map: unchanged (113 labels)
```

```
#0339  type Davout, move to Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0339_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Franconia to Bohemia (75 lost to march)
Tyrol lies undefended — an attack takes it.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/5
   Admin:
   2/2
   Gold:
   6,824
   Inf:
   39,559
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, move to Bohemia
   → Davout moves from Franconia to Bohemia (75 lost to march)
   Tyrol lies undefended — an attack takes it.
   [4/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2248,485)  Napoleon(2304,451)  Murat(2062,426)  Massena(2118,392)  ?(2257,819)  Archduke John(2257,785)  Buxhowden(2471,539)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Bennigsen(2536,642)  Bernadotte(1871,455)  Deroy(1927,421)  Brunswick(1994,618)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  10k(2376,360)  4k(2461,645)  ?(2798,413)  4k(2126,239)  3k(1899,567)  2k(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0340  type Murat, move to Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0340_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat moves from Franconia to Bohemia (81 lost to march)
Tyrol lies undefended — an attack takes it.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   3/5
   Admin:
   2/2
   Gold:
   6,824
   Inf:
   39,559
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Ney — held by Russia since turn 16.
   Soult — held by Russia since turn 17.
   Lannes — held by Prussia since turn 13.
   DIPLOMATIC EVENTS
   War exhaustion grows — France nears breaking point (exhaustion: 85).
   War exhaustion grows — Bavaria nears breaking point (exhaustion: 81).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Britain's gold reaches Naples — the subsidy stands at 300 this season.
   REVANCHE: Bavaria will not forgive Prussia the loss of Franconia and 1 more province. A new design hardens in their court.
   The court of Bavaria takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Bohemia) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms — theirs to impose (-29)
   War Purpose: Conquest vs Prussia — Berlin [not held]  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+10)
   War Purpose: Defense vs Ottoman — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sweden — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Naples — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+10)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 84/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Mortier awaits a commission at 4,000g."
   ════════════════════════════════════
   ► Napoleon, move to Franconia
   Cannot enter Franconia — it is controlled by Prussia (diplomatic state: ARMISTICE). Open borders or higher required.
   ► Davout, move to Bohemia
   → Davout moves from Franconia to Bohemia (75 lost to march)
   Tyrol lies undefended — an attack takes it.
   [4/5 actions remaining]
   ► Murat, move to Bohemia
   → Murat moves from Franconia to Bohemia (81 lost to march)
   Tyrol lies undefended — an attack takes it.
   [3/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout(2248,485)  Murat(2276,451)  Napoleon(2304,416)  Massena(2090,426)  ?(2257,819)  Archduke John(2257,785)  Buxhowden(2471,539)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Bennigsen(2536,642)  Bernadotte(1871,455)  Deroy(1927,421)  Brunswick(1994,618)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  10k(2376,360)  4k(2461,645)  ?(2798,413)  4k(2126,239)  3k(1899,567)  2k(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0341  type Massena, move to Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0341_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Massena moves from Franconia to Bohemia (92 lost to march)
Tyrol lies undefended — an attack takes it.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   6,824
   Inf:
   39,559
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, move to Bohemia
   → Massena moves from Franconia to Bohemia (92 lost to march)
   Tyrol lies undefended — an attack takes it.
   [2/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout +3(2277,461)  ?(2257,819)  Archduke John(2257,785)  Buxhowden(2471,539)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Bennigsen(2536,642)  Bernadotte(1871,455)  Deroy(1927,421)  Brunswick(1994,618)  Oudinot(1267,404)  Augereau(1323,370)  Dumonceau(1660,203)  Teulie(2015,742)  10k(2376,360)  4k(2461,645)  ?(2798,413)  4k(2126,239)  3k(1899,567)  2k(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0342  click THE FOURTH BRITISH COALITION  ->  ok
  (clicked at (3211, 895))
view: <run>\frames\0342_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'war_detail'], region_panel=no
── TopBar (layer 75): unchanged
── WarDetailPopup (layer 30) ──
   THE FOURTH BRITISH COALITION
   Britain
   BR
   0
   FR
   Austria
   AU
   +10
   FR
   Portugal
   PO
   −1
   FR
   Ottoman Empire
   OT
   0
   FR
   Saxony
   SA
   0
   FR
   Papal States
   PA
   0
   FR
   Sweden
   SW
   0
   FR
   Naples
   NA
   0
   FR
   Hanover
   HA
   0
   FR
   Sardinia
   SA
   0
   FR
   Russia
   RU
   −30
   FR
   Leader: Britain   Posture: Defensive /  /   Britain  Unknown  — leads the coalition /   Austria  WE:32  ~50,000 men /   Portugal  Unknown /   Ottoman Empire  Unknown /   Saxony  Unknown /   Papal States  Unknown /   Sweden  Considerable (last seen) /   Naples  Unknown /   Hanover  Unknown /   Sardinia  Unknown /   Russia  WE:63  35,031 men /  / Coordination /   Britain-Austria: Good /   Britain-Po …
   Coalition spans multiple wars; settle each separately.
   controls: [icon @(2702,276)]  [Target Austria]  [Target Portugal]  [Target Ottoman Empire]  [Target Saxony]  [Target Papal States]  [Target Sweden]  [Target Naples]  [Target Hanover]  [Target Sardinia]  [Target Russia]
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Massena, move to Bohemia
   → Massena moves from Franconia to Bohemia (92 lost to march)
   Tyrol lies undefended — an attack takes it.
   [2/5 actions remaining]
map: unchanged (111 labels)
```

```
#0343  click Target Saxony  ->  ok
  (clicked at (2376, 742))
view: <run>\frames\0343_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) ──
   DIPLOMACY — Saxony
   DP: 7
   TALLEYRAND'S ASSESSMENT — SAXONY / Status: At War   Relation: -50 (Hostile) /  / "The war with Saxony grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Talleyrand recommends: Propose Armistice /  / KEY FACTORS /   + Base willingness (+20) /   + Diplomatic skill advantage (+12) /   + Diplomat personality (+10) /   - Current relations (-10) …
   No alliance to undermine
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Uncertain — a counter is likely]  [Open Settlement]  [Propose White Peace]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5]  [Undermine Alliances (2 DP)  —  -4 relation between targets/turn](disabled: No alliance to undermine)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Massena, move to Bohemia
   → Massena moves from Franconia to Bohemia (92 lost to march)
   Tyrol lies undefended — an attack takes it.
   [2/5 actions remaining]
map: unchanged (111 labels)
```

```
#0344  click Propose Armistice  ->  ok
  (clicked at (1825, 459))
view: <run>\frames\0344_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   PEACE PREVIEW - Saxony /  / Proposed Terms /   * Armistice (cease hostilities temporarily) / Assessment: GENEROUS /  / Acceptance Estimate / Score: 42 - COUNTER expected / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / War score: 0 -> / Settlement: White Peace / Objective: Defense - the homeland — 28 of 28 provinces held (inactive) / Ticking: +0 / Duration: 3  …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 84 / 100
   Turn 18 — Early June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   6,824
   Inf:
   39,559
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose armistice with Saxony
map: unchanged (111 labels)
```

```
#0345  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0345_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   PEACE PREVIEW - Saxony /  / Proposed Terms / France concedes: /   • France pays 500 gold per turn to Saxony /  / Assessment: GENEROUS /  / Acceptance Estimate / Score: 57 - ACCEPT / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / War score: 0 -> / Settlement: White Peace / Objective: Defense - the homeland — 28 of 28 provinces held (inactive) / Ticking: +0 / Du …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (111 labels)
```

```
#0346  click Not Now  ->  ok
  (clicked at (2056, 727))
view: <run>\frames\0346_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 84 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Coalition Brewing — 3 turns @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Ney orders lost @(3477,64)]  [icon: Marshal Davout grows bitter @(3519,64)]  [icon: Marshal Massena grows bitter @(3561,64)]  [+42]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +9
   T:3
   Russia
   -30
   T:6
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  1t]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   2/5
   Admin:
   2/2
   Gold:
   6,824
   Inf:
   39,559
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (111 labels)
```

```
#0347  type recruit infantry for Oudinot  ->  ok
  (typed and Enter)
view: <run>\frames\0347_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Oudinot recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Oudinot's intendance: +15%). Morale: 52% -> 48%
Infantry pool: 39,559 -> 29,559
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   2/5
   Admin:
   1/2
   Gold:
   6,306
   Inf:
   29,559
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit infantry for Oudinot
   + Oudinot recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Oudinot's intendance: +15%). Morale: 52% -> 48%
   Infantry pool: 39,559 -> 29,559
   [2/5 actions remaining]
map: unchanged (111 labels)
```

```
#0348  type recruit artillery for Augereau  ->  ok
  (typed and Enter)
view: <run>\frames\0348_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Berthier notes: 'Marshal Augereau commands infantry, Sire.' Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 52% -> 48%
Infantry pool: 29,559 -> 19,559
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   2/5
   Admin:
   0/2
   Gold:
   5,788
   Inf:
   19,559
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► recruit artillery for Augereau
   + Berthier notes: 'Marshal Augereau commands infantry, Sire.' Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 52% -> 48%
   Infantry pool: 29,559 -> 19,559
   [2/5 actions remaining]
   ▸ The administration is spent: the order that spends your last action ends the turn at once.
map: unchanged (111 labels)
```

```
#0349  type Davout, fortify Bohemia  ->  ok
  (typed and Enter)
view: <run>\frames\0349_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   1/5
   Admin:
   0/2
   Gold:
   5,788
   Inf:
   19,559
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+10)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 84/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Mortier awaits a commission at 4,000g."
   ════════════════════════════════════
   ► Napoleon, move to Franconia
   Cannot enter Franconia — it is controlled by Prussia (diplomatic state: ARMISTICE). Open borders or higher required.
   ► Davout, move to Bohemia
   → Davout moves from Franconia to Bohemia (75 lost to march)
   Tyrol lies undefended — an attack takes it.
   [4/5 actions remaining]
   ► Murat, move to Bohemia
   → Murat moves from Franconia to Bohemia (81 lost to march)
   Tyrol lies undefended — an attack takes it.
   [3/5 actions remaining]
   ► Massena, move to Bohemia
   → Massena moves from Franconia to Bohemia (92 lost to march)
   Tyrol lies undefended — an attack takes it.
   [2/5 actions remaining]
   ► propose armistice with Saxony
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► recruit infantry for Oudinot
   + Oudinot recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Oudinot's intendance: +15%). Morale: 52% -> 48%
   Infantry pool: 39,559 -> 29,559
   [2/5 actions remaining]
   ► recruit artillery for Augereau
   + Berthier notes: 'Marshal Augereau commands infantry, Sire.' Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 52% -> 48%
   Infantry pool: 29,559 -> 19,559
   [2/5 actions remaining]
   ▸ The administration is spent: the order that spends your last action ends the turn at once.
   ► Davout, fortify Bohemia
   Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
   [1/5 actions remaining]
map: unchanged (111 labels)
```

```
#0350  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0350_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 18
   RUSSIA / ──────────────────────────── / - Buxhowden forms square / - Kutuzov holds position /  / PRUSSIA / ──────────────────────────── / - Brunswick attacks Deroy /     Third Battle of Swabia /     Brunswick: 702 casualties, 23,633 remaining /     Deroy: 9,137 casualties, 10,101 remaining /     Result: Attacker tactical victory (Brunswick victorious) /     Deroy forced to retreat! /     ⚔ View th …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 82 / 100
   Turn 19 — Late June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,900
   Inf:
   20,734
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► recruit infantry for Oudinot
   + Oudinot recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Oudinot's intendance: +15%). Morale: 52% -> 48%
   Infantry pool: 39,559 -> 29,559
   [2/5 actions remaining]
   ► recruit artillery for Augereau
   + Berthier notes: 'Marshal Augereau commands infantry, Sire.' Augereau recruits 10,000 infantry at Paris - Cost: 518 gold (capital discount) (×3 at war) (Augereau's intendance: +15%). Morale: 52% -> 48%
   Infantry pool: 29,559 -> 19,559
   [2/5 actions remaining]
   ▸ The administration is spent: the order that spends your last action ends the turn at once.
   ► Davout, fortify Bohemia
   Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
   [1/5 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 19 BEGINS
   ═══════════════════════════════════════
   Income: 2679g | Occupation: -70g | Charges of Empire: -689g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Blockade: -289g | Other: +1399g | Upkeep: -1508g | Net: +1112g | Spent: 1036g
   Treasury: 6,900g
   Actions refreshed: 5/5
   Davout's resolve hardens behind his earthworks (1/3) — his next assault will strike +8% harder. (Iron Resolve)
   Davout's fortifications strengthen: +12% defense (MAX)
   Murat's army is recovering. Effectiveness penalty: -15%.
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   Crowded at Bohemia: Davout loses 223 troops to the press of 4 corps on one province's roads
   Crowded at Bohemia: Murat loses 241 troops to the press of 4 corps on one province's roads
   Crowded at Bohemia: Massena loses 273 troops to the press of 4 corps on one province's roads
   Crowded at Bohemia: Napoleon loses 22 troops to the press of 4 corps on one province's roads
   Crowded at Hungary: Archduke Charles loses 810 troops to the press of 3 corps on one province's roads
   Crowded at Hungary: Archduke John loses 289 troops to the press of 3 corps on one province's roads
   Crowded at Hungary: Bennigsen loses 82 troops to the press of 3 corps on one province's roads
   Garrison at Vienna reinforced: 4,000 -> 6,000
   Garrison at Berlin reinforced: 4,000 -> 6,000
   Garrison at Munich reinforced: 2,000 -> 4,000
   The armistice between France and Prussia has concluded. Peace declared.
   Britain subsidizes Naples with 300 gold.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Tyrol(2102,763)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  Davout +3(2277,461)  Buxhowden(2471,539)  ?(2484,711)  Archduke Charles(2484,677)  ?(2519,711)  Archduke John(2519,642)  ?(2554,711)  Bennigsen(2554,608)  Bernadotte(1899,455)  ?(1834,109)  Yorck(1823,75)  ?(1793,533)  Deroy(1793,499)  Brunswick(1994,618)  Lannes(1267,404)  Oudinot(1295,370)  Augereau(1323,283)  Dumonceau(1660,203)  Teulie(2015,742)  10k(2376,360)  6k(2470,611)  ?(2798,413)  6k(2126,239)  1k(1899,567)  4k(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  ?(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0351  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0351_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   PRUSSIA LOSSES
   BAVARIA LOSSES
   0
   0
   ⚔
   Brunswick ◆
   Deroy ◆
   24,335 → 23,633
   19,238 → 10,101
   THIRD BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 18
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Armfelt — Stralsund — substantial force [last known - T11]
   Dresden garrison — Dresden — garrison of 10,000 [confirmed]
   Vienna garrison — Vienna — garrison of 6,000 [confirmed]
   Podolia garrison — Podolia — garrison — screening force [partial]
   Vilna garrison — Vilna — garrison — substantial force [stale - T16]
   TURN EVENTS
   Davout's fortifications strengthen: +12% defense (MAX)
   Murat's army is recovering. Effectiveness penalty: -15%.
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   Supply cost you 759 men, at Bohemia.
   Vienna's garrison regains 2,000: 4,000 -> 6,000.
   PRISONERS OF WAR
   Ney — held by Russia since turn 16.
   Soult — held by Russia since turn 17.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The armistice between France and Prussia has concluded. Peace declared.
   Britain's gold reaches Naples — the subsidy stands at 300 this season.
   The court of Britain hardens over The Low Countries — prepared now to go as far as war.
   The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Bohemia) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms — theirs to impose (-30)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+7)
   War Purpose: Defense vs Ottoman — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sweden — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Naples — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 82/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0352  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Brunswick ◆' (Control, layer 121))
view: <run>\frames\0352_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   AN INDECISIVE ACTION
   PRUSSIA LOSSES
   BAVARIA LOSSES
   702
   9,137
   ⚔
   Brunswick ◆
   Deroy ◆
   24,335 → 23,633
   19,238 → 10,101
   ROUTED
   Berthier: “Deroy's army has been badly mauled. Brunswick proved the stronger force today.”
   THIRD BATTLE OF SWABIA
   SWABIA · TURN 18
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 82/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0353  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0353_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   6,900
   Inf:
   20,734
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 82/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0354  click Moniteur  ->  ok
  (clicked at (515, 18))
view: <run>\frames\0354_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=['gazette'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 82 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Coalition Brewing — 3 turns @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Ney orders lost @(3477,64)]  [icon: Marshal Davout grows bitter @(3519,64)]  [icon: Marshal Massena grows bitter @(3561,64)]  [+44]
── GazetteView (layer 50) ──
   LE MONITEUR
   ════════════════════════════════════ /   LE MONITEUR — Paris, Early June 1806 /   SPECIAL EDITION — a capital stormed / ════════════════════════════════════ / The capital's press — the continent's story as printed, issue by issue. Page through the archive below. /  / From Vienna, the army executes a manoeuvre of the greatest delicacy; the situation develops. /  / — THE WAR — /   Third Battle of Vi …
   Issue 8 of 8
   controls: [Pin]  [icon @(2143,296)]  [< Earlier issue]  [Later issue >](disabled)
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 82/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0355  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0355_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +9
   T:3
   Russia
   -30
   T:6
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]  [Prussia  1t]
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 82/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
map: unchanged (115 labels)
```

```
#0356  type recruit infantry for Lannes  ->  ok
  (typed and Enter)
view: <run>\frames\0356_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Lannes recruits 10,000 infantry at Paris - Cost: 460 gold (capital discount) (×3 at war) (×1.02 over the ordinance). Morale: 50% -> 43%
Infantry pool: 20,734 -> 10,734
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +6
   T:4
   Russia
   -30
   T:7
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   5/5
   Admin:
   1/2
   Gold:
   6,440
   Inf:
   10,734
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Vilna garrison — Vilna — garrison — substantial force [stale - T16]
   TURN EVENTS
   Davout's fortifications strengthen: +12% defense (MAX)
   Murat's army is recovering. Effectiveness penalty: -15%.
   Massena's army is recovering. Effectiveness penalty: -25%. The rout's disorder lingers in the ranks.
   Napoleon's army is recovering. Effectiveness penalty: -15%. Napoleon rallies the survivors — the ranks reform ahead of schedule.
   Supply cost you 759 men, at Bohemia.
   Vienna's garrison regains 2,000: 4,000 -> 6,000.
   PRISONERS OF WAR
   Ney — held by Russia since turn 16.
   Soult — held by Russia since turn 17.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The armistice between France and Prussia has concluded. Peace declared.
   Britain's gold reaches Naples — the subsidy stands at 300 this season.
   The court of Britain hardens over The Low Countries — prepared now to go as far as war.
   The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Bohemia) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms — theirs to impose (-30)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+7)
   War Purpose: Defense vs Ottoman — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sweden — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Naples — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 82/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   ► recruit infantry for Lannes
   + Lannes recruits 10,000 infantry at Paris - Cost: 460 gold (capital discount) (×3 at war) (×1.02 over the ordinance). Morale: 50% -> 43%
   Infantry pool: 20,734 -> 10,734
   [5/5 actions remaining]
map: unchanged (115 labels)
```

```
#0357  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0357_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 19
   RUSSIA / ──────────────────────────── / - Bennigsen moves to Vienna / - Buxhowden attacks Massena /     Fourth Battle of Bohemia /     Buxhowden: 667 casualties, 10,923 remaining /     Massena's army: 3,173 casualties — Massena's own corps: 6,874 remaining /     Result: Attacker tactical victory (Buxhowden victorious) /     Massena forced to retreat! /     ⚔ View the field /     --- Berthier's Rep …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 80 / 100
   Turn 20 — Early July 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   7,146
   Inf:
   11,734
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   War Purpose: Defense vs Naples — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 82/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "I have ordered the remnants collected, Sire. Do not commit them until they reform."
   ════════════════════════════════════
   ► recruit infantry for Lannes
   + Lannes recruits 10,000 infantry at Paris - Cost: 460 gold (capital discount) (×3 at war) (×1.02 over the ordinance). Morale: 50% -> 43%
   Infantry pool: 20,734 -> 10,734
   [5/5 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 2663g | Requisitions: +37g | Occupation: -70g | Charges of Empire: -782g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Blockade: -265g | Materiel: -349g | Other: +1386g | Upkeep: -1504g | Net: +706g | Spent: 460g
   Treasury: 7,146g
   Actions refreshed: 5/5
   Davout's army is recovering. Effectiveness penalty: -15%. Davout rallies the survivors — the ranks reform ahead of schedule.
   Murat's army has fully recovered and is combat ready.
   Massena's army has fully recovered and is combat ready.
   Napoleon's army has fully recovered and is combat ready.
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Paris: Lannes loses 330 troops
   Supply shortage at Paris: Oudinot loses 770 troops
   Supply shortage at Paris: Augereau loses 770 troops
   Garrison at Vienna reinforced: 6,000 -> 8,000
   Garrison at Munich reinforced: 4,000 -> 6,000
   Relations between France and Spain have collapsed: Alliance → Defensive Alliance.
   Relations between Austria and Britain are deteriorating. Alliance may collapse in 2 turns.
   Britain subsidizes Austria with 300 gold.
   Berthier notes that Augereau no longer presses the matter — his quarrel with Davout has cooled.
   Oudinot's resentment of Davout is set aside. His rival's corps is broken or falling back — there is nothing in him to envy until it rallies.
   Berthier reports that Oudinot resents Murat's laurels again, 3 turns after the last — he has grown restless for glory.
   Augereau's resentment of Davout is set aside. His rival's corps is broken or falling back — there is nothing in him to envy until it rallies.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2925,71)  Kutuzov(2925,37)  Murat(2248,485)  Massena(2277,451)  Napoleon(2304,416)  Buxhowden(2443,539)  Bennigsen(2498,505)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Archduke John(2536,642)  Bernadotte(1871,455)  Deroy(1927,421)  ?(1834,109)  Yorck(1823,75)  Davout(2101,708)  Brunswick(1994,618)  Lannes(1267,404)  Oudinot(1295,370)  Augereau(1323,283)  Dumonceau(1660,203)  Teulie(2015,742)  10k(2376,360)  8k(2442,645)  ?(2798,413)  ?(2126,239)  1k(1899,567)  6k(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0358  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0358_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt'], region_panel=no
── InterruptPopup (layer 103) ──
   MASSENA REPORTS
   "Massena is cornered at Bohemia with 6,874 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout."
   controls: [Fight to the Last]  [Attempt a Breakout]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   --- Strategic Order Updates ---
   Massena: Massena is cornered at Bohemia with 6,874 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
   Murat: Murat is cornered at Bohemia with 3,990 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
   Massena awaits your orders!
map: unchanged (117 labels)
```

```
#0359  click Attempt a Breakout  ->  ok
  (clicked at (1971, 590))
view: <run>\frames\0359_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   PRUSSIA LOSSES
   BAVARIA LOSSES
   0
   0
   ⚔
   Brunswick ◆
   Deroy ◆
   22,792 → 22,415
   10,051 → 5,496
   BATTLE OF FRANCHE-COMTE
   click anywhere to skip ▸
   FRANCHE-COMTE · TURN 19
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   7,146
   Inf:
   15,171
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   > Massena: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Massena is taken by Russia at Bohemia! 3,437 of his men escape home to the depots.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2925,71)  Kutuzov(2925,37)  Murat(2248,485)  Napoleon(2304,451)  Buxhowden(2443,539)  Bennigsen(2498,505)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Archduke John(2536,642)  Bernadotte(1871,455)  Deroy(1927,421)  ?(1834,109)  Yorck(1823,75)  Davout(2101,708)  Brunswick(1994,618)  Lannes(1267,404)  Oudinot(1295,370)  Augereau(1323,283)  Dumonceau(1660,203)  Teulie(2015,742)  10k(2376,360)  8k(2442,645)  ?(2798,413)  ?(2126,239)  1k(1899,567)  6k(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0360  click_at 1800 900  ->  ok
  (clicked at (1800, 900) on Root 'Brunswick ◆' (Control, layer 121))
view: <run>\frames\0360_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   AN INDECISIVE ACTION
   PRUSSIA LOSSES
   BAVARIA LOSSES
   377
   4,555
   ⚔
   Brunswick ◆
   Deroy ◆
   22,792 → 22,415
   10,051 → 5,496
   ROUTED
   Berthier: “The toll on Deroy's forces is heavy, Sire. This defeat will be felt.”
   BATTLE OF FRANCHE-COMTE
   FRANCHE-COMTE · TURN 19
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Murat: Murat is cornered at Bohemia with 3,990 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
   Massena awaits your orders!
   > Massena: attempt breakout
   The breakout fails — [!] MARSHAL CAPTURED — Massena is taken by Russia at Bohemia! 3,437 of his men escape home to the depots.
map: unchanged (116 labels)
```

```
#0361  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0361_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['interrupt'], region_panel=no
── InterruptPopup (layer 103) ──
   MURAT REPORTS
   "Murat is cornered at Bohemia with 3,990 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout."
   controls: [Fight to the Last]  [Attempt a Breakout]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Murat awaits your orders!
map: unchanged (116 labels)
```

```
#0362  click Fight to the Last  ->  ok
  (clicked at (1686, 590))
view: <run>\frames\0362_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 80 / 100
   Turn 20 — Early July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Massena is cornered @(3351,64)]  [icon: Murat is cornered @(3393,64)]  [icon: The Fourth British Coalition Declared! @(3435,64)]  [icon: Coalition Brewing — 3 turns @(3477,64)]  [icon: Armistice Collapsed @(3519,64)]  [icon: Ney orders lost @(3561,64)]  [+44]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden
   +6
   T:4
   Russia
   -30
   T:7
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Portugal + Sardinia + Saxony + Sweden]  [Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   7,146
   Inf:
   15,171
   Cav:
   31,995
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Vilna garrison — Vilna — garrison — substantial force [stale - T16]
   TURN EVENTS
   Davout's army is recovering. Effectiveness penalty: -15%. Davout rallies the survivors — the ranks reform ahead of schedule.
   Murat's army has fully recovered and is combat ready.
   Massena's army has fully recovered and is combat ready.
   Napoleon's army has fully recovered and is combat ready.
   Supply cost you 1,870 men, at Paris.
   Vienna's garrison regains 2,000: 6,000 -> 8,000.
   Berthier notes that Augereau no longer presses the matter — his quarrel with Davout has cooled.
   Oudinot's resentment of Davout is set aside. His rival's corps is broken or falling back — there is nothing in him to envy until it rallies.
   Berthier reports that Oudinot resents Murat's laurels again, 3 turns after the last — he has grown restless for glory.
   Augereau's resentment of Davout is set aside. His rival's corps is broken or falling back — there is nothing in him to envy until it rallies.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   PRISONERS OF WAR
   Ney — held by Russia since turn 16.
   Soult — held by Russia since turn 17.
   DIPLOMATIC EVENTS
   Sire — Portugal has been eliminated from the war.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Relations between France and Spain have collapsed: Alliance → Defensive Alliance.
   Britain's gold reaches Austria — the subsidy stands at 300 this season.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Bohemia) · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms — theirs to impose (-34)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+4)
   War Purpose: Defense vs Ottoman — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sweden — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Naples — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 80/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "One enemy the fewer, Sire. Every court in Europe is doing its arithmetic tonight."
   ════════════════════════════════════
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2925,71)  Kutuzov(2925,37)  Napoleon(2276,485)  Buxhowden(2443,539)  Bennigsen(2498,505)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Archduke John(2536,642)  Bernadotte(1871,455)  Deroy(1927,421)  ?(1834,109)  Yorck(1823,75)  Davout(2101,708)  Brunswick(1994,618)  Lannes(1267,404)  Oudinot(1295,370)  Augereau(1323,283)  Dumonceau(1660,203)  Teulie(2015,742)  10k(2376,360)  8k(2442,645)  ?(2798,413)  ?(2126,239)  1k(1899,567)  6k(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0363  type where is Murat  ->  ok
  (typed and Enter)
view: <run>\frames\0363_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."

What I CAN do today:
  Napoleon, attack Buxhowden
  Davout, march to Bohemia
  enact the Train des Équipages — 3,500g, then 200g a turn (cures Living off the land — the court's doctrine flaw — while its Staff stands); the Charges of Empire fall by 681g a turn
  recruit infantry in Paris — 518g for 10,000 men under Oudinot

For any matter of state, press F1 for the Cabinet.
Type 'help' for the full command reference.
── TopBar (layer 75) ──
   DP: 7/7
   Threat 80 / 100
   Turn 20 — Early July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Coalition Brewing — 3 turns @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Ney orders lost @(3477,64)]  [icon: Marshal Davout grows bitter @(3519,64)]  [icon: Marshal Massena grows bitter @(3561,64)]  [+42]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Sardinia + Saxony + Sweden
   +4
   T:5
   Russia
   -35
   T:8
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Sardinia + Saxony + Sweden]  [Russia]
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► where is Murat
   Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
   What I CAN do today:
   Napoleon, attack Buxhowden
   Davout, march to Bohemia
   enact the Train des Équipages — 3,500g, then 200g a turn (cures Living off the land — the court's doctrine flaw — while its Staff stands); the Charges of Empire fall by 681g a turn
   recruit infantry in Paris — 518g for 10,000 men under Oudinot
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
map: unchanged (115 labels)
```

```
#0364  type Napoleon, move to Tyrol  ->  ok
  (typed and Enter)
view: <run>\frames\0364_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Napoleon moves from Bohemia to Tyrol. Tyrol lies open, but Napoleon's 714 men are a raiding party, not an army — a corps under 5,000 holds no homeland province it walks onto. (14 lost to march)
Carniola lies undefended — an attack takes it.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/5
   Admin:
   2/2
   Gold:
   7,146
   Inf:
   15,171
   Cav:
   31,995
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Napoleon, move to Tyrol
   → Napoleon moves from Bohemia to Tyrol. Tyrol lies open, but Napoleon's 714 men are a raiding party, not an army — a corps under 5,000 holds no homeland province it walks onto. (14 lost to march)
   Carniola lies undefended — an attack takes it.
   [4/5 actions remaining]
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,560)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Bern(1691,635)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2925,71)  Kutuzov(2925,37)  Buxhowden(2443,539)  Bennigsen(2498,505)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Archduke John(2536,642)  Bernadotte(1871,455)  Deroy(1927,421)  ?(1834,109)  Yorck(1823,75)  Davout(2073,708)  Napoleon(2129,674)  Brunswick(1994,618)  Lannes(1267,404)  Oudinot(1295,370)  Augereau(1323,283)  Dumonceau(1660,203)  Teulie(2015,742)  10k(2376,360)  8k(2442,645)  ?(2798,413)  ?(2126,239)  1k(1899,567)  6k(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0365  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0365_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 21 — Late July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 20
   PRUSSIA / ──────────────────────────── / - Yorck moves to Berlin / - Yorck moves to Franconia / - Yorck moves to Munich / - Brunswick recruits troops /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 78 / 100
   Turn 21 — Late July 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   21
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   8,115
   Inf:
   16,171
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 80/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "One enemy the fewer, Sire. Every court in Europe is doing its arithmetic tonight."
   ════════════════════════════════════
   ► where is Murat
   Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
   What I CAN do today:
   Napoleon, attack Buxhowden
   Davout, march to Bohemia
   enact the Train des Équipages — 3,500g, then 200g a turn (cures Living off the land — the court's doctrine flaw — while its Staff stands); the Charges of Empire fall by 681g a turn
   recruit infantry in Paris — 518g for 10,000 men under Oudinot
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
   ► Napoleon, move to Tyrol
   → Napoleon moves from Bohemia to Tyrol. Tyrol lies open, but Napoleon's 714 men are a raiding party, not an army — a corps under 5,000 holds no homeland province it walks onto. (14 lost to march)
   Carniola lies undefended — an attack takes it.
   [4/5 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 21 BEGINS
   ═══════════════════════════════════════
   Income: 2666g | Requisitions: +37g | Occupation: -70g | Charges of Empire: -1000g | Laws: -300g | Infrastructure: -20g | Admiralty: -90g | Blockade: -265g | Other: +1411g | Upkeep: -1400g | Net: +969g
   Treasury: 8,115g
   Actions refreshed: 5/5
   Davout's army has fully recovered and is combat ready.
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Hungary: Archduke Charles loses 501 troops
   Supply shortage at Hungary: Archduke John loses 199 troops
   Supply shortage at Paris: Lannes loses 317 troops
   Supply shortage at Paris: Oudinot loses 740 troops
   Supply shortage at Paris: Augereau loses 740 troops
   Garrison at Munich reinforced: 6,000 -> 8,000
   Switzerland sends 4,500 men under Amey to the colours at Bern — they await the orders of France. The nearest host is Bernadotte at Swabia. Switzerland pays them; their dead will be its grief.
   Britain subsidizes Naples with 300 gold.
   Augereau's resentment of Murat is set aside. There is no one left to envy.
   Berthier reports that Augereau resents Davout's laurels again, 3 turns after the last — he has grown restless for glory.
   Oudinot's resentment of Murat is set aside. There is no one left to envy.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map names: White Russia(3299,-91)  Anatolia(2873,1071)  Silesia(2673,204)  Karaman(3173,1130)  Dresden(2376,303)  Lithuania(2925,123)  Bohemia(2276,539)  Berry(1133,591)  Volhynia(3091,137)  East Prussia(2516,-97)  Franconia(2090,481)  Carniola(2257,871)  Trebizond(3289,926)  Piedmont(1681,857)  Vienna(2470,594)  Albania(2333,1138)  Samogitia(2682,-85)  Podolia(2799,356)  Berlin(2126,182)  Moravia(2666,551)  Hungary(2519,763)  Posen(2407,54)  Artois(1342,316)  Croatia(2506,895)  Rome(1921,1051)  Beira(526,1121)  Ukraine(2935,433)  Midlands(985,98)  Rhineland(1824,356)  Brunswick(1834,162)  Gascony(1079,816)  Ulster(670,-41)  Limousin(1305,619)  Anjou(955,576)  Lorraine(1655,445)  Munster(626,88)  Lyonnais(1405,686)  Cornwall(864,256)  New Russia(2966,557)  Savoy(1612,691)  Brandenburg(2284,26)  Maine(1032,429)  Franche-Comte(1793,585)  Jutland(1574,-115)  Northumbria(973,-47)  Wales(836,134)  Porto(305,1061)  Orleanais(1523,456)  Languedoc(1280,807)  Madrid(679,1124)  Pomerania(2204,-22)  Constantinople(2706,1004)  Brittany(839,497)  Oldenburg(1536,135)  Cagliari(1464,1095)  Frankfurt(1975,253)  Nivernais(1645,558)  Burgundy(1499,580)  Gelderland(1789,256)  Champagne(1416,432)  Normandy(1194,360)  Stralsund(2066,70)  Holstein(1891,84)  Schleswig(1571,35)  Nassau(1978,361)  Brabant(1636,335)  Provence(1438,760)  Hanover(1711,88)  East Anglia(1094,175)  Westphalia(1494,214)  Rumelia(2646,949)  East Frisia(1413,165)  Flanders(1571,273)  Osnabruck(1628,170)  Picardy(1514,307)  Scania(1684,-49)  Corsica(1477,929)  London(1054,276)  Wessex(1024,241)  Balearics(1048,1108)
map pieces: 100(839,294)  45(789,746)  15(2757,844)  12(1289,64)  ?(2453,542)  Buxhowden(2453,507)  ?(2488,542)  Bennigsen(2488,473)  ?(2501,711)  Archduke Charles(2501,677)  ?(2537,711)  Archduke John(2536,642)  Bernadotte(1899,455)  ?(1824,323)  Deroy(1824,289)  Davout(2073,708)  Napoleon(2129,674)  Brunswick(1966,618)  Yorck(2022,584)  Lannes(1267,404)  Oudinot(1295,370)  Augereau(1323,283)  Amey(1691,591)  Dumonceau(1660,203)  Teulie(2015,742)  ?(2376,360)  ?(2442,645)  ?(2798,413)  ?(2126,239)  1k(1899,567)  8k(1994,710)  ?(1975,310)  25k(1294,516)  12k(1193,417)  10k(1691,692)  10k(1660,304)  12k(1571,330)  10k(2014,854)
```

```
#0366  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0366_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 21 — Late July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 78 / 100
   Turn 21 — Late July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: The Fourth British Coalition Declared! @(3351,64)]  [icon: Coalition Brewing — 3 turns @(3393,64)]  [icon: Armistice Collapsed @(3435,64)]  [icon: Ney orders lost @(3477,64)]  [icon: Marshal Davout grows bitter @(3519,64)]  [icon: Armistice Concluded @(3561,64)]  [+40]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Sardinia + Saxony + Sweden
   +3
   T:6
   Russia
   -35
   T:9
   controls: [THE FOURTH BRITISH COALITION  ▸]  [Britain + Austria + Hanover + Naples + Ottoman Empire + Papal States + Sardinia + Saxony + Sweden]  [Russia]
── BottomLeftUI (layer 0) ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   21
   Actions:
   5/5
   Admin:
   2/2
   Gold:
   8,115
   Inf:
   16,171
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Podolia garrison — Podolia — garrison — screening force [stale - T18]
   TURN EVENTS
   Davout's army has fully recovered and is combat ready.
   Supply cost you 1,797 men, at Paris.
   Augereau's resentment of Murat is set aside. There is no one left to envy.
   Berthier reports that Augereau resents Davout's laurels again, 3 turns after the last — he has grown restless for glory.
   Oudinot's resentment of Murat is set aside. There is no one left to envy.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   PRISONERS OF WAR
   Ney — held by Russia since turn 16.
   Soult — held by Russia since turn 17.
   Murat — held by Austria since turn 20.
   Massena — held by Russia since turn 20.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Switzerland sends 4,500 men under Amey to the colours at Bern — they await the orders of France. The nearest host is Bernadotte at Swabia. Switzerland pays them; their dead will be its grief.
   Britain's gold reaches Naples — the subsidy stands at 300 this season.
   REVANCHE: Ottoman Empire will not forgive Spain the loss of Oran and 1 more province. A new design hardens in their court.
   The court of Ottoman Empire takes up a new design: Revanche.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled (1 held, unsettled: Bohemia) · summon from the Cabinet (F1)
   DIPLOMATIC STATUS
   Sire, the diplomatic front has been quiet. Perhaps too quiet. Shall I assess our options?
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms — theirs to impose (-35)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+3)
   War Purpose: Defense vs Ottoman — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sweden — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Naples — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Portugal — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Saxony — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Papal States — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Sardinia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 78/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Mortier awaits a commission at 4,000g."
   ════════════════════════════════════
map: unchanged (118 labels)
```

```
#0367  quit  ->  ok
  (the engine quits)
view: <run>\frames\0367_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 21 — Late July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 78/100 [Formed]
   ACTIVE: The Fourth British Coalition — Leader: Britain
   Berthier: "We must consider his ransom, Sire — or make his captors regret the keeping. And the Marshalate holds men yet, Sire — Mortier awaits a commission at 4,000g."
   ════════════════════════════════════
map: unchanged (118 labels)
```

