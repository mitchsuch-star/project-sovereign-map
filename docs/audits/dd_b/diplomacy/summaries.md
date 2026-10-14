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
── PaintingCaption (layer 0): unchanged
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
── BottomLeftUI (layer 0) [scrolled 1323 of 1323 px] ──
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
#0004  click ⚖ Diplomacy  ->  ok
  (clicked at (829, 978))
view: <run>\frames\0004_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   At War (3)
   Treaties (2)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1323 of 1323 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0005  click Austria  —  At War  ->  ok
  (clicked at (1825, 601))
view: <run>\frames\0005_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 222 px, 0 of 159 px] ──
   DIPLOMACY — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War   Relation: -80 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus. /  / KEY FACTORS /   + Base willingness (+20) /   + Diplomat personality (+ …
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Hopeless]  [Open Settlement]  [Propose White Peace]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5]  [Undermine Alliances (2 DP)  —  -4 relation between targets/turn]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1323 of 1323 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   ─────────────────────────────────────
map: unchanged (53 labels)
```

```
#0006  click Propose White Peace  ->  ok
  (clicked at (1825, 535))
view: <run>\frames\0006_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 156 px] ──
   This settlement cannot be ratified now. / France vs Austria + Britain + Russia - Whole-war settlement / STAGED FOR REVIEW — the terms are frozen. Ratify, revise, or return to shaping. / ▸ Blocked: Settlement legitimacy / ▸ Holding out: Austria, Britain, Russia / Covered enemies: Austria, Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria -8/50, Britain -8 …
   The table /   * Austria - Holding out (-8/50) White peace /       Blocker: Settlement legitimacy /       Metternich regrets that Austria must remain… unconvinced — it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. /   * Britain - Holding out (-8/50) White peace /       Blocker: Settlement legitimacy /       Castlereagh declines for …
   Sire, a white peace for France vs Austria + Britain + Russia cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. Author terms or hold until the field shifts. Vienna, London and Vilna are unbeaten — a whole-war peace needs their consent (Austria -8/50, Britain -8/50, Russia -8/50). /  / Allies and Standi …
   controls: [Make peace with Austria only]  [Armistice with Austria only]  [Open War Detail]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1368 of 1368 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose white peace with Austria  (sent from the diplomacy screen — typed, this line would propose a peace treaty with terms)
map: unchanged (53 labels)
```

```
#0007  click Make peace with Austria only  ->  ok
  (clicked at (1455, 884))
view: <run>\frames\0007_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   Leave the joint settlement? / France vs Austria + Britain + Russia /  / Treat with Austria alone — every other court keeps its war. / Set aside the joint settlement; the other courts stay at war. Your drafted terms for Austria carry into the talks. / The joint draft stays untouched if you cancel. /  / "Sire, this sets aside the joint settlement of France vs Austria + Britain + Russia to treat with …
   controls: [Proceed — peace with Austria alone]  [Stay with the joint settlement]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1389 of 1389 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: seek bilateral peace
map: unchanged (53 labels)
```

```
#0008  click Proceed — peace with Austria alone  ->  ok
  (clicked at (1615, 727))
view: <run>\frames\0008_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 376 px] ──
   PEACE PREVIEW - Austria /  / Proposed Terms /   * Peace Treaty (end state of war) / Assessment: GENEROUS /  / Acceptance Estimate / Score: 14 - REJECT / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / War score: 0 -> / Settlement: White Peace / Objective: Defense - the homeland — 28 of 28 provinces held (inactive) / Ticking: +0 / Duration: 0 turns   Battles: 0W …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested](disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is )  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1411 of 1411 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: confirm pair substitute
map: unchanged (53 labels)
```

```
#0009  scroll 1820 500 down 5  ->  ok
  (scrolled down 5 at (1820, 500))
view: <run>\frames\0009_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 220 of 376 px] ──
   PEACE PREVIEW - Austria /  / Proposed Terms /   * Peace Treaty (end state of war) / Assessment: GENEROUS /  / Acceptance Estimate / Score: 14 - REJECT / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / War score: 0 -> / Settlement: White Peace / Objective: Defense - the homeland — 28 of 28 provinces held (inactive) / Ticking: +0 / Duration: 0 turns   Battles: 0W …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested](disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is )  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1411 of 1411 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ─────────────────────────────────────
   ► propose white peace with Austria  (sent from the diplomacy screen — typed, this line would propose a peace treaty with terms)
   Directing Talleyrand: seek bilateral peace
   Directing Talleyrand: confirm pair substitute
map: unchanged (53 labels)
```

```
#0010  click Not Now  ->  ok
  (clicked at (1829, 727))
view: <run>\frames\0010_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   0
   T:0
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [scrolled 1477 of 1477 px] ──
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
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (53 labels)
```

```
#0011  type how can I make peace with Austria?  ->  ok
  (typed and Enter)
view: <run>\frames\0011_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
reply: ok I must warn you — my information is incomplete. Proceed with caution. We are at war with Austria, Sire. War score stands at 0 from our perspective. Their military strength is overmatched relative to ours. Metternich is calculating — skill 9. Embattled, but allied with Russia, Britain.
── ProposalConfirmPopup (layer 110) ──
   TALLEYRAND'S ASSESSMENT — Austria /  / "I must warn you — my information is incomplete. Proceed with caution. We are at war with Austria, Sire. War score stands at 0 from our perspective. Their military strength is overmatched relative to ours. Metternich is calculating — skill 9. Embattled, but allied with Russia, Britain."
   controls: [icon: Close (Esc) @(2151,292)]  [What terms would they accept?]  [Thank you]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1523 of 1523 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► how can I make peace with Austria?
map: unchanged (53 labels)
```

```
#0012  click What terms would they accept?  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0012_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Austria /  /  / "Sire, the war with Austria is at a standstill. Neither side has won a decisive advantage on the battlefield."
   controls: [icon: Close (Esc) @(2151,292)]  [Propose peace]  [Press advantage]  [Wait]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1545 of 1545 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: expand to proposal
map: unchanged (53 labels)
```

```
#0013  click Wait  ->  ok
  (clicked at (2056, 727))
view: <run>\frames\0013_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   0
   T:0
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [scrolled 1611 of 1611 px] ──
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
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (53 labels)
```

```
#0014  click Diplomacy (D)  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0014_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 3017 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 5/5
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  / How Europe Reads France /   Read as: The hegemon of Europe — 40% of the continent's weight. /   The courts believe he will go as far as war (alarm 70). /   They think he is coming for Hesse — his corps stand against their soil. /  / The Emperor's …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1611 of 1611 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► how can I make peace with Austria?
   Directing Talleyrand: expand to proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (53 labels)
```

```
#0015  click Pin  ->  ok
  (clicked at (2171, 236))
view: <run>\frames\0015_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 2555 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 5/5
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  / How Europe Reads France /   Read as: The hegemon of Europe — 40% of the continent's weight. /   The courts believe he will go as far as war (alarm 70). /   They think he is coming for Hesse — his corps stand against their soil. /  / The Emperor's …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   0
   T:0
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [scrolled 1765 of 1765 px] ──
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
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► how can I make peace with Austria?
   Directing Talleyrand: expand to proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
map names: Russia(1858,232)  Ottoman Empire(1672,740)  Prussia(1490,310)  Sweden(1281,93)  Saxony(1454,404)  Austria(1465,576)  France(982,525)  Bavaria(1295,499)  Kingdom of Italy(1161,645)  Denmark(1137,128)  Papal States(1255,731)  Britain(846,315)  Hanover(1127,350)  Naples(1193,839)  Sardinia(1056,750)  Hesse(1279,403)  Holland(1137,389)  Switzerland(1155,549)
map pieces: 100(782,395)  45(761,592)  30(802,737)  20(1358,161)  18(1334,118)  15(1621,635)  12(979,294)  10(497,753)  10(1313,239)  5(1191,784)  Bernadotte(1316,451)  Deroy(1341,425)  ?(1346,325)  Brunswick(1345,287)  Mack(1240,430)  Ney(1200,397)  Davout(1226,371)  ?(1351,579)  Archduke John(1335,540)  Soult(1127,436)  Napoleon(1151,462)  Lannes(1187,497)  Murat(1224,471)  Massena(1297,589)  ?(1455,435)  ?(1346,376)  ?(1247,560)  ?(1279,372)  25k(982,494)  12k(938,454)  ?(1155,580)  12k(1080,420)  10k(1297,645)
```

```
#0016  scroll 3000 600 down 8  ->  ok
  (scrolled down 8 at (3000, 600))
view: <run>\frames\0016_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 835 of 2554 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 5/5
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  / How Europe Reads France /   Read as: The hegemon of Europe — 40% of the continent's weight. /   The courts believe he will go as far as war (alarm 70). /   They think he is coming for Hesse — his corps stand against their soil. /  / The Emperor's …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1765 of 1765 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► how can I make peace with Austria?
   Directing Talleyrand: expand to proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (51 labels)
```

```
#0017  scroll 3000 600 down 10  ->  ok
  (scrolled down 10 at (3000, 600))
view: <run>\frames\0017_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 1893 of 2555 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 5/5
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  / How Europe Reads France /   Read as: The hegemon of Europe — 40% of the continent's weight. /   The courts believe he will go as far as war (alarm 70). /   They think he is coming for Hesse — his corps stand against their soil. /  / The Emperor's …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1765 of 1765 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► how can I make peace with Austria?
   Directing Talleyrand: expand to proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (51 labels)
```

```
#0018  click CONGRESS  ->  ok
  (clicked at (3119, 113))
view: <run>\frames\0018_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 68 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 5/5
   ═══ THE CONGRESS OF PARIS ═══ / Europe must RECOGNIZE the new order. With 45 titled provinces the Emperor may summon the great powers to Paris; each answers at every end turn, with its reason and its price, and the Congress sits 8 turns. If on the last day every court recognizes, is shut out or is gone, and the hold never broke, the Imperial Peace is proclaimed. /  / THE CONGRESS OF PARIS — 35 of  …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS](disabled: You are reading this book)  <Open the Cabinet at London →>  <Open the Cabinet at St Petersburg →>  <Open the Cabinet at Vienna →>  <Open the Cabinet at Berlin →>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1765 of 1765 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► how can I make peace with Austria?
   Directing Talleyrand: expand to proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (51 labels)
```

```
#0019  click TALLEYRAND  ->  ok
  (clicked at (2829, 113))
view: <run>\frames\0019_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) ──
   DIPLOMATIC LEDGER
   Talleyrand: Idle
   DP: 5/5
   TALLEYRAND — Divine Right / Authority: 100/100   Skill: 10   DP: 5/5 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Idle — no active diplomatic mission. /  / PROPOSAL IN TRANSIT /   None /  / PENDING ENVOYS /   0 envoys awaiting response /  / SABOTAGE WARNINGS /   None detected. /  / DIPLOMAT …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1765 of 1765 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► how can I make peace with Austria?
   Directing Talleyrand: expand to proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (51 labels)
```

```
#0020  click Assess the Situation  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0020_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 134 px] ──
   TALLEYRAND'S ASSESSMENT /  / "Sire — the state of Europe, plainly told. /  /   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1) /  /   Against Britain + Austria + Russia: the war hangs in the balance (+0) — 0 battles across 0 turns. /     Britain's design: The Low Countries — They will not suffer France's bloc in Flanders. /     Their price: prepared to go as far as war — Fra …
   controls: [icon: Close (Esc) @(2151,292)]  [Satisfy their design (Britain)]  [Thank you]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1810 of 1810 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Talleyrand, assess our situation
map: unchanged (51 labels)
```

```
#0021  scroll 1820 500 down 5  ->  ok
  (scrolled down 5 at (1820, 500))
view: <run>\frames\0021_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 110 of 134 px] ──
   TALLEYRAND'S ASSESSMENT /  / "Sire — the state of Europe, plainly told. /  /   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1) /  /   Against Britain + Austria + Russia: the war hangs in the balance (+0) — 0 battles across 0 turns. /     Britain's design: The Low Countries — They will not suffer France's bloc in Flanders. /     Their price: prepared to go as far as war — Fra …
   controls: [icon: Close (Esc) @(2151,292)]  [Satisfy their design (Britain)]  [Thank you]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1810 of 1810 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: expand to proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
   ► Talleyrand, assess our situation
map: unchanged (51 labels)
```

```
#0022  click Satisfy their design (Britain)  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0022_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Britain /  /  / "Sire, the war with Britain is at a standstill. Neither side has won a decisive advantage on the battlefield."
   controls: [icon: Close (Esc) @(2151,292)]  [Propose peace]  [Press advantage]  [Wait]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1832 of 1832 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: expand options
map: unchanged (51 labels)
```

```
#0023  click Propose peace  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0023_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1854 of 1854 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: execute proposal
map: unchanged (51 labels)
```

```
#0024  look  ->  ok
  (a fresh frame)
view: <run>\frames\0024_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1854 of 1854 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Very well, Sire.
   ► Talleyrand, assess our situation
   Directing Talleyrand: expand options
   Directing Talleyrand: execute proposal
map: unchanged (51 labels)
```

```
#0025  click Propose peace  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0025_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1876 of 1876 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: execute proposal
map: unchanged (51 labels)
```

```
#0026  click Wait  ->  ok
  (clicked at (2056, 727))
view: <run>\frames\0026_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   0
   T:0
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [scrolled 1942 of 1942 px] ──
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
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (51 labels)
```

```
#0027  click ⚖ Diplomacy  ->  ok
  (clicked at (509, 978))
view: <run>\frames\0027_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   At War (3)
   Treaties (2)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1942 of 1942 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: execute proposal
   Directing Talleyrand: execute proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (51 labels)
```

```
#0028  scroll 1825 600 down 5  ->  ok
  (scrolled down 5 at (1825, 600))
view: <run>\frames\0028_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 222 of 662 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (2)
   Vassals (3)
   Neutral (11)
   controls: [icon: Close (Esc) @(2075,284)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1942 of 1942 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: execute proposal
   Directing Talleyrand: execute proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (51 labels)
```

```
#0029  scroll 1825 600 down 5  ->  ok
  (scrolled down 5 at (1825, 600))
view: <run>\frames\0029_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 428 of 627 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (11)
   controls: [icon: Close (Esc) @(2075,284)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Prussia  —  Peace  |  -10 (Wary)]  [Ottoman Empire  —  Peace  |  -20 (Wary)]  [Sweden  —  Peace  |  -60 (Hostile)]  [Naples  —  Peace  |  -30 (Hostile)]  [Portugal  —  Peace  |  -10 (Wary)]  [Denmark  —  Peace  |  +10 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1942 of 1942 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: execute proposal
   Directing Talleyrand: execute proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (51 labels)
```

```
#0030  click Prussia  —  Peace  ->  ok
  (clicked at (1825, 482))
view: <run>\frames\0030_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 244 px, 0 of 300 px] ──
   DIPLOMACY — Prussia
   DP: 5
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Peace   Relation: -10 (Wary) /  / "Prussia maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. Courting Prussia would be quicker — ≈4 turns again …
   Their price is 1128g — the treasury holds 800g.
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends]  [Buy Off Their Design (1128g) (1 DP + 1128g)  —  The design sleeps while the bargain stands — and waking it by betrayal i](disabled: Their price is 1128g — the treasury holds 800g.)  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Open Borders (1 DP)  —  Unlikely]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1942 of 1942 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: execute proposal
   Directing Talleyrand: execute proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (51 labels)
```

```
#0031  scroll 1825 380 down 5  ->  ok
  (scrolled down 5 at (1825, 380))
view: <run>\frames\0031_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 110 of 244 px, 0 of 300 px] ──
   DIPLOMACY — Prussia
   DP: 5
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Peace   Relation: -10 (Wary) /  / "Prussia maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. Courting Prussia would be quicker — ≈4 turns again …
   Their price is 1128g — the treasury holds 800g.
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends]  [Buy Off Their Design (1128g) (1 DP + 1128g)  —  The design sleeps while the bargain stands — and waking it by betrayal i](disabled: Their price is 1128g — the treasury holds 800g.)  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Open Borders (1 DP)  —  Unlikely]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1942 of 1942 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: execute proposal
   Directing Talleyrand: execute proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (51 labels)
```

```
#0032  scroll 1825 600 down 5  ->  ok
  (scrolled down 5 at (1825, 600))
view: <run>\frames\0032_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 110 of 244 px, 234 of 302 px] ──
   DIPLOMACY — Prussia
   DP: 5
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Peace   Relation: -10 (Wary) /  / "Prussia maintains a cautious distance. Their diplomats watch our moves with calculating eyes. Open borders would test their appetite." / Recommendation: No proposal would find purchase now. Talleyrand recommends: Improve Relations mission to warm the diplomatic climate. Courting Prussia would be quicker — ≈4 turns again …
   controls: [icon: Close (Esc) @(2075,284)]  [Declare War (1 DP)]  [Send Ultimatum (2 DP)]  [Improve Relations (1 DP)  —  +8 relation/turn]  [Court Nation (2 DP)  —  +8 relation/turn, proposals +2/turn courted (max +10), 20% blowback]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1942 of 1942 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: execute proposal
   Directing Talleyrand: execute proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
map: unchanged (51 labels)
```

```
#0033  click Court Nation (2 DP)  ->  ok
  (clicked at (1825, 593))
view: <run>\frames\0033_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Prussia /  / "Sire, I shall begin efforts to court and charm Prussia. This will cost 2 DP per turn." /  / DP cost: 2/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1988 of 1988 px] ──
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► court Prussia
map: unchanged (51 labels)
```

```
#0034  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0034_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]
── DiplomaticLedger (layer 50) ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/5
   TALLEYRAND — Divine Right / Authority: 100/100   Skill: 10   DP: 5/5 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary (+0 over 0 turns) /   Status: Active, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, now +0);  …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   0
   T:0
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [scrolled 2053 of 2053 px] ──
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
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: start mission
   Talleyrand begins efforts to court and charm Prussia. (2 DP/turn)
map: unchanged (51 labels)
```

```
#0035  type how strong is Mack's army in Swabia?  ->  ok
  (typed and Enter)
view: <run>\frames\0035_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Yes, Sire — Mack stands at Swabia — large force; his works and stance are not in view.
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2141 of 2141 px] ──
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
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► how strong is Mack's army in Swabia?
   Yes, Sire — Mack stands at Swabia — large force; his works and stance are not in view.
map: unchanged (51 labels)
```

```
#0036  type Murat, scout Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0036_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat scouts Swabia: Controlled by Bavaria. Terrain: Plains. Enemy forces: Mack (Austria): ~52,000 troops
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2274 of 2274 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   3/4
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
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, scout Swabia
   👁 Murat scouts Swabia: Controlled by Bavaria. Terrain: Plains. Enemy forces: Mack (Austria): ~52,000 troops
   [3/4 actions remaining]
map: unchanged (51 labels)
```

```
#0037  type what can I do  ->  ok
  (typed and Enter)
view: <run>\frames\0037_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok These orders would be carried out today, Sire:
  Ney, attack Mack
  Davout, march to Lorraine
  Soult, fortify
  recruit infantry in Rhineland — 741g for 3,000 men under Davout
  build supply depot in Rhineland — 300g
For any matter of state, press F1 for the Cabinet.
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1966 of 1967 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   3/4
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
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
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
   ► propose white peace with Austria  (sent from the diplomacy screen — typed, this line would propose a peace treaty with terms)
   Directing Talleyrand: seek bilateral peace
   Directing Talleyrand: confirm pair substitute
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► how can I make peace with Austria?
   Directing Talleyrand: expand to proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
   ► Talleyrand, assess our situation
   Directing Talleyrand: expand options
   Directing Talleyrand: execute proposal
   Directing Talleyrand: execute proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
   ► court Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to court and charm Prussia. (2 DP/turn)
   ► how strong is Mack's army in Swabia?
   Yes, Sire — Mack stands at Swabia — large force; his works and stance are not in view.
   ► Murat, scout Swabia
   👁 Murat scouts Swabia: Controlled by Bavaria. Terrain: Plains. Enemy forces: Mack (Austria): ~52,000 troops
   [3/4 actions remaining]
   ► what can I do
   These orders would be carried out today, Sire:
   Ney, attack Mack
   Davout, march to Lorraine
   Soult, fortify
   recruit infantry in Rhineland — 741g for 3,000 men under Davout
   build supply depot in Rhineland — 300g
   For any matter of state, press F1 for the Cabinet.
map: unchanged (51 labels)
```

```
#0038  click_at 1245 445  ->  ok
  (clicked at (1245, 445) on MapArea '100' (Control, layer 0))
view: <run>\frames\0038_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── RegionPanel (layer 26) ──
   Rhineland
   France  City · Plains / ACTIONS /   Recruit:  59,000 over the ordinance — every levy costs ×1.45 /       Infantry    Davout · 3,000 foot · 741g · field levy (pool 80,000) /       Cavalry    1,504g — the treasury holds 800g /       Artillery    No commander of guns serves us — commission Marmont (4500g) and he raises a corps of guns. /   Substitutes:   Buy Substitutes    4,012g — the treasury holds …
   controls: [icon @(351,73)]  <Infantry>  <▸ Build — 6 works>  <Fortify>  <Scout>  <Fortify>  <Scout>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1966 of 1967 px]: unchanged
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, last lines ──
   Soult, fortify
   recruit infantry in Rhineland — 741g for 3,000 men under Davout
   build supply depot in Rhineland — 300g
   For any matter of state, press F1 for the Cabinet.
map: unchanged (51 labels)
```

```
#0039  scroll 1240 440 up 3  ->  ok
  (scrolled up 3 at (1240, 440))
view: <run>\frames\0039_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── RegionPanel (layer 26): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1966 of 1967 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0) ──
   controls: [icon: Zoom out  (−) @(1181,992)]  [icon: Fit Europe — the whole theatre  (Home re-centres) @(1215,992)]  [icon: Zoom in  (+) @(1249,992)]
── command window, last lines ──
   Soult, fortify
   recruit infantry in Rhineland — 741g for 3,000 men under Davout
   build supply depot in Rhineland — 300g
   For any matter of state, press F1 for the Cabinet.
map: unchanged (51 labels)
```

```
#0040  type which of my marshals can reach Swabia this turn?  ->  ok
  (typed and Enter)
view: <run>\frames\0040_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
reply: ok Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
What you want is in the Generals screen (press G).

What I CAN do today:
  Ney, attack Mack
  Davout, march to Lorraine
  recruit infantry in Rhineland — 741g for 3,000 men under Davout
  build supply depot in Rhineland — 300g

For any matter of state, press F1 for the Cabinet.
Type 'help' for the full command reference.
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── RegionPanel (layer 26): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2275 of 2275 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   3/4
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
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► which of my marshals can reach Swabia this turn?
   Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
   What you want is in the Generals screen (press G).
   What I CAN do today:
   Ney, attack Mack
   Davout, march to Lorraine
   recruit infantry in Rhineland — 741g for 3,000 men under Davout
   build supply depot in Rhineland — 300g
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
map: unchanged (51 labels)
```

```
#0041  type Soult, march to Rhineland to join Ney and Davout  ->  ok
  (typed and Enter)
view: <run>\frames\0041_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: 'Davout' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
reply: ok Soult begins march to Rhineland. Moves to Rhineland. "Soult, march to Rhineland to join Ney and Davout." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)

Berthier: "One order at a time, Sire — I have relayed the first. "Davout" waits behind it. It is on the line — send it when you are ready."
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── RegionPanel (layer 26) [scrolled 0 of 10 px] ──
   Rhineland
   France  City · Plains / ACTIONS /   Recruit:  59,000 over the ordinance — every levy costs ×1.45 /       Infantry    Davout · 3,000 foot · 741g · field levy (pool 80,000) /       Cavalry    1,504g — the treasury holds 800g /       Artillery    No commander of guns serves us — commission Marmont (4500g) and he raises a corps of guns. /   Substitutes:   Buy Substitutes    4,012g — the treasury holds …
   controls: [icon @(351,73)]  <Infantry>  <▸ Build — 6 works>  <Fortify>  <Scout>  <Fortify>  <Scout>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2467 of 2467 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
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
   [Davout,]  (Tab)
   Davout
   controls: [+]  [−]  [—]  [Execute]  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, march to Rhineland to join Ney and Davout
   Soult begins march to Rhineland. Moves to Rhineland. "Soult, march to Rhineland to join Ney and Davout." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
   Berthier: "One order at a time, Sire — I have relayed the first. "Davout" waits behind it. It is on the line — send it when you are ready."
   [2/4 actions remaining]
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1507,597)  France(943,537)  Bavaria(1309,507)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  30(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Bernadotte(1334,451)  Deroy(1363,425)  ?(1367,302)  Brunswick(1368,263)  Mack(1251,466)  Ney(1198,387)  Davout(1212,360)  Soult(1227,332)  ?(1367,599)  Archduke John(1355,559)  Napoleon(1127,433)  Lannes(1183,504)  Murat(1193,478)  Massena(1310,612)  ?(1495,430)  ?(1367,363)  ?(1270,642)  ?(1290,362)  25k(942,504)  12k(890,454)  ?(1145,600)  12k(1055,412)  10k(1310,677)
```

```
#0042  key Ctrl+A  ->  ok
  (pressed Ctrl+A)
view: <run>\frames\0042_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: 'Davout' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)', 'region_panel (not modal)'], region_panel=yes
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── RegionPanel (layer 26) [scrolled 0 of 10 px]: unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2467 of 2467 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Soult, march to Rhineland to join Ney and Davout
   Soult begins march to Rhineland. Moves to Rhineland. "Soult, march to Rhineland to join Ney and Davout." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
   Berthier: "One order at a time, Sire — I have relayed the first. "Davout" waits behind it. It is on the line — send it when you are ready."
   [2/4 actions remaining]
map: unchanged (51 labels)
```

```
#0043  type Napoleon, march to Rhineland  ->  ok
  (typed and Enter)
view: <run>\frames\0043_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused) (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['clarification'], region_panel=no
reply: ok Which marshal shall march to Rhineland, Sire?
── ClarificationPopup (layer 102) ──
   BERTHIER ASKS:
   "Which marshal shall march to Rhineland, Sire?"
   controls: [Lannes]  [Murat]  [Bernadotte]  [Massena]  [Napoleon]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2541 of 2541 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   2/4
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
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► DavoutNapoleon, march to Rhineland
   Berthier requests clarification...
map: unchanged (51 labels)
```

```
#0044  click Napoleon  ->  ok
  (clicked at (1829, 637))
view: <run>\frames\0044_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Threat 70 / 100
   Turn 1 — Late September 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   0
   T:0
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [scrolled 2651 of 2651 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   1/4
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
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   > Napoleon, DavoutNapoleon, march to Rhineland
   Napoleon begins march to Rhineland. Moves to Rhineland. (1 AP — the Emperor commands in his own name.)
   [1/4 actions remaining]
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1507,597)  France(943,537)  Bavaria(1309,507)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  30(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Bernadotte(1334,451)  Deroy(1363,425)  ?(1367,302)  Brunswick(1368,263)  Mack(1251,466)  Ney +3(1212,375)  ?(1367,599)  Archduke John(1355,559)  Lannes(1183,504)  Murat(1193,478)  Massena(1310,612)  ?(1495,430)  ?(1367,363)  ?(1270,642)  ?(1290,362)  25k(942,504)  12k(890,454)  ?(1145,600)  12k(1083,412)  10k(1310,677)
```

```
#0045  click ⚖ Diplomacy  ->  ok
  (clicked at (509, 978))
view: <run>\frames\0045_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   At War (3)
   Treaties (2)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Spain  —  Alliance  |  +40 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2651 of 2651 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier requests clarification...
   > Napoleon, DavoutNapoleon, march to Rhineland
   Napoleon begins march to Rhineland. Moves to Rhineland. (1 AP — the Emperor commands in his own name.)
   [1/4 actions remaining]
map: unchanged (48 labels)
```

```
#0046  click Austria  —  At War  ->  ok
  (clicked at (1825, 601))
view: <run>\frames\0046_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 200 px, 0 of 182 px] ──
   DIPLOMACY — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War   Relation: -80 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus. /  / KEY FACTORS /   + Base willingness (+20) /   + Diplomat personality (+ …
   Mission already active
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Hopeless]  [Open Settlement]  [Propose White Peace]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5](disabled: Mission already active)  [Undermine Alliances (2 DP)  —  -4 relation between targets/turn](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2651 of 2651 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier requests clarification...
   > Napoleon, DavoutNapoleon, march to Rhineland
   Napoleon begins march to Rhineland. Moves to Rhineland. (1 AP — the Emperor commands in his own name.)
   [1/4 actions remaining]
map: unchanged (48 labels)
```

```
#0047  click Cancel  ->  ok
  (clicked at (1884, 740))
view: <run>\frames\0047_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2651 of 2651 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier requests clarification...
   > Napoleon, DavoutNapoleon, march to Rhineland
   Napoleon begins march to Rhineland. Moves to Rhineland. (1 AP — the Emperor commands in his own name.)
   [1/4 actions remaining]
map: unchanged (48 labels)
```

```
#0048  type Bernadotte, fortify in Franconia  ->  ok
  (typed and Enter)
view: <run>\frames\0048_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining.
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2762 of 2762 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   1/4
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
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Bernadotte, fortify in Franconia
   Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining.
map: unchanged (48 labels)
```

```
#0049  click End Turn (E)  ->  ok
  (clicked at (617, 978))
view: <run>\frames\0049_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 0 of 180 px] ──
   ENEMY PHASE - Turn 1
   AUSTRIA / ──────────────────────────── / - Mack attacks Swabia /     Region captured: Swabia (was Bavaria) (secured) / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 3,765 casualties, 50,235 remaining /     Massena: 6,688 casualties, 35,312 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) /     ⚔ View the field /     --- Be …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (3)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   TALLEYRAND — Divine Right / Authority: 95/100   Skill: 10   DP: 5/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary (+8 over 1 turns) /   Status: Active, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, now +2); 2 …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2697 of 2699 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,546
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
   Commands:
   • "Ney, attack Mack"
   • "scout Swabia" or "move to Flanders"
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   ─────────────────────────────────────
   ► propose white peace with Austria  (sent from the diplomacy screen — typed, this line would propose a peace treaty with terms)
   Directing Talleyrand: seek bilateral peace
   Directing Talleyrand: confirm pair substitute
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► how can I make peace with Austria?
   Directing Talleyrand: expand to proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
   ► Talleyrand, assess our situation
   Directing Talleyrand: expand options
   Directing Talleyrand: execute proposal
   Directing Talleyrand: execute proposal
   Directing Talleyrand: dismiss
   Very well, Sire.
   ► court Prussia
   Directing Talleyrand: start mission
   Talleyrand begins efforts to court and charm Prussia. (2 DP/turn)
   ► how strong is Mack's army in Swabia?
   Yes, Sire — Mack stands at Swabia — large force; his works and stance are not in view.
   ► Murat, scout Swabia
   👁 Murat scouts Swabia: Controlled by Bavaria. Terrain: Plains. Enemy forces: Mack (Austria): ~52,000 troops
   [3/4 actions remaining]
   ► what can I do
   These orders would be carried out today, Sire:
   Ney, attack Mack
   Davout, march to Lorraine
   Soult, fortify
   recruit infantry in Rhineland — 741g for 3,000 men under Davout
   build supply depot in Rhineland — 300g
   For any matter of state, press F1 for the Cabinet.
   ► which of my marshals can reach Swabia this turn?
   Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
   What you want is in the Generals screen (press G).
   What I CAN do today:
   Ney, attack Mack
   Davout, march to Lorraine
   recruit infantry in Rhineland — 741g for 3,000 men under Davout
   build supply depot in Rhineland — 300g
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
   ► Soult, march to Rhineland to join Ney and Davout
   Soult begins march to Rhineland. Moves to Rhineland. "Soult, march to Rhineland to join Ney and Davout." No more and no less. (1 AP — Soult executes precise orders with fewer couriers.)
   Berthier: "One order at a time, Sire — I have relayed the first. "Davout" waits behind it. It is on the line — send it when you are ready."
   [2/4 actions remaining]
   ► DavoutNapoleon, march to Rhineland
   Berthier requests clarification...
   > Napoleon, DavoutNapoleon, march to Rhineland
   Napoleon begins march to Rhineland. Moves to Rhineland. (1 AP — the Emperor commands in his own name.)
   [1/4 actions remaining]
   ► Bernadotte, fortify in Franconia
   Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining.
   ► end turn
   ═══════════════════════════════════════
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -334g | Other: +1295g | Upkeep: -2496g | Net: +746g
   Treasury: 1,546g
   Actions refreshed: 4/4
   Supply shortage at Rhineland: Ney loses 900 troops
   Supply shortage at Rhineland: Davout loses 975 troops
   Supply shortage at Rhineland: Soult loses 1,125 troops
   Supply shortage at Rhineland: Napoleon loses 375 troops
   Supply shortage at Tyrol: Archduke Charles loses 1,512 troops
   Supply shortage at Tyrol: Archduke John loses 602 troops
   Holland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 96 (-4): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1444,517)  France(943,537)  Bavaria(1337,509)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  30(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Bernadotte(1334,451)  Deroy(1363,425)  ?(1367,302)  Brunswick(1368,263)  Mack(1251,466)  Ney +3(1212,375)  ?(1368,599)  Archduke Charles(1345,559)  Archduke John(1364,478)  Lannes(1183,504)  Murat(1193,478)  Dumonceau(1129,301)  Massena(1295,612)  Teulie(1325,585)  ?(1495,430)  ?(1367,363)  ?(1300,642)  ?(1290,362)  25k(942,504)  12k(890,454)  ?(1145,600)  10k(1129,412)  12k(1080,412)  10k(1310,677)
```

```
#0050  scroll 1825 500 down 10  ->  ok
  (scrolled down 10 at (1825, 500))
view: <run>\frames\0050_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 155 of 179 px] ──
   ENEMY PHASE - Turn 1
   AUSTRIA / ──────────────────────────── / - Mack attacks Swabia /     Region captured: Swabia (was Bavaria) (secured) / - Archduke Charles attacks Massena /     The Great Battle of Milan /     Archduke Charles: 3,765 casualties, 50,235 remaining /     Massena: 6,688 casualties, 35,312 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) /     ⚔ View the field /     --- Be …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2697 of 2699 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
map: unchanged (52 labels)
```

```
#0051  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0051_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 35,312
   54,000 → 50,235
   THE GREAT BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 1
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2380 of 2380 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,546
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
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -219g | Materiel: -334g | Other: +1295g | Upkeep: -2496g | Net: +746g
   Treasury: 1,546g
   Actions refreshed: 4/4
   Supply shortage at Rhineland: Ney loses 900 troops
   Supply shortage at Rhineland: Davout loses 975 troops
   Supply shortage at Rhineland: Soult loses 1,125 troops
   Supply shortage at Rhineland: Napoleon loses 375 troops
   Supply shortage at Tyrol: Archduke Charles loses 1,512 troops
   Supply shortage at Tyrol: Archduke John loses 602 troops
   Holland loyalty 98 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 96 (-4): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Holland sends 6,500 men under Dumonceau to the colours at Amsterdam — they await the orders of France. The nearest host is Davout at Rhineland. Holland pays them; their dead will be its grief.
   The Kingdom of Italy sends 7,500 men under Teulie to the colours at Milan — they await the orders of France. They stand with Massena. The Kingdom of Italy pays them; their dead will be its grief.
   Sweden and Russia have signed an Open Borders Agreement.
   Naples and Russia have signed an Open Borders Agreement.
   --- Strategic Order Updates ---
   Napoleon: Napoleon is marching to Rhineland (0 turns remaining).
   Soult: Soult is marching to Rhineland (0 turns remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 2
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Swabia has been taken by Austria.
   • Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,546g (+1,080 by the accounts)
   The courts at war hold 29 regions. Estimated enemy strength: 70% of French forces (an estimate — 2 of 3 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Massena — Milan — 35,312 — Awaiting orders.
   - Soult — Rhineland — 28,875 — Arrived at Rhineland. (to the letter)
   - Davout — Rhineland — 25,025 — Awaiting orders.
   - Ney — Rhineland — 23,100 — Awaiting orders.
   - Murat — Franche-Comte — 22,000 — Awaiting orders.
   - Lannes — Franche-Comte — 18,000 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   - Napoleon — Rhineland — 9,625 — Arrived at Rhineland.
   - Teulie — Milan — 7,500 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Franconia — 22,000 [confirmed]
   Mack — Swabia — 52,000 [confirmed]
   Brunswick — Berlin — large force [partial]
   Archduke Charles — Tyrol — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   TURN EVENTS
   Supply cost you 3,375 men, at Rhineland.
   2 satellites drifted — Holland and Switzerland.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Orders in Council — a blockade it lays cuts the enemy's trade by 62%, not half (×1.25).
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
   - Prussia — Open Borders
   - Ottoman — Open Borders
   - Portugal — Open Borders
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-4)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0052  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Massena ◆' (PanelContainer, layer 121))
view: <run>\frames\0052_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS LOST
   FRANCE LOSSES
   AUSTRIA LOSSES
   6,688
   3,765
   ⚔
   Massena ◆
   Archduke Charles ◆
   42,000 → 35,312
   54,000 → 50,235
   Berthier: “The margin was slim. Training and preparation would serve Massena well.” / Archduke Charles: "Your marshals are bold. Boldness is not a plan."
   THE GREAT BATTLE OF MILAN
   MILAN · TURN 1
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2380 of 2380 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0053  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0053_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── BottomLeftUI (layer 0) [scrolled 2380 of 2380 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,546
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
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0054  click Envoys  ->  ok
  (clicked at (3387, 18))
view: <run>\frames\0054_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['mailbox_panel'], region_panel=no
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
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2380 of 2380 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0055  click ACTIVE  ->  ok
  (clicked at (1829, 278))
view: <run>\frames\0055_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Open Borders Agreement / Terms: /   - Proposal: Open Borders Agreement /   - Clause: Open borders /  / Hardenberg, stiffly: "Prussia's interest is the Rhine at peace and the army at home; Berlin signs where those two meet. Open the borders." /  / An unexpected overture. There may be hidden motives worth examining. /  / This offer will  …
   controls: [Accept]  [Counter]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2380 of 2380 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,546
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
   Threat: 68/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Ground lost can be retaken, Sire — but the longer they hold it, the harder the taking."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0056  click Accept  ->  ok
  (clicked at (1604, 687))
view: <run>\frames\0056_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
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
   DP: 5/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(2394,64)]  [icon: Diplomatic Action Accepted @(2436,64)]
── DiplomaticLedger (layer 50) [under a modal] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   TALLEYRAND — Divine Right / Authority: 95/100   Skill: 10   DP: 5/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary (+8 over 1 turns) /   Status: Active, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, now +2); 2 …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Russia
   -4
   T:1
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2446 of 2446 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,546
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
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia.
map: unchanged (52 labels)
```

```
#0057  click#1 Accept  ->  ok
  (clicked at (1433, 465))
view: <run>\frames\0057_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
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
   DP: 5/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(2394,64)]  [icon: Diplomatic Action Accepted @(2436,64)]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2490 of 2490 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,546
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
   You have accepted the Ottoman Empire's proposal. Treaty signed: Peace → Open Borders with the Ottoman Empire.
map: unchanged (52 labels)
```

```
#0058  click Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0058_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(2394,64)]  [icon: Diplomatic Action Accepted @(2436,64)]
── DiplomaticLedger (layer 50) ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   TALLEYRAND — Divine Right / Authority: 95/100   Skill: 10   DP: 5/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary (+8 over 1 turns) /   Status: Active, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, now +2); 2 …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2513 of 2513 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,546
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
   You have accepted Portugal's proposal. Treaty signed: Peace → Open Borders with Portugal.
map: unchanged (52 labels)
```

```
#0059  type how do I attack Mack with several marshals at once?  ->  ok
  (typed and Enter)
view: <run>\frames\0059_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok ═══════════════════════════════════════
           COMMAND REFERENCE
═══════════════════════════════════════

MILITARY COMMANDS:
  attack     - Engage enemy forces or capture region
               "Ney, attack Mack" / "attack" (nearest)

  defend     - Take defensive position (+30% bonus)
               "Davout, defend" / "hold" (alias)

  move       - Move to adjacent region
               "Lannes, move to Munich"

  retreat    - Fall back toward friendly territory (FREE)
               "Ney, retreat" - Aggressive marshals may object!

  recruit    - Raise troops (1 Admin AP + gold)
               "recruit for Davout" - his corps, where he stands
               "recruit at Paris" / "recruit" - at the depot, or the
               nearest corps: a marshal must stand within reach of it
               Infantry 10k / Cavalry 5k / Artillery 3k, from the
               manpower pools. PRICING: base 200-400g, capital -25%,
               x3 AT WAR, dearer above the FORCE LIMIT, and the
               marshal's administration prices the levy (Davout -15%,
               Murat +15% - his card explains, press G).
  substitutes - "buy substitutes for Ney" (1 Admin AP + gold)
               "purchase a levy for Ney" / "hire replacements for Ney"
               The remplacant: under the
               conscription law a called-up man could pay another
               to serve in his place. Draws NO men from the pools -
               gold alone - so it is the one purchase your TREASURY
   
── TopBar (layer 75) ──
   DP: 5/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(2352,64)]  [icon: Diplomatic Action Accepted @(2394,64)]  [icon: Treaty with Ottoman @(2436,64)]  [icon: Treaty with Portugal @(2478,64)]
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 8563 of 8563 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,606
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
   returns. Watch it in the Strategic Ledger's Orders tab
   (T) or on its notice; recall him from either, free.
   THE COMPACTS - three instruments that shipped and were never
   named here, so no player could learn they exist:
   buy off    - "buy off Prussia" - a court aims a grievance at us;
   gold buys its SLEEP for a term. The price is stated
   before you offer (D4 - diplomacy has no fog), and it
   is read off how badly they want the thing.
   sponsor    - "sponsor Prussia against Hanover, 200 gold" - arm
   somebody else's grievance, per turn, for a term.
   "license Prussia against Hanover" at no gold sells
   permission instead: the same bond, a cheaper coin.
   Talleyrand refuses to aim a design at ourselves.
   guarantee  - "guarantee Saxony" - pledge to defend a border.
   Coveters read the pledge and want it less; abandon
   it and the grievance is ours to answer for.
   NOTE: a standing compact runs its TERM. There is no cancelling
   it - war on the court, or a pledge that contradicts it,
   is a RENEGE, and Europe remembers who broke a word.
   Press D for the Diplomatic Ledger - all twenty nations of Europe,
   treaties, wars, and the Balance of Europe.
   THE CONGRESS OF PARIS (how the reign is WON - the table of the
   great powers is the Diplomatic Ledger's Congress tab, press D then 7):
   summon     - "summon the congress" (1 Admin AP + 2 DP), or the
   Congress of Paris row atop the Cabinet (F1). It needs
   50 TITLED provinces - homeland, ceded by treaty, a
   client's soil, or held 12 quiet turns - with Paris
   held, the Emperor free and no satellite on the brink.
   It cannot be undone. For 8 turns every great power
   answers - RECOGNIZES, REFUSES, SUES, SHUT OUT or GONE -
   with its reason and its PRICE. Keep the 50, Paris and
   the Emperor's freedom, and declare no war: on the
   eighth turn, with every great power won over, shut out
   or gone, the Imperial Peace is signed. Otherwise the
   Congress dissolves, and may be summoned again after
   10 turns.
   sweetener  - "offer Prussia 1000 gold for recognition" - offer
   <court> <gold> gold for recognition, at the table
   while the Congress sits (1 DP): +10 for every 1,000
   gold, at most +20 a court. Gold past that is not taken.
   Ask before you act - "can we summon the congress?" names every
   term still unmet, and nothing is spent.
   SCREENS & HOTKEYS:
   F1 diplomacy wizard | T strategic ledger | G marshals
   D diplomatic ledger | L campaign log | R morning dispatch
   E end turn | Tab terminal
   YOUR MARSHALS (press G - each card shows skills, trust, ability):
   Ney "Bravest of the Brave" - devastating assaults
   Davout "Iron Resolve" - fortified patience becomes a hammer-blow
   Soult "Drillmaster of Boulogne" - sharpens his corps in a day
   Lannes "Roland of the Army" - marches to the sound of the guns
   Murat "First Horseman of Europe" - turns routs into annihilation
   Bernadotte "Eyes on a Crown" - may not march for you at all
   Massena "Child of Victory" - hardest to kill when outnumbered
   Enemy generals carry famed abilities too - intel will name them.
   GLORY AND GRIEVANCE (the ladder on the Generals screen):
   Victories earn GLORY, counted over the last 8 turns. A marshal who
   falls behind a peer starts to ENVY him - and once he does, that man
   stays his rival for as long as he is above.
   ESTATES AND RENTES CANNOT TOUCH THIS. Gold answers a marshal's
   LOYALTY; only glory answers his envy. Rewarding a jealous marshal
   is not wrong - it is simply a different quarrel.
   A grievance costs you a corps: he will not coordinate with the man
   he resents, and at the worst he will not march beside him at all.
   Watch the muster preview - it names the quarrel when it bites.
   What ENDS it is the field. An aggressive marshal needs a win against
   a real foe; a cautious one a victory won shoulder to shoulder; a
   literal one only meaningful contact with the enemy. A hard defeat
   costs glory - unless he was outnumbered, which carries no shame -
   and out-bleeding the enemy 2-to-1 earns glory even when the field is
   left undecided.
   While he is aggrieved he attacks at +15% with no marshal of yours
   counted on the field beside him. Send him alone and he fights like
   a man with something to prove.
   FREE ACTIONS: help, end turn, wait, retreat, economy
   RETREAT RECOVERY (2-4 turns - command skill drives The Rally):
   After retreating, marshals are demoralized.
   BLOCKED: attack, fortify, drill, scout
   ALLOWED: move, recruit, defend, wait, change stance
   ═══════════════════════════════════════
map: unchanged (52 labels)
```

```
#0060  type Davout, Ney and Soult, attack Mack in Swabia together  ->  ok
  (typed and Enter)
view: <run>\frames\0060_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['objection'], region_panel=no
reply: ok Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.)

Berthier: "You named Ney and Soult beside Davout, Sire — Davout takes the order; Ney's own waits behind it. It waits behind the question Davout has put to you. Answer, and it returns to the line; another order, or the turn's end, lets it go. Soult needs his own order."
── ObjectionDialog (layer 108) ──
   DAVOUT'S ADVICE
   "Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.)"
   Personality: Cautious
   Trust: 85 (Loyal)
   Track record: Neutral
   Authority: 95
   controls: [Trust Davout: fortify current position (+2 trust)]  [Proceed as Ordered (-5 trust)]  [Compromise: adopt DEFENSIVE stance (+3 trust)]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 8673 of 8673 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,606
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
   ► Davout, Ney and Soult, attack Mack in Swabia together
   ⚠ Marshal Davout raises concerns...
map: unchanged (52 labels)
```

```
#0061  click Compromise: adopt DEFENSIVE stance  ->  ok
  (clicked at (2097, 582))
view: <run>\frames\0061_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: 'Ney, support Davout' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 68 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(2352,64)]  [icon: Diplomatic Action Accepted @(2394,64)]  [icon: Treaty with Ottoman @(2436,64)]  [icon: Treaty with Portugal @(2478,64)]
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   -4
   T:1
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [scrolled 8932 of 8932 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   1,606
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   [Ney, support Davout]  (Tab)
   Ney, support Davout
   controls: [+]  [−]  [—]  [Execute]  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► You seek a middle ground with your marshal.
   You find middle ground with Davout.
   Davout executes the compromise plan.
   Davout shifts from NEUTRAL to DEFENSIVE stance. Effect: -10% attack, +15% defense.
   Berthier: "One order at a time, Sire — "Ney, support Davout" was waiting behind the question. It is on the line — send it when you are ready."
   [3/4 actions remaining]
map: unchanged (52 labels)
```

```
#0062  key Ctrl+A  ->  ok
  (pressed Ctrl+A)
view: <run>\frames\0062_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: 'Ney, support Davout' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 8932 of 8932 px]: unchanged
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Davout executes the compromise plan.
   Davout shifts from NEUTRAL to DEFENSIVE stance. Effect: -10% attack, +15% defense.
   Berthier: "One order at a time, Sire — "Ney, support Davout" was waiting behind the question. It is on the line — send it when you are ready."
   [3/4 actions remaining]
map: unchanged (52 labels)
```

```
#0063  key Backspace  ->  ok
  (pressed Backspace)
view: <run>\frames\0063_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 8940 of 8940 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   1,606
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Davout executes the compromise plan.
   Davout shifts from NEUTRAL to DEFENSIVE stance. Effect: -10% attack, +15% defense.
   Berthier: "One order at a time, Sire — "Ney, support Davout" was waiting behind the question. It is on the line — send it when you are ready."
   [3/4 actions remaining]
map: unchanged (52 labels)
```

```
#0064  type Ney, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0064_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Ney (23,100; expect about 102,626 with the corps likely to arrive, up to 109,021 if all march) vs Mack (52,000 men) at Swabia — the balance of force looks favorable.
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10)
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
  Swabia feeds 40,000 — the whole muster standing there would lose ~5,864 men a turn to short supply.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
  (Stan
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   18,000 → 16,612
   Murat
   22,000 → 21,322
   Davout
   25,025 → 23,481
   ⚔
   Ney ◆
   Mack ◆
   marched to the guns
   23,100 → 20,723 → 20,486 after the advance
   52,000 → 37,385
   marched to the guns
   marched to the guns
   +2 corps in reserve
   Soult — awaits explicit orders
   THE GREAT BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(2352,64)]  [icon: Diplomatic Action Accepted @(2394,64)]  [icon: Treaty with Ottoman @(2436,64)]  [icon: Treaty with Portugal @(2478,64)]
── DiplomaticLedger (layer 50) [under a modal] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   TALLEYRAND — Divine Right / Authority: 100/100   Skill: 10   DP: 5/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary (+8 over 1 turns) /   Status: Active, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, now +2);  …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Russia
   +12
   T:1
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 9530 of 9530 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,307
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
   literal one only meaningful contact with the enemy. A hard defeat
   costs glory - unless he was outnumbered, which carries no shame -
   and out-bleeding the enemy 2-to-1 earns glory even when the field is
   left undecided.
   While he is aggrieved he attacks at +15% with no marshal of yours
   counted on the field beside him. Send him alone and he fights like
   a man with something to prove.
   FREE ACTIONS: help, end turn, wait, retreat, economy
   RETREAT RECOVERY (2-4 turns - command skill drives The Rally):
   After retreating, marshals are demoralized.
   BLOCKED: attack, fortify, drill, scout
   ALLOWED: move, recruit, defend, wait, change stance
   ═══════════════════════════════════════
   ► Davout, Ney and Soult, attack Mack in Swabia together
   ⚠ Marshal Davout raises concerns...
   ► You seek a middle ground with your marshal.
   You find middle ground with Davout.
   Davout executes the compromise plan.
   Davout shifts from NEUTRAL to DEFENSIVE stance. Effect: -10% attack, +15% defense.
   Berthier: "One order at a time, Sire — "Ney, support Davout" was waiting behind the question. It is on the line — send it when you are ready."
   [3/4 actions remaining]
   ► Ney, attack Mack
   ⚔ The Great Battle of Swabia ⚔
   MUSTER — Ney (23,100; expect about 102,626 with the corps likely to arrive, up to 109,021 if all march) vs Mack (52,000 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10)
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   Swabia feeds 40,000 — the whole muster standing there would lose ~5,864 men a turn to short supply.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+6%)
   Ney's attack meets fierce resistance. Ney gains the advantage over Mack. Casualties: Ney's army 5,987, Mack 14,615. Both armies remain in the field. Ney advances into Swabia. (237 lost to march)
   [Materiel] Guns, horses and stores lost with the fallen: France -299g, Austria -730g.
   ⚔ View the field
   [2/4 actions remaining]
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
   Napoleon was nearly in position, but fate intervened at the crucial moment.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 23,100 (lead) + 67,687 committed (Davout, Lannes, Murat) = 90,787.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,610 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   The corps system brought Murat in.
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%)
   Casualties: Ney's own corps 2,377 | Mack 14,615
   Strength: Ney 23,100 → 20,723 → 20,486 after the advance | Mack 52,000 → 37,385
   Berthier: "Reinforcements from Davout, Lannes and Murat bolstered Ney's position — though Soult, Bernadotte and Napoleon never arrived, Sire."
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1444,517)  France(943,537)  Bavaria(1337,509)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  30(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Bernadotte(1334,451)  Deroy(1363,425)  ?(1367,302)  Brunswick(1368,263)  Mack(1265,362)  Ney +3(1246,442)  Soult(1203,387)  Napoleon(1227,335)  ?(1368,599)  Archduke Charles(1345,559)  Archduke John(1364,478)  Dumonceau(1129,301)  Massena(1295,612)  Teulie(1325,585)  ?(1495,430)  ?(1367,363)  ?(1300,642)  ?(1315,360)  25k(942,504)  12k(890,454)  ?(1145,600)  10k(1129,412)  12k(1080,412)  10k(1310,677)
```

```
#0065  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Ney ◆' (PanelContainer, layer 121))
view: <run>\frames\0065_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A FIELD OF LEGEND IS WON
   FRANCE LOSSES
   AUSTRIA LOSSES
   5,987
   14,615
   Lannes
   18,000 → 16,612
   Murat
   22,000 → 21,322
   Davout
   25,025 → 23,481
   ⚔
   Ney ◆
   Mack ◆
   marched to the guns
   23,100 → 20,723 → 20,486 after the advance
   52,000 → 37,385
   marched to the guns
   marched to the guns
   +2 corps in reserve
   Soult — awaits explicit orders
   Berthier: “Reinforcements from Davout, Lannes and Murat bolstered Ney's position — though Soult, Bernadotte and Napoleon never arrived, Sire.” / Mack: "A temporary derangement of the arithmetic. Vienna will understand."
   THE GREAT BATTLE OF SWABIA
   SWABIA · TURN 2
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 9530 of 9530 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (52 labels)
```

```
#0066  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0066_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 9530 of 9530 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (52 labels)
```

```
#0067  click ⚖ Diplomacy  ->  ok
  (clicked at (509, 978))
view: <run>\frames\0067_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   At War (3)
   Treaties (5)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -2 (Wary)  [MISSION]]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 9530 of 9530 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (52 labels)
```

```
#0068  click Austria  —  At War  ->  ok
  (clicked at (1825, 601))
view: <run>\frames\0068_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 222 px, 0 of 182 px] ──
   DIPLOMACY — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War   Relation: -80 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus. /  / KEY FACTORS /   + Base willingness (+40) /   + Diplomat personality (+ …
   Mission already active
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Doubtful — may counter]  [Open Settlement]  [Propose White Peace]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5](disabled: Mission already active)  [Undermine Alliances (2 DP)  —  -4 relation between targets/turn](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 9530 of 9530 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
map: unchanged (52 labels)
```

```
#0069  click Propose Armistice (1 DP)  ->  ok
  (clicked at (1825, 459))
view: <run>\frames\0069_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 530 px] ──
   PEACE PREVIEW - Austria /  / Proposed Terms /   * Armistice (cease hostilities temporarily) / Assessment: GENEROUS /  / Acceptance Estimate / Score: 34 - REJECT likely — no workable counter / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / War score: 12 ^ (Decisive Battle +10) / Settlement: White Peace / Objective: Defense - the homeland — 28 of 28 provinces he …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 9575 of 9575 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,307
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
   ► propose armistice with Austria
map: unchanged (52 labels)
```

```
#0070  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0070_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 508 px] ──
   PEACE PREVIEW - Austria /  / Proposed Terms / France concedes: /   • France pays 130 gold per turn to Austria /  / Assessment: GENEROUS /  / Acceptance Estimate / Score: 38 - COUNTER expected / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / War score: 12 ^ (Decisive Battle +10) / Settlement: White Peace / Objective: Defense - the homeland — 28 of 28 provinces  …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 9596 of 9596 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,307
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
   Directing Talleyrand: modify generous
map: unchanged (52 labels)
```

```
#0071  scroll 1820 500 down 10  ->  ok
  (scrolled down 10 at (1820, 500))
view: <run>\frames\0071_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 440 of 508 px] ──
   PEACE PREVIEW - Austria /  / Proposed Terms / France concedes: /   • France pays 130 gold per turn to Austria /  / Assessment: GENEROUS /  / Acceptance Estimate / Score: 38 - COUNTER expected / Key advantage: Base Disposition / Key obstacle: Relation Modifier /  / War Summary / War score: 12 ^ (Decisive Battle +10) / Settlement: White Peace / Objective: Defense - the homeland — 28 of 28 provinces  …
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 9596 of 9596 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
   ► propose armistice with Austria
   Directing Talleyrand: modify generous
map: unchanged (52 labels)
```

```
#0072  click Not Now  ->  ok
  (clicked at (2056, 727))
view: <run>\frames\0072_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 76 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(2352,64)]  [icon: Diplomatic Action Accepted @(2394,64)]  [icon: Treaty with Ottoman @(2436,64)]  [icon: Treaty with Portugal @(2478,64)]
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   +12
   T:1
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [scrolled 9663 of 9663 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,307
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
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (52 labels)
```

```
#0073  type where is Mack now?  ->  ok
  (typed and Enter)
view: <run>\frames\0073_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Mack of Austria is at Swabia — 37,385 men, confirmed.
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 9752 of 9752 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,307
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► where is Mack now?
   Mack of Austria is at Swabia — 37,385 men, confirmed.
map: unchanged (52 labels)
```

```
#0074  type Soult, support Ney  ->  ok
  (typed and Enter)
view: <run>\frames\0074_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult reaches the approach to Swabia, but Mack's forces hold it. Orders complete — awaiting instructions to attack or hold.
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 9245 of 9245 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   1,307
   Inf:
   82,325
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   After retreating, marshals are demoralized.
   BLOCKED: attack, fortify, drill, scout
   ALLOWED: move, recruit, defend, wait, change stance
   ═══════════════════════════════════════
   ► Davout, Ney and Soult, attack Mack in Swabia together
   ⚠ Marshal Davout raises concerns...
   ► You seek a middle ground with your marshal.
   You find middle ground with Davout.
   Davout executes the compromise plan.
   Davout shifts from NEUTRAL to DEFENSIVE stance. Effect: -10% attack, +15% defense.
   Berthier: "One order at a time, Sire — "Ney, support Davout" was waiting behind the question. It is on the line — send it when you are ready."
   [3/4 actions remaining]
   ► Ney, attack Mack
   ⚔ The Great Battle of Swabia ⚔
   MUSTER — Ney (23,100; expect about 102,626 with the corps likely to arrive, up to 109,021 if all march) vs Mack (52,000 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   WILL JOIN — Murat: will march to the sound of the guns — but he and Ney are at odds; expect about half his weight — likely to make it in time (about 76%); order 'Murat, support Ney' and it rises to about 100% (The corps system lowers the bar by 10)
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   Swabia feeds 40,000 — the whole muster standing there would lose ~5,864 men a turn to short supply.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   (Standing orders decide who marches: 'Soult, support Ney' authorizes even a literal marshal to move to his guns.)
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+6%)
   Ney's attack meets fierce resistance. Ney gains the advantage over Mack. Casualties: Ney's army 5,987, Mack 14,615. Both armies remain in the field. Ney advances into Swabia. (237 lost to march)
   [Materiel] Guns, horses and stores lost with the fallen: France -299g, Austria -730g.
   ⚔ View the field
   [2/4 actions remaining]
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
   Napoleon was nearly in position, but fate intervened at the crucial moment.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 23,100 (lead) + 67,687 committed (Davout, Lannes, Murat) = 90,787.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,610 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   The corps system brought Murat in.
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%)
   Casualties: Ney's own corps 2,377 | Mack 14,615
   Strength: Ney 23,100 → 20,723 → 20,486 after the advance | Mack 52,000 → 37,385
   Berthier: "Reinforcements from Davout, Lannes and Murat bolstered Ney's position — though Soult, Bernadotte and Napoleon never arrived, Sire."
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
   ► propose armistice with Austria
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► where is Mack now?
   Mack of Austria is at Swabia — 37,385 men, confirmed.
   ► Soult, support Ney
   Soult reaches the approach to Swabia, but Mack's forces hold it. Orders complete — awaiting instructions to attack or hold.
   [1/4 actions remaining]
map: unchanged (52 labels)
```

```
#0075  type Ney, attack Mack  ->  ok
  (typed and Enter)
view: <run>\frames\0075_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused) (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['capture_choice'], region_panel=no
reply: ok MUSTER — Ney (20,486; expect about 113,555 with the corps likely to arrive, up to 114,091 if all march) vs Mack (37,385 men) at Swabia — the balance of force looks favorable.
  WILL JOIN — Davout: stands on the field and will fight beside him
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
  WILL JOIN — Lannes: stands on the field and will fight beside him
  WILL JOIN — Murat: stands on the field and will fight beside him
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
  Swabia feeds 32,000 — the whole muster standing there would lose ~5,489 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
  Murat shares the field at Swabia — his men will absorb part of any losses.


Ney holds them at Swabia while allies attack from Rhineland! (+1 coordination)

[Combat] Ney leads the charge! (Aggressive: +15% attack)
[Alert] Ney's troops are exhausted from repea
── CaptureChoiceDialog (layer 105) ──
   REGION CAPTURED!
   Ney has taken Swabia
   How shall your forces treat the conquered territory?
   controls: [PLUNDER (+600 gold, buildings burned, stability 10)]  [SECURE (Preserve order, stability 25, buildings damaged)]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 86 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2802 of 2803 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   1,150
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
   Napoleon was nearly in position, but fate intervened at the crucial moment.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 23,100 (lead) + 67,687 committed (Davout, Lannes, Murat) = 90,787.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 3,610 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "They stood, Sire. Briefly."
   The corps system brought Murat in.
   Berthier: the corps marched apart and arrived together.
   Attack: Ney (Personality (aggressive) +15%)
   Casualties: Ney's own corps 2,377 | Mack 14,615
   Strength: Ney 23,100 → 20,723 → 20,486 after the advance | Mack 52,000 → 37,385
   Berthier: "Reinforcements from Davout, Lannes and Murat bolstered Ney's position — though Soult, Bernadotte and Napoleon never arrived, Sire."
   ┌─────────────────────────────────────────────────┐
   BERTHIER'S REPORT
   ───────────────────────────────────────────────
   "Sire, our marshals fight as one corps for the first time! The combined arms of infantry and cavalry proved decisive."
   Position different unit types together for combined arms bonuses. Coordination improves with strong relationships between marshals.
   When marshals coordinate, casualties are shared. All friendly marshals in a battle region take proportional damage — even those not directly targeted.
   └─────────────────────────────────────────────────┘
   ► propose armistice with Austria
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► where is Mack now?
   Mack of Austria is at Swabia — 37,385 men, confirmed.
   ► Soult, support Ney
   Soult reaches the approach to Swabia, but Mack's forces hold it. Orders complete — awaiting instructions to attack or hold.
   [1/4 actions remaining]
   ► Ney, attack Mack
   ⚔ Second Battle of Swabia ⚔
   MUSTER — Ney (20,486; expect about 113,555 with the corps likely to arrive, up to 114,091 if all march) vs Mack (37,385 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   Swabia feeds 32,000 — the whole muster standing there would lose ~5,489 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Murat shares the field at Swabia — his men will absorb part of any losses.
   Ney holds them at Swabia while allies attack from Rhineland! (+1 coordination)
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Alert] Ney's troops are exhausted from repeated attacks! (2nd attack: -10%)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney launches a devastating assault! Ney gains the advantage over Mack. Casualties: Ney's army 3,140, Mack 27,672. Both armies remain in the field. Swabia has been captured by France!
   [Materiel] Guns, horses and stores lost with the fallen: France -157g, Austria -1383g.
   [!] MARSHAL CAPTURED — Mack is taken by France at Swabia! 4,856 of his men escape home to the depots.
   Napoleon answered the guns and stands at Swabia; his march to Rhineland stands and resumes next turn.
   Your forces have taken Swabia. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   ⚑ Swabia captured! ⚑
   ⚔ View the field
   [0/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 20,486 (lead) + 93,605 committed (Napoleon, Davout, Lannes, Murat) = 114,091.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,158 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "The bravest of the brave was first through their line — ask the line."
   Attack: Ney (Personality (aggressive) +15%, Exhaustion -10%, Flanking +1%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 982 | Mack 27,672
   Strength: Ney 20,486 → 19,504 | Mack 37,385 → 9,713
   Berthier: "Napoleon arrived to reinforce Ney, but Soult and Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
   Your forces await orders: Plunder or Secure?
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1507,597)  France(963,534)  Bavaria(1337,509)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  30(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Bernadotte(1334,451)  Deroy(1363,425)  ?(1367,302)  Brunswick(1368,263)  Ney +4(1246,442)  Soult(1213,387)  ?(1368,599)  Archduke Charles(1345,559)  Archduke John(1364,478)  Dumonceau(1129,301)  Massena(1295,612)  Teulie(1325,585)  ?(1495,430)  ?(1367,363)  ?(1300,642)  ?(1290,360)  25k(942,500)  12k(890,454)  ?(1145,600)  10k(1129,412)  12k(1080,412)  10k(1310,677)
```

```
#0076  click SECURE  ->  ok
  (clicked at (1995, 598))
view: <run>\frames\0076_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   16,612 → 16,016
   Murat
   21,322 → 20,710
   Davout
   23,481 → 22,807
   ⚔
   Ney ◆
   Mack ◆
   20,486 → 19,504
   37,385 → 9,713
   +2 corps in reserve — 276 lost
   Soult — awaits explicit orders
   SECOND BATTLE OF SWABIA
   click anywhere to skip ▸
   SWABIA · TURN 2
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 86 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(2352,64)]  [icon: Diplomatic Action Accepted @(2394,64)]  [icon: Treaty with Ottoman @(2436,64)]  [icon: Treaty with Portugal @(2478,64)]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Russia
   +32
   T:1
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2891 of 2891 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   1,150
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
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
map: unchanged (50 labels)
```

```
#0077  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Ney ◆' (PanelContainer, layer 121))
view: <run>\frames\0077_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS OURS
   FRANCE LOSSES
   AUSTRIA LOSSES
   3,140
   27,672
   Swabia falls to France.
   Lannes
   16,612 → 16,016
   Murat
   21,322 → 20,710
   Davout
   23,481 → 22,807
   ⚔
   Ney ◆
   Mack ◆
   20,486 → 19,504
   37,385 → 9,713
   +2 corps in reserve — 276 lost
   ROUTED
   Soult — awaits explicit orders
   Berthier: “Napoleon arrived to reinforce Ney, but Soult and Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him.” / Mack: "I withdraw in perfect conformity with a plan I have just completed."
   SECOND BATTLE OF SWABIA
   SWABIA · TURN 2
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2891 of 2891 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Napoleon arrived to reinforce Ney, but Soult and Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
map: unchanged (50 labels)
```

```
#0078  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0078_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2891 of 2891 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   1,150
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
   Berthier: "Napoleon arrived to reinforce Ney, but Soult and Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
map: unchanged (50 labels)
```

```
#0079  click ⚖ Diplomacy  ->  ok
  (clicked at (509, 978))
view: <run>\frames\0079_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   At War (3)
   Treaties (5)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  -2 (Wary)  [MISSION]]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2891 of 2891 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Napoleon arrived to reinforce Ney, but Soult and Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
map: unchanged (50 labels)
```

```
#0080  click Austria  —  At War  ->  ok
  (clicked at (1825, 601))
view: <run>\frames\0080_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 222 px, 0 of 182 px] ──
   DIPLOMACY — Austria
   DP: 5
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War   Relation: -80 (Hostile) /  / "The war with Austria grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus. /  / KEY FACTORS /   + Base willingness (+40) /   + Diplomat personality (+ …
   Mission already active
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Doubtful — may counter]  [Open Settlement]  [Propose White Peace]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5](disabled: Mission already active)  [Undermine Alliances (2 DP)  —  -4 relation between targets/turn](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2891 of 2891 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Napoleon arrived to reinforce Ney, but Soult and Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
map: unchanged (50 labels)
```

```
#0081  click Propose White Peace  ->  ok
  (clicked at (1825, 547))
view: <run>\frames\0081_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 156 px] ──
   This settlement cannot be ratified now. / France vs Austria + Britain + Russia - Whole-war settlement / STAGED FOR REVIEW — the terms are frozen. Ratify, revise, or return to shaping. / ▸ Blocked: Settlement legitimacy / ▸ Holding out: Austria, Britain, Russia / Covered enemies: Austria, Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 6/50, Britain -2/ …
   The table /   * Austria - Holding out (6/50) White peace /       Blocker: Settlement legitimacy /       Metternich regrets that Austria must remain… unconvinced — it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. /   * Britain - Holding out (-2/50) White peace /       Blocker: Settlement legitimacy /       Castlereagh declines for  …
   Sire, a white peace for France vs Austria + Britain + Russia cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. Author terms or hold until the field shifts. Vienna, London and Vilna are unbeaten — a whole-war peace needs their consent (Austria 6/50, Britain -2/50, Russia -2/50). /  / Allies and Standin …
   controls: [Make peace with Austria only]  [Armistice with Austria only]  [Open War Detail]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 86 / 100
   Turn 2 — Early October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2958 of 2958 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   1,150
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
   ► propose white peace with Austria  (sent from the diplomacy screen — typed, this line would propose a peace treaty with terms)
map: unchanged (50 labels)
```

```
#0082  click Back Out  ->  ok
  (clicked at (1455, 937))
view: <run>\frames\0082_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Early October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 86 / 100
   Turn 2 — Early October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(2352,64)]  [icon: Diplomatic Action Accepted @(2394,64)]  [icon: Treaty with Ottoman @(2436,64)]  [icon: Treaty with Portugal @(2478,64)]
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   +32
   T:1
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [scrolled 3023 of 3023 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   1,150
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
   Directing Talleyrand: back out settlement
   Settlement review cancelled.
map: unchanged (50 labels)
```

```
#0083  click End Turn (E)  ->  ok
  (clicked at (617, 978))
view: <run>\frames\0083_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused) (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 155 of 664 px] ──
   ENEMY PHASE - Turn 2
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Second Battle of Milan /     Archduke Charles: 3,873 casualties, 44,850 remaining /     Massena's army: 5,674 casualties — Massena's own corps: 30,279 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%)  …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   TALLEYRAND — Divine Right / Authority: 95/100   Skill: 10   DP: 5/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary → Neutral (+16, 2 turns) /   Status: Active, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, now …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── BottomLeftUI (layer 0) [under a modal] [scrolled 3233 of 3233 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,375
   Inf:
   84,487
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► where is Mack now?
   Mack of Austria is at Swabia — 37,385 men, confirmed.
   ► Soult, support Ney
   Soult reaches the approach to Swabia, but Mack's forces hold it. Orders complete — awaiting instructions to attack or hold.
   [1/4 actions remaining]
   ► Ney, attack Mack
   ⚔ Second Battle of Swabia ⚔
   MUSTER — Ney (20,486; expect about 113,555 with the corps likely to arrive, up to 114,091 if all march) vs Mack (37,385 men) at Swabia — the balance of force looks favorable.
   WILL JOIN — Davout: stands on the field and will fight beside him
   WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Ney' and he will march
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him
   WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   Swabia feeds 32,000 — the whole muster standing there would lose ~5,489 men a turn to short supply. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Murat shares the field at Swabia — his men will absorb part of any losses.
   Ney holds them at Swabia while allies attack from Rhineland! (+1 coordination)
   [Combat] Ney leads the charge! (Aggressive: +15% attack)
   [Alert] Ney's troops are exhausted from repeated attacks! (2nd attack: -10%)
   [Combat] Ney's combined arms coordination! (+10% attack)
   [Combat] Adjacent allies bolster Ney's attack! (+4%)
   Ney launches a devastating assault! Ney gains the advantage over Mack. Casualties: Ney's army 3,140, Mack 27,672. Both armies remain in the field. Swabia has been captured by France!
   [Materiel] Guns, horses and stores lost with the fallen: France -157g, Austria -1383g.
   [!] MARSHAL CAPTURED — Mack is taken by France at Swabia! 4,856 of his men escape home to the depots.
   Napoleon answered the guns and stands at Swabia; his march to Rhineland stands and resumes next turn.
   Your forces have taken Swabia. Plunder it for 600 gold — buildings burned, the province left hostile — or secure it and keep the country quiet? ('plunder' or 'secure')
   ⚑ Swabia captured! ⚑
   ⚔ View the field
   [0/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Soult awaits explicit orders and did not march to the sound of the guns.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Bernadotte hesitated — the I Corps weighed its own ambitions and did not march.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Ney!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 20,486 (lead) + 93,605 committed (Napoleon, Davout, Lannes, Murat) = 114,091.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,158 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Ney: "The bravest of the brave was first through their line — ask the line."
   Attack: Ney (Personality (aggressive) +15%, Exhaustion -10%, Flanking +1%, The Emperor commands in person +10%)
   Casualties: Ney's own corps 982 | Mack 27,672
   Strength: Ney 20,486 → 19,504 | Mack 37,385 → 9,713
   Berthier: "Napoleon arrived to reinforce Ney, but Soult and Bernadotte failed to reach the field in time. And Mack was taken on that field — France holds him."
   Your forces await orders: Plunder or Secure?
   You order your troops to secure the region.
   Ney secures Swabia. Stability set to 25. Order is maintained.
   ► propose white peace with Austria  (sent from the diplomacy screen — typed, this line would propose a peace treaty with terms)
   Directing Talleyrand: back out settlement
   Settlement review cancelled.
   ► end turn
   ═══════════════════════════════════════
   TURN 3 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -281g | Materiel: -561g | Other: +1329g | Upkeep: -2762g | Net: +225g
   Treasury: 1,375g
   Actions refreshed: 4/4
   Bavaria completes a market at Franconia.
   Supply shortage at Franconia: Archduke Charles loses 612 troops
   Supply shortage at Swabia: Ney loses 1,026 troops — 108 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Davout loses 1,200 troops — 126 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Lannes loses 842 troops — 88 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Murat loses 1,089 troops — 114 of them to living off the land (this stripped country feeds a French army 80%)
   Supply shortage at Swabia: Napoleon loses 491 troops — 51 of them to living off the land (this stripped country feeds a French army 80%)
   Kingdom of Italy loyalty 98 (-2): the contingent's dead, satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 94 (-2): satellite drift, the lord's defeats
   Britain subsidizes Austria with 200 gold.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Davout appears envious of Ney's laurels — he has grown careful about what he commits to paper.
   Murat is eyeing Archduke Charles's position at Franconia. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1507,597)  France(943,537)  Bavaria(1309,507)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  30(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Bernadotte(1334,451)  Archduke Charles(1362,425)  ?(1367,302)  Brunswick(1368,263)  Ney +4(1246,442)  Soult(1213,387)  ?(1368,599)  Archduke John(1355,559)  Dumonceau(1129,301)  Massena(1295,612)  Teulie(1325,585)  ?(1495,430)  ?(1367,363)  ?(1263,583)  ?(1290,360)  25k(942,504)  12k(890,454)  ?(1145,600)  10k(1129,412)  12k(1080,412)  10k(1310,677)
```

```
#0084  scroll 1825 500 down 10  ->  ok
  (scrolled down 10 at (1825, 500))
view: <run>\frames\0084_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused) (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 595 of 664 px] ──
   ENEMY PHASE - Turn 2
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Massena /     The Great Second Battle of Milan /     Archduke Charles: 3,873 casualties, 44,850 remaining /     Massena's army: 5,674 casualties — Massena's own corps: 30,279 remaining /     Result: Bloody stalemate /     ⚔ View the field /     --- Berthier's Report --- /     Defense: Massena (Child of Victory (outnumbered) +10%)  …
   controls: <⚔ View the field>  <⚔ View the field>  <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3233 of 3233 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Davout appears envious of Ney's laurels — he has grown careful about what he commits to paper.
   Murat is eyeing Archduke Charles's position at Franconia. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
map: unchanged (49 labels)
```

```
#0085  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0085_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Teulie
   7,500 → 6,859
   ⚔
   Massena ◆
   Archduke Charles ◆
   35,312 → 30,279
   48,723 → 44,850
   THE GREAT SECOND BATTLE OF MILAN
   click anywhere to skip ▸
   MILAN · TURN 2
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,375
   Inf:
   84,487
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Napoleon: Napoleon answered the guns this turn and stands at Swabia; his march resumes next turn.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 3
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — General Mack of Austria is taken at Swabia — he is our prisoner, and their order of battle is one commander shorter.
   • Sire — Swabia has fallen to our arms. The tricolor flies over it this morning.
   • Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
   SITUATION
   France holds 28 regions. Treasury: 1,375g (+786 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 39% of French forces (an estimate — 1 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — Hunted by Archduke Charles on consecutive turns — holds Milan with 26,239 men.
   - Davout — Swabia — 21,607 — Awaiting orders.
   - Murat — Swabia — 19,621 — Awaiting orders.
   - Ney — Swabia — 18,478 — Awaiting orders.
   - Bernadotte — Franconia — 17,000 — Awaiting orders. Trust:40
   ⚠ IN PERIL — an enemy force of ~38,006 shares the field (Franconia).
   - Lannes — Swabia — 15,174 — Awaiting orders.
   > Napoleon — Swabia — 8,858 — Moving to Rhineland.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   - Teulie — Milan — 5,334 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Franconia — 38,006 [confirmed]
   Brunswick — Berlin — large force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Deroy — Munich — substantial force [partial]
   TURN EVENTS
   Supply cost you 4,648 men, at Swabia.
   2 satellites drifted — Kingdom of Italy and Switzerland.
   Berthier reports that Murat appears envious of Ney's laurels — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Davout appears envious of Ney's laurels — he has grown careful about what he commits to paper.
   Murat is eyeing Archduke Charles's position at Franconia. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   Berthier notes that Ney's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Open Borders Agreement.
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Portugal and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 22).
   War exhaustion grows — Austria nears breaking point (exhaustion: 42).
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 6.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   France hands Swabia back to Bavaria — the liberated soil comes home.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Denmark — Non Aggression
   - Saxony — Open Borders
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms (+27)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (49 labels)
```

```
#0086  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Massena ◆' (PanelContainer, layer 121))
view: <run>\frames\0086_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama'], region_panel=no
── BattleDiorama (layer 121) ──
   A BLOODY STALEMATE
   FRANCE LOSSES
   AUSTRIA LOSSES
   5,674
   3,873
   Teulie
   7,500 → 6,859
   ⚔
   Massena ◆
   Archduke Charles ◆
   35,312 → 30,279
   48,723 → 44,850
   Berthier: “An inconclusive affair. Both sides bloodied but unbroken.” / Archduke Charles: "Your Emperor needs quick victories. I need only deny them."
   THE GREAT SECOND BATTLE OF MILAN
   MILAN · TURN 2
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (49 labels)
```

```
#0087  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0087_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── BottomLeftUI (layer 0) [scrolled 1872 of 1872 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,375
   Inf:
   84,487
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (49 labels)
```

```
#0088  click Envoys  ->  ok
  (clicked at (3391, 18))
view: <run>\frames\0088_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['mailbox_panel'], region_panel=no
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
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1872 of 1872 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
map: unchanged (49 labels)
```

```
#0089  click#1 Accept  ->  ok
  (clicked at (1433, 421))
view: <run>\frames\0089_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['mailbox_panel'], region_panel=no
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
   DP: 5/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
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
   1,375
   Inf:
   84,487
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
map: unchanged (49 labels)
```

```
#0090  click Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0090_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   TALLEYRAND — Divine Right / Authority: 95/100   Skill: 10   DP: 5/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary → Neutral (+16, 2 turns) /   Status: Active, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, now …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
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
   1,375
   Inf:
   84,487
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
map: unchanged (49 labels)
```

```
#0091  type Murat, attack Archduke Charles in Franconia  ->  ok
  (typed and Enter)
view: <run>\frames\0091_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Murat (19,621; expect about 61,549 with the corps likely to arrive, up to 62,881 if all march) vs Archduke Charles (38,006 men) at Franconia — the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns — but Murat resents him, and will make no use of him: NOTHING of his weight reaches the fighting — likely to make it in time (about 99%) (The corps system lowers the bar by 10)
  WILL JOIN — Davout: is willing to march if the roads allow — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
  WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
  The band weighs more than the men: Archduke Charles stands +3% on the defense (his stance, his character and his works).
  Franconia feeds 60,000 — the whole muster standing there would lose ~6,042 men a turn to short supply.
  Every corps in the province shares the field — that is the design, and the quarrel above is its one exception: no order holds a corps out o
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   15,174 → 13,961
   Ney
   18,478 → 18,478
   Davout
   21,607 → 20,744
   ⚔
   Murat ◆
   Archduke Charles ◆
   marched to the guns
   19,621 → 17,004
   38,006 → 30,515
   marched to the guns
   marched to the guns
   +1 corps in reserve — 885 lost
   THE GREAT SECOND BATTLE OF FRANCONIA
   click anywhere to skip ▸
   FRANCONIA · TURN 3
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Murat seeks an audience @(2032,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Denmark @(2350,64)]  [icon: Treaty with Saxony @(2392,64)]  [icon: Treaty with Prussia @(2434,64)]  [icon: Diplomatic Action Accepted @(2476,64)]  [+2]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Russia
   +26
   T:2
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2894 of 2894 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   1,179
   Inf:
   84,487
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Sire — the Ottoman Empire and France have signed the Open Borders Agreement.
   Sire — Portugal and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 22).
   War exhaustion grows — Austria nears breaking point (exhaustion: 42).
   THE LAWS: Russia enacts the Opolchenie — infantry manpower returns 25% faster.
   An envoy from Denmark has arrived with a proposal.
   An envoy from Saxony has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 6.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   France hands Swabia back to Bavaria — the liberated soil comes home.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Denmark — Non Aggression
   - Saxony — Open Borders
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms (+27)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
   ► Murat, attack Archduke Charles in Franconia
   ⚔ The Great Second Battle of Franconia ⚔
   MUSTER — Murat (19,621; expect about 61,549 with the corps likely to arrive, up to 62,881 if all march) vs Archduke Charles (38,006 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — but Murat resents him, and will make no use of him: NOTHING of his weight reaches the fighting — likely to make it in time (about 99%) (The corps system lowers the bar by 10)
   WILL JOIN — Davout: is willing to march if the roads allow — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
   WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   The band weighs more than the men: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~6,042 men a turn to short supply.
   Every corps in the province shares the field — that is the design, and the quarrel above is its one exception: no order holds a corps out of its own province, but a feud does. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Combat] Murat's combined arms coordination! (+10% attack)
   Murat attacks with overwhelming force. Brutal stalemate between Murat and Archduke Charles. Heavy casualties on both sides: Murat's army 5,578, Archduke Charles 7,491.
   [Materiel] Guns, horses and stores lost with the fallen: France -278g, Austria -374g.
   Ney withdraws to Swabia after the battle.
   Davout withdraws to Swabia after the battle.
   Lannes withdraws to Swabia after the battle.
   Napoleon withdraws to Swabia after the battle.
   Napoleon answered the guns and stands at Swabia; his march to Rhineland stands and resumes next turn.
   (Murat stands down from his intended attack — your orders reached him in time.)
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
   Napoleon's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 19,621 (lead) + 43,260 committed (Ney, Davout, Lannes, Napoleon) = 62,881.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,961 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Murat: "Neither side yielded. Unfinished business sits badly with me."
   Murat fought with particular ferocity — though one wonders if it was for France or for himself.
   Attack: Murat (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Murat's own corps 2,617 | Archduke Charles 7,491
   Strength: Murat 19,621 → 17,004 | Archduke Charles 38,006 → 30,515
   Berthier: "Ney, Davout, Lannes and Napoleon arrived in time to steady Murat's position. The field was held, nothing further."
   The war's cost now stands at 32,632 of our men.
map: unchanged (49 labels)
```

```
#0092  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Murat ◆' (PanelContainer, layer 121))
view: <run>\frames\0092_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A BLOODY STALEMATE
   FRANCE LOSSES
   AUSTRIA LOSSES
   5,578
   7,491
   Lannes
   15,174 → 13,961
   Ney
   18,478 → 18,478
   Davout
   21,607 → 20,744
   ⚔
   Murat ◆
   Archduke Charles ◆
   marched to the guns
   19,621 → 17,004
   38,006 → 30,515
   marched to the guns
   marched to the guns
   +1 corps in reserve — 885 lost
   Berthier: “Ney, Davout, Lannes and Napoleon arrived in time to steady Murat's position. The field was held, nothing further.” / Archduke Charles: "A day of arithmetic. The sums still favor me."
   THE GREAT SECOND BATTLE OF FRANCONIA
   FRANCONIA · TURN 3
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2894 of 2894 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Casualties: Murat's own corps 2,617 | Archduke Charles 7,491
   Strength: Murat 19,621 → 17,004 | Archduke Charles 38,006 → 30,515
   Berthier: "Ney, Davout, Lannes and Napoleon arrived in time to steady Murat's position. The field was held, nothing further."
   The war's cost now stands at 32,632 of our men.
map: unchanged (49 labels)
```

```
#0093  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0093_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2894 of 2894 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Casualties: Murat's own corps 2,617 | Archduke Charles 7,491
   Strength: Murat 19,621 → 17,004 | Archduke Charles 38,006 → 30,515
   Berthier: "Ney, Davout, Lannes and Napoleon arrived in time to steady Murat's position. The field was held, nothing further."
   The war's cost now stands at 32,632 of our men.
map: unchanged (49 labels)
```

```
#0094  type Bernadotte, support Lannes  ->  ok
  (typed and Enter)
view: <run>\frames\0094_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: Bernadotte is engaged with Archduke Charles and cannot begin a strategic march. Deal with the engagement first.
Try: 'Bernadotte, attack Archduke Charles' or 'Bernadotte, retreat'
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3028 of 3028 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   1,179
   Inf:
   84,487
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Bernadotte, support Lannes
   Bernadotte is engaged with Archduke Charles and cannot begin a strategic march. Deal with the engagement first.
   Try: 'Bernadotte, attack Archduke Charles' or 'Bernadotte, retreat'
map: unchanged (49 labels)
```

```
#0095  type Bernadotte, attack Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0095_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused) (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['interrupt'], region_panel=no
reply: ok Bernadotte notes the risks but prepares the attack. Bernadotte halts before the order is carried out. "I will go if you order it, Sire — but look at the ground first. This is not a battle, it is an arithmetic problem."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Bernadotte (17,000) vs Archduke Charles (30,515 men) at Franconia — the balance of force looks unfavorable.
  WILL NOT — Ney: has already marched this turn
  WILL NOT — Davout: has already marched this turn
  WILL NOT — Lannes: has already marched this turn
  WILL NOT — Murat: will not lift a finger for Marshal Bernadotte
  WILL NOT — Napoleon: has already marched this turn
  The band weighs more than the men: all told, Bernadotte's own modifiers weigh 10% against the attack; Archduke Charles stands +3% on the defense (his stance, his character and his works).
  Franconia feeds 60,000 — the whole muster can stand there fed.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
── InterruptPopup (layer 103) ──
   BERNADOTTE REPORTS
   "Bernadotte halts before the order is carried out. "I will go if you order it, Sire — but look at the ground first. This is not a battle, it is an arithmetic problem." /  / The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back. / MUSTER — Bernadotte (17,000) vs Archduke Charles (30,515 men) at Franconia — the balance of force looks unfavorable. /  …
   controls: [Commit the Attack]  [Cancel Order]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3095 of 3095 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   1,179
   Inf:
   84,487
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Bernadotte, attack Archduke Charles
   Bernadotte awaits your orders!
map: unchanged (49 labels)
```

```
#0096  click Cancel Order  ->  ok
  (clicked at (1971, 761))
view: <run>\frames\0096_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Murat seeks an audience @(2032,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Denmark @(2350,64)]  [icon: Treaty with Saxony @(2392,64)]  [icon: Treaty with Prussia @(2434,64)]  [icon: Diplomatic Action Accepted @(2476,64)]  [+2]
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   +26
   T:2
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [scrolled 3139 of 3139 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   1,179
   Inf:
   84,487
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   > Bernadotte: cancel order
   Bernadotte stands down, Sire — the attack on ArchdukeCharles is called off.
map: unchanged (49 labels)
```

```
#0097  click Marshal Murat seeks an audience  ->  ok
  (clicked at (2032, 64))
view: <run>\frames\0097_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   Imperial Box
   Marshal Murat seeks an audience
   T2
   Murat asks to be heard — at your leisure, Sire; nothing waits on it. His card is on the Generals screen.
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Murat seeks an audience @(2032,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Denmark @(2350,64)]  [icon: Treaty with Saxony @(2392,64)]  [icon: Treaty with Prussia @(2434,64)]  [icon: Diplomatic Action Accepted @(2476,64)]  [+2]  [Hear him]  [Keep]  [Acknowledge]
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3139 of 3139 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► Bernadotte, attack Archduke Charles
   Bernadotte awaits your orders!
   > Bernadotte: cancel order
   Bernadotte stands down, Sire — the attack on ArchdukeCharles is called off.
map: unchanged (49 labels)
```

```
#0098  click Hear him  ->  ok
  (clicked at (2440, 221))
view: <run>\frames\0098_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['marshal_petition', 'war_status_panel (not modal)'], region_panel=no
── MarshalPetitionDialog (layer 114) [scrolled 0 of 159 px] ──
   MURAT — Marshal Murat seeks an audience
   "Sire — I have earned better than to watch Ney take the field while I hold a road." /  / Sire, Murat has expressed... displeasure about Ney's recent recognition. He requests a command worthy of his talents.
   Free, and it fixes nothing. For 5 more turns he brings NONE of his 20,710 men to any battle Ney leads, and the quarrel may harden further.
   His patience is bought — the grievance shortens by 2 turns, and for 6 turns the quarrel cannot harden further.
   controls: [Let it stand   [Free]]  [Promise Glory   [1 AP]]  [Rebuke]  [Later (he will return)]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Marshal Murat seeks an audience @(2032,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Denmark @(2350,64)]  [icon: Treaty with Saxony @(2392,64)]  [icon: Treaty with Prussia @(2434,64)]  [icon: Diplomatic Action Accepted @(2476,64)]  [+2]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3139 of 3139 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   1,179
   Inf:
   84,487
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► Bernadotte, attack Archduke Charles
   Bernadotte awaits your orders!
   > Bernadotte: cancel order
   Bernadotte stands down, Sire — the attack on ArchdukeCharles is called off.
map: unchanged (49 labels)
```

```
#0099  click Promise Glory  ->  ok
  (clicked at (1825, 592))
view: <run>\frames\0099_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Late October 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 84 / 100
   Turn 3 — Late October 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Denmark @(2308,64)]  [icon: Treaty with Saxony @(2350,64)]  [icon: Treaty with Prussia @(2392,64)]  [icon: Diplomatic Action Accepted @(2434,64)]  [icon: Treaty with Ottoman @(2476,64)]  [+1]
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2589 of 2590 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   1,179
   Inf:
   84,487
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0) ──
   controls: {100}
── MapControls (layer 0): unchanged
── command window, new lines ──
   Talleyrand's efforts in Prussia continue. Relations now at 6.
   Britain's gold reaches Austria — the subsidy stands at 200 this season.
   France hands Swabia back to Bavaria — the liberated soil comes home.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Denmark — Non Aggression
   - Saxony — Open Borders
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms (+27)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 84/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A commander is not replaced like a battalion, Sire. Press them before they find another."
   ════════════════════════════════════
   You have accepted Denmark's proposal. Treaty signed: Peace → Non-Aggression with Denmark.
   You have accepted Saxony's proposal. Treaty signed: Peace → Open Borders with Saxony.
   ► Murat, attack Archduke Charles in Franconia
   ⚔ The Great Second Battle of Franconia ⚔
   MUSTER — Murat (19,621; expect about 61,549 with the corps likely to arrive, up to 62,881 if all march) vs Archduke Charles (38,006 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — but Murat resents him, and will make no use of him: NOTHING of his weight reaches the fighting — likely to make it in time (about 99%) (The corps system lowers the bar by 10)
   WILL JOIN — Davout: is willing to march if the roads allow — but he and Murat are at odds; expect about half his weight — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
   WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
   WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   The band weighs more than the men: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~6,042 men a turn to short supply.
   Every corps in the province shares the field — that is the design, and the quarrel above is its one exception: no order holds a corps out of its own province, but a feud does. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Combat] Murat's combined arms coordination! (+10% attack)
   Murat attacks with overwhelming force. Brutal stalemate between Murat and Archduke Charles. Heavy casualties on both sides: Murat's army 5,578, Archduke Charles 7,491.
   [Materiel] Guns, horses and stores lost with the fallen: France -278g, Austria -374g.
   Ney withdraws to Swabia after the battle.
   Davout withdraws to Swabia after the battle.
   Lannes withdraws to Swabia after the battle.
   Napoleon withdraws to Swabia after the battle.
   Napoleon answered the guns and stands at Swabia; his march to Rhineland stands and resumes next turn.
   (Murat stands down from his intended attack — your orders reached him in time.)
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
   Napoleon's forces arrived to reinforce Murat!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 19,621 (lead) + 43,260 committed (Ney, Davout, Lannes, Napoleon) = 62,881.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,961 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Murat: "Neither side yielded. Unfinished business sits badly with me."
   Murat fought with particular ferocity — though one wonders if it was for France or for himself.
   Attack: Murat (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Murat's own corps 2,617 | Archduke Charles 7,491
   Strength: Murat 19,621 → 17,004 | Archduke Charles 38,006 → 30,515
   Berthier: "Ney, Davout, Lannes and Napoleon arrived in time to steady Murat's position. The field was held, nothing further."
   The war's cost now stands at 32,632 of our men.
   ► Bernadotte, support Lannes
   Bernadotte is engaged with Archduke Charles and cannot begin a strategic march. Deal with the engagement first.
   Try: 'Bernadotte, attack Archduke Charles' or 'Bernadotte, retreat'
   ► Bernadotte, attack Archduke Charles
   Bernadotte awaits your orders!
   > Bernadotte: cancel order
   Bernadotte stands down, Sire — the attack on ArchdukeCharles is called off.
   Murat bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (49 labels)
```

```
#0100  click End Turn (E)  ->  ok
  (clicked at (617, 978))
view: <run>\frames\0100_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused) (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) [scrolled 155 of 179 px] ──
   ENEMY PHASE - Turn 3
   AUSTRIA / ──────────────────────────── / - Archduke Charles attacks Bernadotte /     Third Battle of Franconia /     Archduke Charles: 1,610 casualties, 28,905 remaining /     Bernadotte: 4,418 casualties, 12,582 remaining /     Result: Attacker tactical victory (Archduke Charles victorious) /     ⚔ View the field /     --- Berthier's Report --- /     Attack: Archduke Charles (Forced march momentu …
   controls: <⚔ View the field>  [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 82 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   TALLEYRAND — Divine Right / Authority: 95/100   Skill: 10   DP: 5/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary → Neutral (+24, 3 turns) /   Status: Active, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, now …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── BottomLeftUI (layer 0) [under a modal] [scrolled 3186 of 3186 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,364
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 4 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -329g | Materiel: -220g | Other: +1408g | Upkeep: -2174g | Net: +1185g
   Treasury: 2,364g
   Actions refreshed: 4/4
   Supply shortage at Franconia: Archduke Charles loses 305 troops
   Supply shortage at Swabia: Ney loses 1,088 troops
   Supply shortage at Swabia: Davout loses 1,222 troops
   Supply shortage at Swabia: Lannes loses 822 troops
   Supply shortage at Swabia: Murat loses 1,001 troops
   Supply shortage at Swabia: Napoleon loses 469 troops
   Supply shortage at Swabia: Deroy loses 1,031 troops
   Holland loyalty 96 (-2): satellite drift, the lord's defeats — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 90 (-4): satellite drift, the lord's defeats
   Territorial rivalry between Russia and Prussia grows.
   Territorial rivalry between Russia and Sweden grows.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Murat is eyeing Archduke Charles's position at Franconia. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1507,597)  France(943,537)  Bavaria(1309,507)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  31(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Bernadotte(1334,451)  Archduke Charles(1362,425)  ?(1367,302)  Brunswick(1368,263)  Deroy(1265,356)  Ney +4(1246,442)  Soult(1213,387)  ?(832,626)  Castanos(832,586)  ?(1368,599)  Archduke John(1355,559)  Dumonceau(1129,301)  Massena(1295,612)  Teulie(1325,585)  ?(1495,430)  ?(1367,363)  ?(1263,583)  ?(1318,360)  25k(942,504)  12k(890,454)  ?(1145,600)  10k(1129,412)  12k(1080,412)  10k(1310,677)
```

```
#0101  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0101_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── BottomLeftUI (layer 0) [scrolled 2071 of 2071 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,364
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ━━ Field Dispatches ━━
   Bernadotte notes the risks but prepares the attack.
   --- Strategic Order Updates ---
   Napoleon: Napoleon answered the guns this turn and stands at Swabia; his march resumes next turn.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 4
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 4,418 men — lost in a single action.
   • Sire — Ney, Davout, Lannes, Murat and Napoleon stand 73,558 men at Swabia, which feeds 60,000. 13,558 too many. 9,250 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for the province. Lorraine can feed 60,000 more and Franche-Comte can feed 52,500 more — a corps marched there ends it.
   • Sire — London now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 6 turns (6 DP); buying off her design costs 1,368 gold and shortens the road to 5 turns.
   SITUATION
   France holds 28 regions. Treasury: 2,364g (+1,405 by the accounts)
   The courts at war hold 28 regions. Estimated enemy strength: 37% of French forces (an estimate — 1 of 2 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 95 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — Hunted by Archduke Charles on consecutive turns — holds Milan with 26,239 men.
   - Davout — Swabia — 19,522 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Ney — Swabia — 17,390 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Murat — Swabia — 16,003 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Lannes — Swabia — 13,139 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Bernadotte — Franconia — 12,582 — Awaiting orders. Trust:40
   ⚠ IN PERIL — an enemy force of ~28,600 shares the field (Franconia).
   > Napoleon — Swabia — 7,504 — Moving to Rhineland.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   - Teulie — Milan — 5,334 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Franconia — 28,600 [confirmed]
   Deroy — Swabia — 16,469 [confirmed]
   Brunswick — Berlin — large force [partial]
   Castanos — Gascony — small force [partial]
   Archduke John — Tyrol — substantial force [partial]
   TURN EVENTS
   Supply cost you 4,602 men, at Swabia.
   2 satellites drifted — Holland and Switzerland.
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Murat is eyeing Archduke Charles's position at Franconia. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   DIPLOMATIC EVENTS
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 14.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Hesse — Non Aggression
   - Papal States — Open Borders
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms (+23)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 82/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0102  click Envoys (2)  ->  ok
  (clicked at (3375, 18))
view: <run>\frames\0102_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['mailbox_panel'], region_panel=no
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
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2071 of 2071 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 82/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
map: unchanged (52 labels)
```

```
#0103  click#1 Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0103_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['mailbox_panel'], region_panel=no
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
   DP: 5/7
   Threat 82 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2093 of 2093 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,364
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
map: unchanged (52 labels)
```

```
#0104  click Accept  ->  ok
  (clicked at (1433, 443))
view: <run>\frames\0104_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 82 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   TALLEYRAND — Divine Right / Authority: 95/100   Skill: 10   DP: 5/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary → Neutral (+24, 3 turns) /   Status: Active, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, now …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── BottomLeftUI (layer 0) [scrolled 2137 of 2137 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,364
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
map: unchanged (52 labels)
```

```
#0105  type buy off Sweden  ->  ok
  (typed and Enter)
view: <run>\frames\0105_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── BottomLeftUI (layer 0) [scrolled 2248 of 2248 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,364
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► buy off Sweden
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
map: unchanged (52 labels)
```

```
#0106  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0106_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   At War (3)
   Treaties (9)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  +14 (Neutral)  [MISSION]]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2248 of 2248 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
   ► buy off Sweden
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
map: unchanged (52 labels)
```

```
#0107  scroll 1825 600 down 15  ->  ok
  (scrolled down 15 at (1825, 600))
view: <run>\frames\0107_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 604 of 643 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Vassals (3)
   Neutral (4)
   controls: [icon: Close (Esc) @(2075,284)]  [Papal States  —  Open Borders  |  -10 (Wary)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Sweden  —  Peace  |  -57 (Hostile)]  [Naples  —  Peace  |  -27 (Wary)]  [Hanover  —  Peace  |  -47 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2248 of 2248 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
   ► buy off Sweden
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
map: unchanged (52 labels)
```

```
#0108  click Sweden  —  Peace  ->  ok
  (clicked at (1825, 587))
view: <run>\frames\0108_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 46 px, 0 of 392 px] ──
   DIPLOMACY — Sweden
   DP: 5
   TALLEYRAND'S ASSESSMENT — SWEDEN / Status: Peace   Relation: -57 (Hostile) /  / "Relations with Sweden remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus.
   Their design is aimed at France herself.
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1368g) (1 DP + 1368g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Open Borders (1 DP)  —  Hopeless](disabled: Relations with Sweden stand at -57; an Open Borders needs -20.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2248 of 2248 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
   ► buy off Sweden
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
map: unchanged (52 labels)
```

```
#0109  click Buy Off Their Design (1368g)  ->  ok
  (clicked at (1825, 540))
view: <run>\frames\0109_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 82 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Hesse @(2308,64)]  [icon: Treaty with Papal States @(2350,64)]  [icon: Treaty with Denmark @(2392,64)]  [icon: Treaty with Saxony @(2434,64)]  [icon: Treaty with Prussia @(2476,64)]  [+3]
── DiplomaticLedger (layer 50) ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 4/7
   TALLEYRAND — Divine Right / Authority: 95/100   Skill: 10   DP: 4/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary → Neutral (+24, 3 turns) /   Status: Active, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, now …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Austria + Russia
   +22
   T:3
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [scrolled 2380 of 2380 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   1,101
   Inf:
   86,499
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
   ► buy off Sweden
   Sweden's design — Scourge of the Usurper — is bought off for 1368 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (52 labels)
```

```
#0110  type Lannes, attack Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0110_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Lannes (13,139; expect about 93,744 with the corps likely to arrive, up to 95,868 if all march) vs Archduke Charles (28,600 men) at Franconia — the balance of force looks favorable.
  WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 96%) (The corps system lowers the bar by 10)
  WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
  WILL JOIN — Murat: will march to the sound of the guns — but he and Lannes are at odds; expect about half his weight — likely to make it in time (about 100%) (The corps system lowers the bar by 10)
  WILL JOIN — Bernadotte: stands on the field and will fight beside him
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
  The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
  The band weighs more than the men: Archduke Charles stands +3% on the defense (his stance, his character and his works).
  Franconia feeds 60,000 — the whole muster standing there would lose ~4,867 men a turn to short supply.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
  Bernadotte shares the field at Franconia — his men will absorb part of any losses.


[Combat] Lannes leads the charge! 
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Murat
   16,003 → 15,730
   Ney
   17,390 → 16,647
   Davout
   19,522 → 18,684
   ⚔
   Lannes ◆
   Archduke Charles ◆
   marched to the guns
   13,139 → 12,390 → 12,267 after the advance
   28,600 → 17,098
   marched to the guns
   marched to the guns
   +2 corps in reserve — 750 lost
   THE GREAT FOURTH BATTLE OF FRANCONIA
   click anywhere to skip ▸
   FRANCONIA · TURN 4
── TopBar (layer 75) [under a modal] ──
   DP: 4/7
   Threat 90 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Hesse @(2308,64)]  [icon: Treaty with Papal States @(2350,64)]  [icon: Treaty with Denmark @(2392,64)]  [icon: Treaty with Saxony @(2434,64)]  [icon: Treaty with Prussia @(2476,64)]  [+3]
── DiplomaticLedger (layer 50) [under a modal] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 4/7
   TALLEYRAND — Divine Right / Authority: 100/100   Skill: 10   DP: 4/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary → Neutral (+24, 3 turns) /   Status: Active, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, no …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Russia
   +29
   T:3
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2567 of 2567 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   934
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Berthier notes that Soult has been holding position for some time while others receive commands. He may begin to feel... overlooked.
   Murat is eyeing Archduke Charles's position at Franconia. I cannot guarantee he will wait for orders, Sire — give him something to do and he will stand down.
   DIPLOMATIC EVENTS
   Sire — Denmark and France have signed the Non-Aggression Pact.
   Sire — Saxony and France have signed the Open Borders Agreement.
   An envoy from Hesse has arrived with a proposal.
   An envoy from the Papal States has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 14.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Hesse — Non Aggression
   - Papal States — Open Borders
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Austria — the homeland — 28 of 28 provinces held  |  Settlement: Favorable Terms (+23)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 82/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The butcher's bill is heavy, Sire. The army feels it."
   ════════════════════════════════════
   You have accepted Hesse's proposal. Treaty signed: Peace → Non-Aggression with Hesse.
   You have accepted the Papal States's proposal. Treaty signed: Peace → Open Borders with the Papal States.
   ► buy off Sweden
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
   ► buy off Sweden
   Sweden's design — Scourge of the Usurper — is bought off for 1368 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► Lannes, attack Archduke Charles
   ⚔ The Great Fourth Battle of Franconia ⚔
   MUSTER — Lannes (13,139; expect about 93,744 with the corps likely to arrive, up to 95,868 if all march) vs Archduke Charles (28,600 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 96%) (The corps system lowers the bar by 10)
   WILL JOIN — Davout: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
   WILL JOIN — Murat: will march to the sound of the guns — but he and Lannes are at odds; expect about half his weight — likely to make it in time (about 100%) (The corps system lowers the bar by 10)
   WILL JOIN — Bernadotte: stands on the field and will fight beside him
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   The band weighs more than the men: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~4,867 men a turn to short supply.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Bernadotte shares the field at Franconia — his men will absorb part of any losses.
   [Combat] Lannes leads the charge! (Aggressive: +15% attack)
   [Combat] Lannes's combined arms coordination! (+10% attack)
   Lannes's forces press forward aggressively. Lannes gains the advantage over Archduke Charles. Casualties: Lannes's army 3,353, Archduke Charles 11,502. Both armies remain in the field. Lannes advances into Franconia. (123 lost to march)
   [Materiel] Guns, horses and stores lost with the fallen: France -167g, Austria -575g.
   Napoleon answered the guns and stands at Franconia; his march to Rhineland stands and resumes next turn.
   ⚔ View the field
   [3/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Lannes!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Lannes!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat's forces arrived to reinforce Lannes!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Lannes!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 13,139 (lead) + 82,729 committed (Ney, Davout, Murat, Napoleon, Bernadotte) = 95,868.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,604 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Lannes: "The field is ours! Give me leave and I will take the next one before dusk."
   Davout fought like a man with something to prove — and proved it. His grievance is settled. Murat fought like a man with something to prove — and proved it. His grievance is settled.
   Attack: Lannes (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Lannes's own corps 749 | Archduke Charles 11,502
   Strength: Lannes 13,139 → 12,390 → 12,267 after the advance | Archduke Charles 28,600 → 17,098
   Berthier: "Reinforcements! Ney, Davout, Murat and Napoleon marched onto the field beside Lannes. The enemy's advantage melted away."
   The war's cost now stands at 40,403 of our men.
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1507,597)  France(943,537)  Bavaria(1309,507)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  31(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Archduke Charles(1377,319)  Ney +5(1348,427)  ?(1367,291)  Brunswick(1368,263)  Deroy(1251,466)  Soult(1213,387)  ?(832,626)  Castanos(832,586)  ?(1368,599)  Archduke John(1355,559)  Dumonceau(1129,301)  Massena(1295,612)  Teulie(1325,585)  ?(1495,430)  ?(1367,363)  ?(1263,583)  ?(1290,428)  25k(942,504)  12k(890,454)  ?(1145,600)  10k(1129,412)  12k(1080,412)  10k(1310,677)
```

```
#0111  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Lannes ◆' (PanelContainer, layer 121))
view: <run>\frames\0111_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A FIELD OF LEGEND IS WON
   FRANCE LOSSES
   AUSTRIA LOSSES
   3,353
   11,502
   Murat
   16,003 → 15,730
   Ney
   17,390 → 16,647
   Davout
   19,522 → 18,684
   ⚔
   Lannes ◆
   Archduke Charles ◆
   marched to the guns
   13,139 → 12,390 → 12,267 after the advance
   28,600 → 17,098
   marched to the guns
   marched to the guns
   +2 corps in reserve — 750 lost
   Berthier: “Reinforcements! Ney, Davout, Murat and Napoleon marched onto the field beside Lannes. The enemy's advantage melted away.” / Archduke Charles: "I spend ground as a miser spends coin — rarely, and never twice."
   THE GREAT FOURTH BATTLE OF FRANCONIA
   FRANCONIA · TURN 4
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2567 of 2567 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Casualties: Lannes's own corps 749 | Archduke Charles 11,502
   Strength: Lannes 13,139 → 12,390 → 12,267 after the advance | Archduke Charles 28,600 → 17,098
   Berthier: "Reinforcements! Ney, Davout, Murat and Napoleon marched onto the field beside Lannes. The enemy's advantage melted away."
   The war's cost now stands at 40,403 of our men.
map: unchanged (51 labels)
```

```
#0112  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0112_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2567 of 2567 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Casualties: Lannes's own corps 749 | Archduke Charles 11,502
   Strength: Lannes 13,139 → 12,390 → 12,267 after the advance | Archduke Charles 28,600 → 17,098
   Berthier: "Reinforcements! Ney, Davout, Murat and Napoleon marched onto the field beside Lannes. The enemy's advantage melted away."
   The war's cost now stands at 40,403 of our men.
map: unchanged (51 labels)
```

```
#0113  type Davout, move to Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0113_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: Cannot advance while engaged with Archduke Charles at Franconia. No friendly province adjoins him: he must fight or stand.
'Davout, attack Archduke Charles' fights; 'Davout, hold' stands.
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2700 of 2700 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   934
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, move to Swabia
   Cannot advance while engaged with Archduke Charles at Franconia. No friendly province adjoins him: he must fight or stand.
   'Davout, attack Archduke Charles' fights; 'Davout, hold' stands.
map: unchanged (51 labels)
```

```
#0114  type Davout, attack Archduke Charles  ->  ok
  (typed and Enter)
view: <run>\frames\0114_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Davout (18,684; expect about 83,064 with the corps likely to arrive) vs Archduke Charles (17,098 men) at Franconia — the balance of force looks favorable.
  WILL JOIN — Ney: stands on the field and will fight beside him
  WILL JOIN — Lannes: stands on the field and will fight beside him
  WILL JOIN — Murat: stands on the field and will fight beside him
  WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
  WILL JOIN — Napoleon: stands on the field and will fight beside him
  The Emperor commands in person — every corps on this field fights +10% harder.
  The band weighs more than the men: Davout attacks from a defensive stance (−10%); all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +13% on the defense (his stance, his character and his works).
  Franconia feeds 60,000 — the whole muster standing there would lose ~4,598 men a turn to short supply.
  Every corps in the province shares the field — that is the design, and the quarrel above is its one exception: no order holds a corps out of its own province, but a feud does. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
  Napoleon shares the field at Franconia — his men will absorb part of any losses.


Davout holds them at Franconia while allies attack from Swabia! (+1 coordination)

[Combat] Davout's DEFENSIVE stance hampers offensive operations (-10% attack)
[Shield] A
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   AUSTRIA LOSSES
   0
   0
   Lannes
   12,267 → 12,143
   Murat
   15,730 → 15,571
   Ney
   16,647 → 16,479
   ⚔
   Davout ◆
   Archduke Charles ◆
   18,684 → 18,366
   17,098 → 7,886
   +1 corps in reserve — 91 lost
   FIFTH BATTLE OF FRANCONIA
   click anywhere to skip ▸
   FRANCONIA · TURN 4
── TopBar (layer 75) [under a modal] ──
   DP: 4/7
   Threat 98 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Hesse @(2308,64)]  [icon: Treaty with Papal States @(2350,64)]  [icon: Treaty with Denmark @(2392,64)]  [icon: Treaty with Saxony @(2434,64)]  [icon: Treaty with Prussia @(2476,64)]  [+3]
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Austria + Russia
   +34
   T:3
   controls: [THIRD COALITION  ▸]  [Britain + Austria + Russia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 3145 of 3145 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   891
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   WILL JOIN — Bernadotte: stands on the field and will fight beside him
   WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10)
   The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
   The band weighs more than the men: Archduke Charles stands +3% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~4,867 men a turn to short supply.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Bernadotte shares the field at Franconia — his men will absorb part of any losses.
   [Combat] Lannes leads the charge! (Aggressive: +15% attack)
   [Combat] Lannes's combined arms coordination! (+10% attack)
   Lannes's forces press forward aggressively. Lannes gains the advantage over Archduke Charles. Casualties: Lannes's army 3,353, Archduke Charles 11,502. Both armies remain in the field. Lannes advances into Franconia. (123 lost to march)
   [Materiel] Guns, horses and stores lost with the fallen: France -167g, Austria -575g.
   Napoleon answered the guns and stands at Franconia; his march to Rhineland stands and resumes next turn.
   ⚔ View the field
   [3/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Ney's forces arrived to reinforce Lannes!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's forces arrived to reinforce Lannes!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat's forces arrived to reinforce Lannes!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Lannes!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 13,139 (lead) + 82,729 committed (Ney, Davout, Murat, Napoleon, Bernadotte) = 95,868.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,604 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Lannes: "The field is ours! Give me leave and I will take the next one before dusk."
   Davout fought like a man with something to prove — and proved it. His grievance is settled. Murat fought like a man with something to prove — and proved it. His grievance is settled.
   Attack: Lannes (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Lannes's own corps 749 | Archduke Charles 11,502
   Strength: Lannes 13,139 → 12,390 → 12,267 after the advance | Archduke Charles 28,600 → 17,098
   Berthier: "Reinforcements! Ney, Davout, Murat and Napoleon marched onto the field beside Lannes. The enemy's advantage melted away."
   The war's cost now stands at 40,403 of our men.
   ► Davout, move to Swabia
   Cannot advance while engaged with Archduke Charles at Franconia. No friendly province adjoins him: he must fight or stand.
   'Davout, attack Archduke Charles' fights; 'Davout, hold' stands.
   ► Davout, attack Archduke Charles
   ⚔ Fifth Battle of Franconia ⚔
   MUSTER — Davout (18,684; expect about 83,064 with the corps likely to arrive) vs Archduke Charles (17,098 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: stands on the field and will fight beside him
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him
   WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   The band weighs more than the men: Davout attacks from a defensive stance (−10%); all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +13% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~4,598 men a turn to short supply.
   Every corps in the province shares the field — that is the design, and the quarrel above is its one exception: no order holds a corps out of its own province, but a feud does. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Napoleon shares the field at Franconia — his men will absorb part of any losses.
   Davout holds them at Franconia while allies attack from Swabia! (+1 coordination)
   [Combat] Davout's DEFENSIVE stance hampers offensive operations (-10% attack)
   [Shield] Archduke Charles stands firm against superior numbers! (Cautious: +10% outnumbered)
   [Combat] Davout's combined arms coordination! (+10% attack)
   Davout attacks with overwhelming force. Davout gains the advantage over Archduke Charles. Casualties: Davout's army 860, Archduke Charles 9,212. Both armies remain in the field. Franconia remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Materiel] Guns, horses and stores lost with the fallen: France -43g, Austria -460g.
   [!] Archduke Charles's broken army flees to Tyrol! (recovering for 2 turns)
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout fought with Ney, Lannes, Murat and Napoleon beside him — massed effective strength: 18,684 (lead) + 64,380 committed (Ney, Lannes, Murat, Napoleon) = 83,064.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's supporting allies lost 542 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Davout: "Victory, at an acceptable price. The pickets are already posted."
   Attack: Davout (Defensive stance -10%, Flanking +1%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Outnumbered (cautious) +10%, Habsburg Resolve +3%)
   Casualties: Davout's own corps 318 | Archduke Charles 9,212
   Strength: Davout 18,684 → 18,366 | Archduke Charles 17,098 → 7,886
   Berthier: "Archduke Charles bled two men for each of Davout's. A clear exchange, not yet a decision."
   The war's cost now stands at 41,263 of our men.
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1507,597)  France(943,537)  Bavaria(1309,507)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  31(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Ney +5(1348,427)  ?(1367,302)  Brunswick(1368,263)  Deroy(1251,466)  Soult(1213,387)  ?(832,626)  Castanos(832,586)  ?(1368,599)  Archduke Charles(1345,559)  Archduke John(1364,474)  Dumonceau(1129,301)  Massena(1295,612)  Teulie(1325,585)  ?(1495,430)  ?(1367,363)  ?(1300,642)  ?(1290,428)  25k(942,504)  12k(890,454)  ?(1145,600)  10k(1129,412)  12k(1080,412)  10k(1310,677)
```

```
#0115  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Davout ◆' (PanelContainer, layer 121))
view: <run>\frames\0115_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS OURS
   FRANCE LOSSES
   AUSTRIA LOSSES
   860
   9,212
   Lannes
   12,267 → 12,143
   Murat
   15,730 → 15,571
   Ney
   16,647 → 16,479
   ⚔
   Davout ◆
   Archduke Charles ◆
   18,684 → 18,366
   17,098 → 7,886
   +1 corps in reserve — 91 lost
   ROUTED
   Berthier: “Archduke Charles bled two men for each of Davout's. A clear exchange, not yet a decision.” / Archduke Charles: "Austria retires to fight again — it is the thing we do best."
   FIFTH BATTLE OF FRANCONIA
   FRANCONIA · TURN 4
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3145 of 3145 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Casualties: Davout's own corps 318 | Archduke Charles 9,212
   Strength: Davout 18,684 → 18,366 | Archduke Charles 17,098 → 7,886
   Berthier: "Archduke Charles bled two men for each of Davout's. A clear exchange, not yet a decision."
   The war's cost now stands at 41,263 of our men.
map: unchanged (51 labels)
```

```
#0116  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0116_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3145 of 3145 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Casualties: Davout's own corps 318 | Archduke Charles 9,212
   Strength: Davout 18,684 → 18,366 | Archduke Charles 17,098 → 7,886
   Berthier: "Archduke Charles bled two men for each of Davout's. A clear exchange, not yet a decision."
   The war's cost now stands at 41,263 of our men.
map: unchanged (51 labels)
```

```
#0117  type Murat, move to Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0117_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat moves from Franconia to Swabia (155 lost to march)
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3256 of 3256 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   891
   Inf:
   86,499
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
   ► Murat, move to Swabia
   → Murat moves from Franconia to Swabia (155 lost to march)
   [1/4 actions remaining]
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1507,597)  France(943,537)  Bavaria(1309,507)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  31(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Ney +4(1348,427)  ?(1367,302)  Brunswick(1368,263)  Murat(1236,466)  Deroy(1265,438)  Soult(1213,387)  ?(832,626)  Castanos(832,586)  ?(1368,599)  Archduke Charles(1345,559)  Archduke John(1364,474)  Dumonceau(1129,301)  Massena(1295,612)  Teulie(1325,585)  ?(1495,430)  ?(1367,363)  ?(1300,642)  ?(1290,360)  25k(942,504)  12k(890,454)  ?(1145,600)  10k(1129,412)  12k(1080,412)  10k(1310,677)
```

```
#0118  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0118_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 4
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   At War (3)
   Treaties (9)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Austria  —  At War  |  -80 (Hostile)]  [Prussia  —  Open Borders  |  +14 (Neutral)  [MISSION]]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3256 of 3256 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   The war's cost now stands at 41,263 of our men.
   ► Murat, move to Swabia
   → Murat moves from Franconia to Swabia (155 lost to march)
   [1/4 actions remaining]
map: unchanged (52 labels)
```

```
#0119  click Austria  —  At War  ->  ok
  (clicked at (1825, 601))
view: <run>\frames\0119_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 200 px, 0 of 182 px] ──
   DIPLOMACY — Austria
   DP: 4
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: At War   Relation: -80 (Hostile) /  / "Austria falters, Your Excellency. Our armies press the advantage — we may dictate the terms, though a court not yet broken will be slow to sign them." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus. /  / KEY FACTORS /   + Base willingne …
   Mission already active
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Doubtful — may counter]  [Open Settlement]  [Propose White Peace]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5](disabled: Mission already active)  [Undermine Alliances (2 DP)  —  -4 relation between targets/turn](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3256 of 3256 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   The war's cost now stands at 41,263 of our men.
   ► Murat, move to Swabia
   → Murat moves from Franconia to Swabia (155 lost to march)
   [1/4 actions remaining]
map: unchanged (52 labels)
```

```
#0120  click Open Settlement  ->  ok
  (clicked at (1825, 503))
view: <run>\frames\0120_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px, 0 of 135 px, 0 of 398 px] ──
   This settlement cannot be ratified now. / France vs Austria + Britain + Russia - Whole-war settlement / Covered enemies: Austria, Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 17/50, Britain 11/50, Russia 11/50. / Treasury 891 gold: committed 0 / reserve 500 / remaining 391 / Sire, this settlement of France vs Austria + Britain + Russia seats 3 court …
   The table /   * Austria ▸ - Holding out (17/50) White peace /       Blocker: Settlement legitimacy /       Metternich regrets that Austria must remain… unconvinced — it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. He offers Vienna's compliments on Marshal Ney's laurels at Franconia — compliments, he notes, are not a signature. /  …
   Austria:
   Britain:
   Russia:
   Sire, a white peace for France vs Austria + Britain + Russia cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. Author terms or hold until the field shifts. London and Vilna are unbeaten — a whole-war peace needs their consent (Austria 17/50, Britain 11/50, Russia 11/50). Press Austria alone: the separ …
   controls: <Austria ▸>  <+ Add demand>  <Britain ▸>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Drop Austria]  [Press Britain]  [Ease Britain]  [Drop Britain]  [Press Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 4/7
   Threat 98 / 100
   Turn 4 — Early November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 4/7
   TALLEYRAND — Divine Right / Authority: 100/100   Skill: 10   DP: 4/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary → Neutral (+24, 3 turns) /   Status: Active, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, no …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── BottomLeftUI (layer 0) [under a modal] [scrolled 3301 of 3301 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   891
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose common peace with Austria
map: unchanged (52 labels)
```

```
#0121  click Drop Britain  ->  ok
  (clicked at (1782, 613))
view: <run>\frames\0121_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 68 px, 0 of 24 px, 0 of 332 px] ──
   This settlement cannot be ratified now. / France vs Austria + Russia - Separate settlement / Covered enemies: Austria, Russia / Still at war: Britain / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 20/50, Russia 14/50. / Treasury 891 gold: committed 0 / reserve 500 / remaining 391 / Sire, this settlement of France vs Austria + Russia seats 2 courts at the table. Austr …
   The table /   * Austria ▸ - Holding out (20/50) White peace /       Blocker: Settlement legitimacy /       Metternich regrets that Austria must remain… unconvinced — it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. He offers Vienna's compliments on Marshal Ney's laurels at Franconia — compliments, he notes, are not a signature. /  …
   Austria:
   Russia:
   Coverage:
   Sire, a white peace for France vs Austria + Russia cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. Author terms or hold until the field shifts. Vilna is unbeaten — a whole-war peace needs its consent (Austria 20/50, Russia 14/50). Press Austria alone: the separate peace. It costs 3 diplomatic points …
   controls: <Austria ▸>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Drop Austria]  [Press Russia]  [Ease Russia]  [Drop Russia]  [Bring Britain to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3322 of 3322 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   891
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement cover drop
map: unchanged (52 labels)
```

```
#0122  click Drop Russia  ->  ok
  (clicked at (1782, 613))
view: <run>\frames\0122_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px, 0 of 244 px] ──
   This settlement cannot be ratified now. / France vs Austria - Separate settlement / Covered enemies: Austria / Still at war: Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 37/50. / Treasury 891 gold: committed 0 / reserve 500 / remaining 391 / Sire, this settlement of France vs Austria seats 1 courts at the table. Austria will not sign; the settlement …
   The table /   * Austria ▸ - Holding out (close) (37/50) White peace /       Blocker: National design /       Austria Holding out → Holding out (close) /       Metternich allows that Austria is… persuadable — though it would seal their national design out of reach. /       + Add demand / Austria is the holdout. / ▸ Austria won't accept these terms yet. Use 'More generous' (or ease a court) until ea …
   Austria:
   Coverage:
   Sire, a white peace for France vs Austria cannot be sealed as it stands: it would seal their national design out of reach. Author terms or hold until the field shifts. Every covered court has been beaten in the field — a whole-war peace still needs each one's consent (Austria 37/50). Press Austria alone: the separate peace. It costs 3 diplomatic points; you have 4. /  / Allies and Standing /   * A …
   controls: <Austria ▸>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Bring Britain to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3345 of 3345 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   891
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement cover drop
map: unchanged (52 labels)
```

```
#0123  click Ease Austria  ->  ok
  (clicked at (1624, 597))
view: <run>\frames\0123_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px, 0 of 244 px] ──
   This settlement cannot be ratified now. / France vs Austria - Separate settlement / Covered enemies: Austria / Still at war: Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 41/50. / Treasury 891 gold: committed 100 / reserve 500 / remaining 291 / Sire, this settlement of France vs Austria seats 1 courts at the table. Austria will not sign; the settleme …
   The table /   * Austria ▸ - Holding out (close) (41/50) Conceded: 100g /       Blocker: National design /       Metternich allows that Austria is… persuadable — though the terms cut against their national design. /       Conceded · France pays 100 gold  [-][+]  Remove /       + Add demand / Austria is the holdout. / ▸ Austria won't accept these terms yet. Use 'More generous' (or ease a court) unti …
   Austria:
   Coverage:
   Sire, the settlement of France vs Austria cannot be ratified now: the terms cut against their national design. Revise terms or stand down before pressing further. Every covered court has been beaten in the field — a whole-war peace still needs each one's consent (Austria 41/50). Press Austria alone: the separate peace. It costs 3 diplomatic points; you have 4. /  / Allies and Standing /   * Austri …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Bring Britain to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3367 of 3367 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   891
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0124  click Ease Austria  ->  ok
  (clicked at (1624, 597))
view: <run>\frames\0124_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px, 0 of 244 px] ──
   This settlement cannot be ratified now. / France vs Austria - Separate settlement / Covered enemies: Austria / Still at war: Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 45/50. / Treasury 891 gold: committed 200 / reserve 500 / remaining 191 / Sire, this settlement of France vs Austria seats 1 courts at the table. Austria will not sign; the settleme …
   The table /   * Austria ▸ - Holding out (close) (45/50) Conceded: 200g /       Blocker: National design /       Metternich allows that Austria is… persuadable — though the terms cut against their national design. /       Conceded · France pays 200 gold  [-][+]  Remove /       + Add demand / Austria is the holdout. / ▸ Austria won't accept these terms yet. Use 'More generous' (or ease a court) unti …
   Austria:
   Coverage:
   Sire, the settlement of France vs Austria cannot be ratified now: the terms cut against their national design. Revise terms or stand down before pressing further. Every covered court has been beaten in the field — a whole-war peace still needs each one's consent (Austria 45/50). Press Austria alone: the separate peace. It costs 3 diplomatic points; you have 4. /  / Allies and Standing /   * Austri …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Bring Britain to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3389 of 3389 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   891
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0125  click Ease Austria  ->  ok
  (clicked at (1624, 597))
view: <run>\frames\0125_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px, 0 of 244 px] ──
   This settlement cannot be ratified now. / France vs Austria - Separate settlement / Covered enemies: Austria / Still at war: Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Austria 49/50. / Treasury 891 gold: committed 300 / reserve 500 / remaining 91 / Sire, this settlement of France vs Austria seats 1 courts at the table. Austria will not sign; the settlemen …
   The table /   * Austria ▸ - Holding out (close) (49/50) Conceded: 300g /       Blocker: National design /       Metternich allows that Austria is… persuadable — though the terms cut against their national design. /       Conceded · France pays 300 gold  [-][+]  Remove /       + Add demand / Austria is the holdout. / ▸ Austria won't accept these terms yet. Use 'More generous' (or ease a court) unti …
   Austria:
   Coverage:
   Sire, the settlement of France vs Austria cannot be ratified now: the terms cut against their national design. Revise terms or stand down before pressing further. Every covered court has been beaten in the field — a whole-war peace still needs each one's consent (Austria 49/50). Press Austria alone: the separate peace. It costs 3 diplomatic points; you have 4. /  / Allies and Standing /   * Austri …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Bring Britain to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3411 of 3411 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   891
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0126  click Ease Austria  ->  ok
  (clicked at (1624, 597))
view: <run>\frames\0126_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 134 px] ──
   Settlement of France vs Austria — ready for ratification / France vs Austria - Separate settlement / Covered enemies: Austria / Still at war: Britain, Russia / Will carry as drafted — every court at or above 50. / Treasury 891 gold: committed 400 / reserve 491 / remaining 0 / Sire, this settlement of France vs Austria seats 1 courts at the table. Every court at the table will sign; the settlement  …
   The table /   * Austria ▸ - Will sign (53/50) Conceded: 400g /       Austria Holding out (close) → Will sign /       Metternich signals that Austria will sign the settlement of France vs Austria. /       Conceded · France pays 400 gold  [-][+]  Remove /       + Add demand / This peace carries.
   Austria:
   Coverage:
   Sire, the settlement of France vs Austria stands ready for ratification. Acceptance reads as Will sign; what weighs heaviest: no single dominant pressure. /  / Allies and Standing /   * Austria - Seat at settlement (Defenders) /   * France - Seat at settlement (Attackers, war leader) /   * Bavaria - Consulted ally (Attackers) /   * Holland - No settlement standing (Attackers) /  / Terms /   * End  …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Separate peace with Austria]  [Bring Britain to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3433 of 3433 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   891
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0127  scroll 1825 760 down 5  ->  ok
  (scrolled down 5 at (1825, 760))
view: <run>\frames\0127_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 110 of 134 px] ──
   Settlement of France vs Austria — ready for ratification / France vs Austria - Separate settlement / Covered enemies: Austria / Still at war: Britain, Russia / Will carry as drafted — every court at or above 50. / Treasury 891 gold: committed 400 / reserve 491 / remaining 0 / Sire, this settlement of France vs Austria seats 1 courts at the table. Every court at the table will sign; the settlement  …
   The table /   * Austria ▸ - Will sign (53/50) Conceded: 400g /       Austria Holding out (close) → Will sign /       Metternich signals that Austria will sign the settlement of France vs Austria. /       Conceded · France pays 400 gold  [-][+]  Remove /       + Add demand / This peace carries.
   Austria:
   Coverage:
   Sire, the settlement of France vs Austria stands ready for ratification. Acceptance reads as Will sign; what weighs heaviest: no single dominant pressure. /  / Allies and Standing /   * Austria - Seat at settlement (Defenders) /   * France - Seat at settlement (Attackers, war leader) /   * Bavaria - Consulted ally (Attackers) /   * Holland - No settlement standing (Attackers) /  / Terms /   * End  …
   controls: <Austria ▸>  <Remove>  <+ Add demand>  [Press Austria]  [Ease Austria]  [Separate peace with Austria]  [Bring Britain to the table]  [Bring Russia to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3433 of 3433 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
map: unchanged (52 labels)
```

```
#0128  click Submit for Review  ->  ok
  (clicked at (2203, 884))
view: <run>\frames\0128_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   Settlement of France vs Austria — ready for ratification / France vs Austria - Separate settlement / STAGED FOR REVIEW — the terms are frozen. Ratify, revise, or return to shaping. / Covered enemies: Austria / Still at war: Britain, Russia / Will carry as drafted — every court at or above 50. / Sire, this settlement of France vs Austria seats 1 courts at the table. Every court at the table will si …
   The table /   * Austria - Will sign (53/50) Conceded: 400g /       Metternich signals that Austria will sign the settlement of France vs Austria. / This peace carries.
   Sire, the settlement of France vs Austria stands ready for ratification. Acceptance reads as Will sign; what weighs heaviest: no single dominant pressure. /  / Allies and Standing /   * Austria - Seat at settlement (Defenders) /   * France - Seat at settlement (Attackers, war leader) /   * Bavaria - Consulted ally (Attackers) /   * Holland - No settlement standing (Attackers) /  / Terms /   * End  …
   controls: [Ratify Settlement]  [Open War Detail]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3456 of 3456 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   891
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: submit settlement for review
map: unchanged (52 labels)
```

```
#0129  click Ratify Settlement  ->  ok
  (clicked at (1455, 828))
view: <run>\frames\0129_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 98 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(2032,64)]  [icon: Settlement Ratified @(2074,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Hesse @(2392,64)]  [icon: Treaty with Papal States @(2434,64)]  [icon: Austria Left Coalition @(2476,64)]  [+7]
── DiplomaticLedger (layer 50) [scrolled 0 of 816 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 4/7
   ═══ ACTIVE TREATIES ═══ /  / Sweden ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (2 turns ago) /  / Naples ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (2 turns ago) /  / Prussia ↔ France: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES](disabled: You are reading this book)  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <v Settlement of France vs Austria: Gold indemnity: 400 gold from France to Austria.>
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -1
   T:3
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [scrolled 3610 of 3610 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   491
   Inf:
   86,499
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
   Directing Talleyrand: confirm settlement
   Settlement Ratified: France vs Austria (3 pairs resolved).
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (52 labels)
```

```
#0130  click Bavaria petitions over settlement scope  ->  ok
  (clicked at (2032, 64))
view: <run>\frames\0130_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 98 / 100
   Turn 4 — Early November 1805
   Imperial Box
   Bavaria petitions over settlement scope
   T4
   Bavaria petitions for Tyrol as reward for its arms.
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(2032,64)]  [icon: Settlement Ratified @(2074,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Hesse @(2392,64)]  [icon: Treaty with Papal States @(2434,64)]  [icon: Austria Left Coalition @(2476,64)]  [+7]  [Open Envoys]  [Keep]  [Acknowledge]
── DiplomaticLedger (layer 50) [scrolled 0 of 816 px]: unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 3610 of 3610 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (52 labels)
```

```
#0131  click Open Envoys  ->  ok
  (clicked at (2433, 177))
view: <run>\frames\0131_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm', 'war_status_panel (not modal)'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   ALLY SETTLEMENT PETITION - BAVARIA /  / France vs Austria + Britain + Russia / Related claim: settlement /  / "The chancery of Bavaria petitions for Tyrol in the settlement of France vs Austria + Britain + Russia. Bavaria fought beside France in this war and presses its claim." /  / Claim at issue: Tyrol against Austria /  / Basis: Bavaria fought beside France in this war and presses its claim. /  …
   controls: [Grant the Claim](disabled: The draft has moved on — Bavaria's ask can no longer be granted as petitioned.)  [Decline]
── TopBar (layer 75) [under a modal] ──
   DP: 4/7
   Threat 98 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(2032,64)]  [icon: Settlement Ratified @(2074,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Hesse @(2392,64)]  [icon: Treaty with Papal States @(2434,64)]  [icon: Austria Left Coalition @(2476,64)]  [+7]
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 816 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 3610 of 3610 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   491
   Inf:
   86,499
   Cav:
   20,250
   Art:
   11,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
map: unchanged (52 labels)
```

```
#0132  click Decline  ->  ok
  (clicked at (1834, 727))
view: <run>\frames\0132_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 4 — Early November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 98 / 100
   Turn 4 — Early November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(2032,64)]  [icon: Settlement Ratified @(2074,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Hesse @(2392,64)]  [icon: Treaty with Papal States @(2434,64)]  [icon: Austria Left Coalition @(2476,64)]  [+7]
── DiplomaticLedger (layer 50) [scrolled 0 of 816 px]: unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2417 of 2417 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   4
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   491
   Inf:
   86,499
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
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Murat's forces arrived to reinforce Lannes!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Napoleon's forces arrived to reinforce Lannes!
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Massed effective strength: 13,139 (lead) + 82,729 committed (Ney, Davout, Murat, Napoleon, Bernadotte) = 95,868.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   His supporting allies lost 2,604 men combined.
   └─────────────────────┘
   --- Berthier's Report ---
   Lannes: "The field is ours! Give me leave and I will take the next one before dusk."
   Davout fought like a man with something to prove — and proved it. His grievance is settled. Murat fought like a man with something to prove — and proved it. His grievance is settled.
   Attack: Lannes (Personality (aggressive) +15%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Habsburg Resolve +3%)
   Casualties: Lannes's own corps 749 | Archduke Charles 11,502
   Strength: Lannes 13,139 → 12,390 → 12,267 after the advance | Archduke Charles 28,600 → 17,098
   Berthier: "Reinforcements! Ney, Davout, Murat and Napoleon marched onto the field beside Lannes. The enemy's advantage melted away."
   The war's cost now stands at 40,403 of our men.
   ► Davout, move to Swabia
   Cannot advance while engaged with Archduke Charles at Franconia. No friendly province adjoins him: he must fight or stand.
   'Davout, attack Archduke Charles' fights; 'Davout, hold' stands.
   ► Davout, attack Archduke Charles
   ⚔ Fifth Battle of Franconia ⚔
   MUSTER — Davout (18,684; expect about 83,064 with the corps likely to arrive) vs Archduke Charles (17,098 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: stands on the field and will fight beside him
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him
   WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   The band weighs more than the men: Davout attacks from a defensive stance (−10%); all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +13% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~4,598 men a turn to short supply.
   Every corps in the province shares the field — that is the design, and the quarrel above is its one exception: no order holds a corps out of its own province, but a feud does. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Napoleon shares the field at Franconia — his men will absorb part of any losses.
   Davout holds them at Franconia while allies attack from Swabia! (+1 coordination)
   [Combat] Davout's DEFENSIVE stance hampers offensive operations (-10% attack)
   [Shield] Archduke Charles stands firm against superior numbers! (Cautious: +10% outnumbered)
   [Combat] Davout's combined arms coordination! (+10% attack)
   Davout attacks with overwhelming force. Davout gains the advantage over Archduke Charles. Casualties: Davout's army 860, Archduke Charles 9,212. Both armies remain in the field. Franconia remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Materiel] Guns, horses and stores lost with the fallen: France -43g, Austria -460g.
   [!] Archduke Charles's broken army flees to Tyrol! (recovering for 2 turns)
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout fought with Ney, Lannes, Murat and Napoleon beside him — massed effective strength: 18,684 (lead) + 64,380 committed (Ney, Lannes, Murat, Napoleon) = 83,064.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's supporting allies lost 542 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Davout: "Victory, at an acceptable price. The pickets are already posted."
   Attack: Davout (Defensive stance -10%, Flanking +1%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Outnumbered (cautious) +10%, Habsburg Resolve +3%)
   Casualties: Davout's own corps 318 | Archduke Charles 9,212
   Strength: Davout 18,684 → 18,366 | Archduke Charles 17,098 → 7,886
   Berthier: "Archduke Charles bled two men for each of Davout's. A clear exchange, not yet a decision."
   The war's cost now stands at 41,263 of our men.
   ► Murat, move to Swabia
   → Murat moves from Franconia to Swabia (155 lost to march)
   [1/4 actions remaining]
   ► propose common peace with Austria
   Directing Talleyrand: settlement cover drop
   Directing Talleyrand: settlement cover drop
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: submit settlement for review
   Directing Talleyrand: confirm settlement
   Settlement Ratified: France vs Austria (3 pairs resolved).
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Directing Talleyrand: decline ally petition
   The chancery of Bavaria records France's refusal in cool terms.
map: unchanged (52 labels)
```

```
#0133  click End Turn (E)  ->  ok
  (clicked at (617, 978))
view: <run>\frames\0133_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 4
   BAVARIA / ──────────────────────────── / - Deroy holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 97 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 816 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   ═══ ACTIVE TREATIES ═══ /  / Sweden ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (3 turns ago) /  / Naples ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (3 turns ago) /  / Prussia ↔ France: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES](disabled: You are reading this book)  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <v Settlement of France vs Austria: Gold indemnity: 400 gold from France to Austria.>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2430 of 2431 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,150
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Cannot advance while engaged with Archduke Charles at Franconia. No friendly province adjoins him: he must fight or stand.
   'Davout, attack Archduke Charles' fights; 'Davout, hold' stands.
   ► Davout, attack Archduke Charles
   ⚔ Fifth Battle of Franconia ⚔
   MUSTER — Davout (18,684; expect about 83,064 with the corps likely to arrive) vs Archduke Charles (17,098 men) at Franconia — the balance of force looks favorable.
   WILL JOIN — Ney: stands on the field and will fight beside him
   WILL JOIN — Lannes: stands on the field and will fight beside him
   WILL JOIN — Murat: stands on the field and will fight beside him
   WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
   WILL JOIN — Napoleon: stands on the field and will fight beside him
   The Emperor commands in person — every corps on this field fights +10% harder.
   The band weighs more than the men: Davout attacks from a defensive stance (−10%); all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +13% on the defense (his stance, his character and his works).
   Franconia feeds 60,000 — the whole muster standing there would lose ~4,598 men a turn to short supply.
   Every corps in the province shares the field — that is the design, and the quarrel above is its one exception: no order holds a corps out of its own province, but a feud does. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Napoleon shares the field at Franconia — his men will absorb part of any losses.
   Davout holds them at Franconia while allies attack from Swabia! (+1 coordination)
   [Combat] Davout's DEFENSIVE stance hampers offensive operations (-10% attack)
   [Shield] Archduke Charles stands firm against superior numbers! (Cautious: +10% outnumbered)
   [Combat] Davout's combined arms coordination! (+10% attack)
   Davout attacks with overwhelming force. Davout gains the advantage over Archduke Charles. Casualties: Davout's army 860, Archduke Charles 9,212. Both armies remain in the field. Franconia remains Bavaria's soil — we drove the enemy from our ally's province; it is not ours to take.
   [Materiel] Guns, horses and stores lost with the fallen: France -43g, Austria -460g.
   [!] Archduke Charles's broken army flees to Tyrol! (recovering for 2 turns)
   ⚔ View the field
   [2/4 actions remaining]
   ┌─── REINFORCEMENT ───┐
   Davout fought with Ney, Lannes, Murat and Napoleon beside him — massed effective strength: 18,684 (lead) + 64,380 committed (Ney, Lannes, Murat, Napoleon) = 83,064.
   └─────────────────────┘
   ┌─── REINFORCEMENT ───┐
   Davout's supporting allies lost 542 men.
   └─────────────────────┘
   --- Berthier's Report ---
   Davout: "Victory, at an acceptable price. The pickets are already posted."
   Attack: Davout (Defensive stance -10%, Flanking +1%, The Emperor commands in person +10%)
   Defense: Archduke Charles (Outnumbered (cautious) +10%, Habsburg Resolve +3%)
   Casualties: Davout's own corps 318 | Archduke Charles 9,212
   Strength: Davout 18,684 → 18,366 | Archduke Charles 17,098 → 7,886
   Berthier: "Archduke Charles bled two men for each of Davout's. A clear exchange, not yet a decision."
   The war's cost now stands at 41,263 of our men.
   ► Murat, move to Swabia
   → Murat moves from Franconia to Swabia (155 lost to march)
   [1/4 actions remaining]
   ► propose common peace with Austria
   Directing Talleyrand: settlement cover drop
   Directing Talleyrand: settlement cover drop
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: submit settlement for review
   Directing Talleyrand: confirm settlement
   Settlement Ratified: France vs Austria (3 pairs resolved).
   Settlement Ratified
   3 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 3
   Opening diplomatic ledger to settlement…
   Directing Talleyrand: decline ally petition
   The chancery of Bavaria records France's refusal in cool terms.
   ► end turn
   Your unratified settlement draft with Austria (1 clause) was set aside at turn's end.
   ═══════════════════════════════════════
   TURN 5 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Admiralty: -90g | Blockade: -368g | Other: +1475g | Upkeep: -1948g | Net: +1659g | Spent: 1368g
   Treasury: 2,150g
   Actions refreshed: 4/4
   Supply shortage at Franconia: Ney loses 684 troops
   Supply shortage at Franconia: Davout loses 763 troops
   Supply shortage at Franconia: Lannes loses 504 troops
   Supply shortage at Franconia: Bernadotte loses 505 troops
   Supply shortage at Franconia: Napoleon loses 294 troops
   Supply shortage at Tyrol: Archduke Charles loses 110 troops
   Supply shortage at Tyrol: Archduke John loses 196 troops
   Holland loyalty 98 (+2): a common enemy, the lord's victories
   Kingdom of Italy loyalty 100 (+2): the garrison's presence, the lord's victories
   Teulie's contingent comes home — 5,334 of 7,500 men.
   Britain subsidizes Russia with 200 gold.
   Berthier reports that Murat resents Ney's laurels again, 2 turns after the last — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Soult appears envious of Murat's laurels — he has thrown himself into his post with obsessive diligence.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1507,597)  France(943,537)  Bavaria(1309,507)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  32(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Ney +4(1348,427)  ?(1367,302)  Brunswick(1368,263)  Murat(1236,466)  Deroy(1265,438)  Soult(1213,387)  ?(1367,613)  Archduke Charles(1345,559)  Archduke John(1364,585)  ?(890,393)  Castanos(891,354)  Dumonceau(1129,301)  Massena(1310,612)  ?(1495,430)  ?(1367,363)  ?(1272,642)  10k(1290,360)  25k(942,504)  12k(890,454)  ?(1145,600)  10k(1129,412)  12k(1080,412)  10k(1310,677)
```

```
#0134  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0134_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 816 px]: unchanged
── BottomLeftUI (layer 0) [scrolled 1894 of 1894 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,150
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Berthier reports that Murat resents Ney's laurels again, 2 turns after the last — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Soult appears envious of Murat's laurels — he has thrown himself into his post with obsessive diligence.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   --- Strategic Order Updates ---
   Napoleon: Napoleon answered the guns this turn and stands at Franconia; his march resumes next turn.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 5
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — St Petersburg now pays London 300 gold a turn against us — her war with us is paid for.
   • Sire — our peace binds Austria for 4 more turns; then she may join a league (relations −79).
   SITUATION
   France holds 28 regions. Treasury: 2,150g (+1,659 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — Hunted by Archduke Charles on consecutive turns — holds Milan with 26,239 men.
   - Davout — Franconia — 17,603 — Awaiting orders.
   - Ney — Franconia — 15,795 — Awaiting orders.
   - Murat — Swabia — 15,416 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — Awaiting orders.
   > Napoleon — Franconia — 6,799 — Moving to Rhineland.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Swabia — 16,469 [confirmed]
   Brunswick — Berlin — large force [partial]
   Archduke Charles — Tyrol — small force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 2,750 men, at Franconia.
   2 satellites steadied — Holland and Kingdom of Italy.
   Berthier reports that Murat resents Ney's laurels again, 2 turns after the last — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Soult appears envious of Murat's laurels — he has thrown himself into his post with obsessive diligence.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 69).
   Settlement of France vs Austria: Gold indemnity: 400 gold from France to Austria.
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 22.
   Teulie's contingent comes home — 5,334 of 7,500 men.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Prussia — Non Aggression
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0135  click Envoys (1)  ->  ok
  (clicked at (3379, 18))
view: <run>\frames\0135_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused) (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Non-Aggression Pact / Terms: /   - Proposal: Non-Aggression Pact /   - Offer: Gold payment - 137 /  / Hardenberg, stiffly: "Prussia's interest is the Rhine at peace and the army at home; Berlin signs where those two meet. Sign the pact of non-aggression." /  / An interesting proposal. I shall study the terms closely. /  / This offer wi …
   controls: [Accept]  [Counter]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 816 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1894 of 1894 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,150
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0136  click Accept  ->  ok
  (clicked at (1604, 687))
view: <run>\frames\0136_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 97 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(2032,64)]  [icon: Settlement Ratified @(2074,64)]  [icon: Marshal Murat seeks an audience @(2116,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: The Moniteur is out @(2434,64)]  [icon: Treaty with Prussia @(2476,64)]  [+9]
── DiplomaticLedger (layer 50) [scrolled 0 of 816 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   ═══ ACTIVE TREATIES ═══ /  / Sweden ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (3 turns ago) /  / Naples ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (3 turns ago) /  / Prussia ↔ France: Non Aggression /   Clauses: Gold payment: 137 (Prussia -> France) /   Duration: permanent   C …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES](disabled: You are reading this book)  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <v Settlement of France vs Austria: Gold indemnity: 400 gold from France to Austria.>
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -2
   T:4
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [scrolled 1960 of 1960 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
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
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
map: unchanged (51 labels)
```

```
#0137  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0137_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   At War (2)
   Treaties (9)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Prussia  —  Non-Aggression  |  +22 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +36 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 816 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
map: unchanged (51 labels)
```

```
#0138  click Russia  —  At War  ->  ok
  (clicked at (1825, 561))
view: <run>\frames\0138_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 200 px, 0 of 182 px] ──
   DIPLOMACY — Russia
   DP: 5
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: At War   Relation: -80 (Hostile) /  / "The war with Russia grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus. /  / KEY FACTORS /   + Base willingness (+20) /   + Exhaustion from prolonged …
   Mission already active
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Unlikely]  [Open Settlement]  [Propose White Peace]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5](disabled: Mission already active)  [Undermine Alliances (2 DP)  —  -4 relation between targets/turn](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 816 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
map: unchanged (51 labels)
```

```
#0139  click Open Settlement  ->  ok
  (clicked at (1825, 503))
view: <run>\frames\0139_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 24 px, 0 of 24 px, 0 of 288 px] ──
   This settlement cannot be ratified now. / France vs Britain + Russia - Whole-war settlement / Covered enemies: Britain, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Britain 8/50, Russia 8/50. / Treasury 2,287 gold: committed 0 / reserve 500 / remaining 1,787 / Sire, this settlement of France vs Britain + Russia seats 2 courts at the table. Britain will not sign; the …
   The table /   * Britain ▸ - Holding out (8/50) White peace /       Blocker: Settlement legitimacy /       Castlereagh declines for Britain: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents, and arithmetic does not sign papers it cannot balance. He adds that London has read the bulletins from Franconia — Marshal Ney's laurels do not …
   Britain:
   Russia:
   Sire, a white peace for France vs Britain + Russia cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. Author terms or hold until the field shifts. London and Vilna are unbeaten — a whole-war peace needs their consent (Britain 8/50, Russia 8/50). /  / Allies and Standing /   * Britain - Seat at settleme …
   controls: <Britain ▸>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Press Britain]  [Ease Britain]  [Drop Britain]  [Press Russia]  [Ease Russia]  [Drop Russia]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 97 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 816 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose common peace with Russia
map: unchanged (51 labels)
```

```
#0140  click Drop Britain  ->  ok
  (clicked at (1782, 591))
view: <run>\frames\0140_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px, 0 of 288 px] ──
   This settlement cannot be ratified now. / France vs Russia - Separate settlement / Covered enemies: Russia / Still at war: Britain / Will NOT carry as drafted — every court must reach 50. Holding out: Russia 9/50. / Treasury 2,287 gold: committed 0 / reserve 500 / remaining 1,787 / Sire, this settlement of France vs Russia seats 1 courts at the table. Russia will not sign; the settlement of France …
   The table /   * Russia ▸ - Holding out (9/50) White peace /       Blocker: Settlement legitimacy /       Czartoryski holds Russia back from the table — it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. The court marks that Marshal Ney stands crowned in glory at Franconia. /       + Add demand / Russia is the holdout. / ▸ Russia won …
   Russia:
   Coverage:
   Sire, a white peace for France vs Russia cannot be sealed as it stands: it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents. Author terms or hold until the field shifts. Vilna is unbeaten — a whole-war peace needs its consent (Russia 9/50). /  / Allies and Standing /   * Britain - Seat at settlement (Defenders, war leader) /   * Franc …
   controls: <Russia ▸>  <+ Add demand>  [Press Russia]  [Ease Russia]  [Bring Britain to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 816 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2027 of 2027 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement cover drop
map: unchanged (51 labels)
```

```
#0141  click Ease Russia  ->  ok
  (clicked at (1624, 597))
view: <run>\frames\0141_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px, 0 of 288 px] ──
   This settlement cannot be ratified now. / France vs Russia - Separate settlement / Covered enemies: Russia / Still at war: Britain / Will NOT carry as drafted — every court must reach 50. Holding out: Russia 3/50. / Treasury 2,287 gold: committed 100 / reserve 500 / remaining 1,687 / Sire, this settlement of France vs Russia seats 1 courts at the table. Russia will not sign; the settlement of Fran …
   The table /   * Russia ▸ - Holding out (3/50) Conceded: 100g /       Blocker: Settlement legitimacy /       Czartoryski holds Russia back from the table — the terms claim a victory the field has not delivered. The court marks that Marshal Ney stands crowned in glory at Franconia. /       Conceded · France pays 100 gold  [-][+]  Remove /       + Add demand / Russia is the holdout. / ▸ Russia won't  …
   Russia:
   Coverage:
   Sire, the settlement of France vs Russia cannot be ratified now: the terms claim a victory the field has not delivered. Revise terms or stand down before pressing further. Vilna is unbeaten — a whole-war peace needs its consent (Russia 3/50). /  / Allies and Standing /   * Britain - Seat at settlement (Defenders, war leader) /   * France - Seat at settlement (Attackers, war leader) /   * Holland - …
   controls: <Russia ▸>  <Remove>  <+ Add demand>  [Press Russia]  [Ease Russia]  [Bring Britain to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 816 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2049 of 2049 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (51 labels)
```

```
#0142  click Ease Russia  ->  ok
  (clicked at (1624, 597))
view: <run>\frames\0142_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 46 px, 0 of 288 px] ──
   This settlement cannot be ratified now. / France vs Russia - Separate settlement / Covered enemies: Russia / Still at war: Britain / Will NOT carry as drafted — every court must reach 50. Holding out: Russia 7/50. / Treasury 2,287 gold: committed 200 / reserve 500 / remaining 1,587 / Sire, this settlement of France vs Russia seats 1 courts at the table. Russia will not sign; the settlement of Fran …
   The table /   * Russia ▸ - Holding out (7/50) Conceded: 200g /       Blocker: Settlement legitimacy /       Czartoryski holds Russia back from the table — the terms claim a victory the field has not delivered. The court marks that Marshal Ney stands crowned in glory at Franconia. /       Conceded · France pays 200 gold  [-][+]  Remove /       + Add demand / Russia is the holdout. / ▸ Russia won't  …
   Russia:
   Coverage:
   Sire, the settlement of France vs Russia cannot be ratified now: the terms claim a victory the field has not delivered. Revise terms or stand down before pressing further. Vilna is unbeaten — a whole-war peace needs its consent (Russia 7/50). /  / Allies and Standing /   * Britain - Seat at settlement (Defenders, war leader) /   * France - Seat at settlement (Attackers, war leader) /   * Holland - …
   controls: <Russia ▸>  <Remove>  <+ Add demand>  [Press Russia]  [Ease Russia]  [Bring Britain to the table]  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 816 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2071 of 2071 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: settlement dial generous
map: unchanged (51 labels)
```

```
#0143  click Back Out  ->  ok
  (clicked at (1455, 937))
view: <run>\frames\0143_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 97 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(2032,64)]  [icon: Settlement Ratified @(2074,64)]  [icon: Marshal Murat seeks an audience @(2116,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: The Moniteur is out @(2434,64)]  [icon: Treaty with Prussia @(2476,64)]  [+9]
── DiplomaticLedger (layer 50) [scrolled 0 of 816 px]: unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -2
   T:4
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [scrolled 2137 of 2137 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
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
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
map: unchanged (51 labels)
```

```
#0144  type where are the Russian armies?  ->  ok
  (typed and Enter)
view: <run>\frames\0144_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Sire — Russia: no word of Buxhowden; no word of Kutuzov.
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 816 px]: unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2226 of 2226 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► where are the Russian armies?
   Sire — Russia: no word of Buxhowden; no word of Kutuzov.
map: unchanged (51 labels)
```

```
#0145  click VASSALS  ->  ok
  (clicked at (3039, 113))
view: <run>\frames\0145_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 46 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   ═══ CLIENT STATES ═══ /  / 3 client states remit +838g/turn in tribute. /  /   Holland  Satellite  (client state of the Empire) /      Loyalty 98/100  ≈ steady /   Tribute: +337g/turn (75% of their income)   Answers the call to arms /   Standing: nothing to ask for /   Bond: no bond yet — each petition honoured is worth +1/turn /   No garrison — a corps in Amsterdam would add a standing +2/turn /  …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS](disabled: You are reading this book)  [CONGRESS]  <Invest>  <Loosen Rein>  <Tighten Rein>  <Release>  <Loosen Rein>  <Tighten Rein>  <Release>  <Invest>  <Loosen Rein>  <Tighten Rein>  <Release>
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2226 of 2226 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
   ► where are the Russian armies?
   Sire — Russia: no word of Buxhowden; no word of Kutuzov.
map: unchanged (51 labels)
```

```
#0146  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0146_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   At War (2)
   Treaties (9)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Prussia  —  Non-Aggression  |  +22 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +36 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2226 of 2226 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
   ► where are the Russian armies?
   Sire — Russia: no word of Buxhowden; no word of Kutuzov.
map: unchanged (51 labels)
```

```
#0147  scroll 1825 600 down 3  ->  ok
  (scrolled down 3 at (1825, 600))
view: <run>\frames\0147_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 142 of 627 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Prussia  —  Non-Aggression  |  +22 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +36 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -16 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Bavaria  —  Alliance  |  +53 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2226 of 2226 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
   ► where are the Russian armies?
   Sire — Russia: no word of Buxhowden; no word of Kutuzov.
map: unchanged (51 labels)
```

```
#0148  click Bavaria  —  Alliance  ->  ok
  (clicked at (1825, 682))
view: <run>\frames\0148_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 0 of 416 px] ──
   DIPLOMACY — Bavaria
   DP: 5
   TALLEYRAND'S ASSESSMENT — BAVARIA / Status: Alliance   Relation: +53 (Friendly) /  / "Our alliance with Bavaria stands firm. There is little to gain from change, and much to lose." / Recommendation: Talleyrand recommends: Propose Vassal /  / KEY FACTORS /   + Current relations (+26) /   + Base willingness (+10) /   + Diplomatic skill advantage (+6)
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Vassal (3 DP)  —  Uncertain — a counter is likely]  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Downgrade (1 DP)]  [Reassure Ally (1 DP)  —  +4 relation/turn](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2226 of 2226 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
   ► where are the Russian armies?
   Sire — Russia: no word of Buxhowden; no word of Kutuzov.
map: unchanged (51 labels)
```

```
#0149  click Propose Vassal (3 DP)  ->  ok
  (clicked at (1825, 459))
view: <run>\frames\0149_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Bavaria /  / France demands: /   • Bavaria pays 138 gold per turn to France /  / Harshness: Low / Acceptance estimate: ~41% (COUNTER expected) / Key obstacle: insufficient concessions / DP cost: 3 /  / "Sire, regarding the Vassalage proposal to Bavaria, I have prepared terms that reflect the current diplomatic climate."
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 97 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   ═══ CLIENT STATES ═══ /  / 3 client states remit +838g/turn in tribute. / Envoys await your reply — vassal instruments are suspended until the matter is answered. /  /   Holland  Satellite  (client state of the Empire) /      Loyalty 98/100  ≈ steady /   Tribute: +337g/turn (75% of their income)   Answers the call to arms /   Standing: nothing to ask for /   Bond: no bond yet — each petition honou …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS](disabled: You are reading this book)  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2271 of 2271 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose vassalization to Bavaria
map: unchanged (51 labels)
```

```
#0150  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0150_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Bavaria /  / France concedes: /   • France pays 228 gold to Bavaria /  / Harshness: Low / Acceptance estimate: ~50% (ACCEPT) / DP cost: 3 /  / "A magnanimous approach, Sire. More generous terms for Bavaria."
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2292 of 2292 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (51 labels)
```

```
#0151  click Even more generous  ->  ok
  (clicked at (1829, 727))
view: <run>\frames\0151_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Bavaria /  / France concedes: /   • France pays 342 gold to Bavaria /   • France cedes 1 AP per turn to Bavaria /  / Harshness: Low / Acceptance estimate: ~69% (ACCEPT) / DP cost: 3 /  / "A magnanimous approach, Sire. More generous terms for Bavaria. We are offering everything short of the crown itself. Any more and we negotiate from our knees."
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2314 of 2314 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (51 labels)
```

```
#0152  click Not Now  ->  ok
  (clicked at (1834, 727))
view: <run>\frames\0152_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 97 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(2032,64)]  [icon: Settlement Ratified @(2074,64)]  [icon: Marshal Murat seeks an audience @(2116,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: The Moniteur is out @(2434,64)]  [icon: Treaty with Prussia @(2476,64)]  [+9]
── DiplomaticLedger (layer 50) [scrolled 0 of 46 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   ═══ CLIENT STATES ═══ /  / 3 client states remit +838g/turn in tribute. /  /   Holland  Satellite  (client state of the Empire) /      Loyalty 98/100  ≈ steady /   Tribute: +337g/turn (75% of their income)   Answers the call to arms /   Standing: nothing to ask for /   Bond: no bond yet — each petition honoured is worth +1/turn /   No garrison — a corps in Amsterdam would add a standing +2/turn /  …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS](disabled: You are reading this book)  [CONGRESS]  <Invest>  <Loosen Rein>  <Tighten Rein>  <Release>  <Loosen Rein>  <Tighten Rein>  <Release>  <Invest>  <Loosen Rein>  <Tighten Rein>  <Release>
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -2
   T:4
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [scrolled 2381 of 2381 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
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
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (51 labels)
```

```
#0153  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0153_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   At War (2)
   Treaties (9)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 35 titled provinces — 45 are needed (10 more to win and)  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Prussia  —  Non-Aggression  |  +22 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +36 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2381 of 2381 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: modify generous
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (51 labels)
```

```
#0154  scroll 1825 600 down 3  ->  ok
  (scrolled down 3 at (1825, 600))
view: <run>\frames\0154_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 142 of 627 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Treaties (9)
   controls: [icon: Close (Esc) @(2075,284)]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Prussia  —  Non-Aggression  |  +22 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +36 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -16 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Denmark  —  Non-Aggression  |  +10 (Neutral)]  [Bavaria  —  Alliance  |  +53 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2381 of 2381 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: modify generous
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (51 labels)
```

```
#0155  click Bavaria  —  Alliance  ->  ok
  (clicked at (1825, 682))
view: <run>\frames\0155_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 0 of 416 px] ──
   DIPLOMACY — Bavaria
   DP: 5
   TALLEYRAND'S ASSESSMENT — BAVARIA / Status: Alliance   Relation: +53 (Friendly) /  / "Our alliance with Bavaria stands firm. There is little to gain from change, and much to lose." / Recommendation: Talleyrand recommends: Propose Vassal /  / KEY FACTORS /   + Current relations (+26) /   + Base willingness (+10) /   + Diplomatic skill advantage (+6)
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Vassal (3 DP)  —  Uncertain — a counter is likely]  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Downgrade (1 DP)]  [Reassure Ally (1 DP)  —  +4 relation/turn](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2381 of 2381 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Directing Talleyrand: modify generous
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
map: unchanged (51 labels)
```

```
#0156  click Propose Vassal (3 DP)  ->  ok
  (clicked at (1825, 459))
view: <run>\frames\0156_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Bavaria /  / France demands: /   • Bavaria pays 103 gold per turn to France /  / Harshness: Low / Acceptance estimate: ~42% (COUNTER expected) / Key obstacle: insufficient concessions / DP cost: 3 /  / "Sire, regarding the Vassalage proposal to Bavaria, I have prepared terms that reflect the current diplomatic climate."
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 97 / 100
   Turn 5 — Late November 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   ═══ CLIENT STATES ═══ /  / 3 client states remit +838g/turn in tribute. / Envoys await your reply — vassal instruments are suspended until the matter is answered. /  /   Holland  Satellite  (client state of the Empire) /      Loyalty 98/100  ≈ steady /   Tribute: +337g/turn (75% of their income)   Answers the call to arms /   Standing: nothing to ask for /   Bond: no bond yet — each petition honou …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS](disabled: You are reading this book)  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1764 of 1764 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Ney — Franconia — 15,795 — Awaiting orders.
   - Murat — Swabia — 15,416 — Awaiting orders.
   ⚠ Starving — supply has failed at Swabia two turns running.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — Awaiting orders.
   > Napoleon — Franconia — 6,799 — Moving to Rhineland.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Swabia — 16,469 [confirmed]
   Brunswick — Berlin — large force [partial]
   Archduke Charles — Tyrol — small force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 2,750 men, at Franconia.
   2 satellites steadied — Holland and Kingdom of Italy.
   Berthier reports that Murat resents Ney's laurels again, 2 turns after the last — he has grown restless for glory.
   Murat seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Soult appears envious of Murat's laurels — he has thrown himself into his post with obsessive diligence.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Sire — Hesse and France have signed the Non-Aggression Pact.
   Sire — the Papal States and France have signed the Open Borders Agreement.
   War exhaustion grows — Austria nears breaking point (exhaustion: 69).
   Settlement of France vs Austria: Gold indemnity: 400 gold from France to Austria.
   THE LAWS: Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 22.
   Teulie's contingent comes home — 5,334 of 7,500 men.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Prussia — Non Aggression
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 35 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-1)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Open Borders → Non-Aggression with Prussia.
   ► propose common peace with Russia
   Directing Talleyrand: settlement cover drop
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: settlement dial generous
   Directing Talleyrand: suspend settlement editor
   Settlement draft kept. Reopen Settlement to continue editing.
   ► where are the Russian armies?
   Sire — Russia: no word of Buxhowden; no word of Kutuzov.
   ► propose vassalization to Bavaria
   Directing Talleyrand: modify generous
   Directing Talleyrand: modify generous
   Directing Talleyrand: reconsider
   Of course, Sire. Take your time.
   ► propose vassalization to Bavaria
map: unchanged (51 labels)
```

```
#0157  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0157_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Bavaria /  / France concedes: /   • France pays 228 gold to Bavaria /  / Harshness: Low / Acceptance estimate: ~50% (ACCEPT) / DP cost: 3 /  / "A magnanimous approach, Sire. More generous terms for Bavaria."
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── DiplomaticLedger (layer 50) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1786 of 1786 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (51 labels)
```

```
#0158  click Send these terms  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0158_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 2/7
   Threat 97 / 100
   Turn 5 — Late November 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(2146,64)]  [icon: Settlement Ratified @(2188,64)]  [icon: Marshal Murat seeks an audience @(2230,64)]  [icon: The Moniteur is out @(2272,64)]  [icon: Treaty with Prussia @(2314,64)]  [icon: Diplomatic Action Accepted @(2356,64)]  [+10]
── DiplomaticLedger (layer 50) [scrolled 0 of 46 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia (paused)
   DP: 2/7
   ═══ CLIENT STATES ═══ /  / 3 client states remit +838g/turn in tribute. /  /   Holland  Satellite  (client state of the Empire) /      Loyalty 98/100  ≈ steady /   Tribute: +337g/turn (75% of their income)   Answers the call to arms /   Standing: nothing to ask for /   Bond: no bond yet — each petition honoured is worth +1/turn /   No garrison — a corps in Amsterdam would add a standing +2/turn /  …
   controls: [Unpin]  [icon @(3613,76)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS](disabled: You are reading this book)  [CONGRESS]  <Invest>  <Loosen Rein>  <Tighten Rein>  <Release>  <Loosen Rein>  <Tighten Rein>  <Release>  <Invest>  <Loosen Rein>  <Tighten Rein>  <Release>
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -2
   T:4
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [scrolled 1874 of 1874 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
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
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Bavaria court with your Vassalage proposal. Expect a response by next turn. (3 DP spent)
map: unchanged (51 labels)
```

```
#0159  type Murat, move to Franche-Comte  ->  ok
  (typed and Enter)
view: <run>\frames\0159_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat moves from Swabia to Franche-Comte
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1985 of 1985 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Murat, move to Franche-Comte
   → Murat moves from Swabia to Franche-Comte
   [3/4 actions remaining]
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1507,597)  France(943,537)  Bavaria(1309,507)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  32(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Ney +4(1348,427)  ?(1367,302)  Brunswick(1368,263)  Deroy(1251,466)  Soult(1213,387)  ?(1367,613)  Archduke Charles(1345,559)  Archduke John(1364,585)  Murat(1196,504)  ?(890,393)  Castanos(891,354)  Dumonceau(1129,301)  Massena(1310,612)  ?(1495,430)  ?(1367,363)  ?(1272,642)  10k(1290,428)  25k(942,504)  12k(890,454)  ?(1145,600)  10k(1129,412)  12k(1080,412)  10k(1310,677)
```

```
#0160  type Davout, move to Swabia  ->  ok
  (typed and Enter)
view: <run>\frames\0160_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout moves from Franconia to Swabia (176 lost to march)
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2095 of 2095 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Davout, move to Swabia
   → Davout moves from Franconia to Swabia (176 lost to march)
   [2/4 actions remaining]
map names: Russia(1966,195)  Ottoman Empire(1748,788)  Prussia(1535,286)  Sweden(1292,32)  Saxony(1495,396)  Austria(1507,597)  France(943,537)  Bavaria(1309,507)  Kingdom of Italy(1152,677)  Denmark(1124,73)  Papal States(1262,778)  Britain(784,292)  Hanover(1112,333)  Naples(1189,904)  Sardinia(1028,800)  Hesse(1291,394)  Holland(1125,378)  Switzerland(1145,566)
map pieces: 100(710,385)  45(684,616)  32(733,785)  20(1382,111)  18(1352,61)  15(1689,666)  12(940,267)  10(377,803)  10(1330,203)  5(1186,839)  Ney +3(1348,439)  ?(1367,302)  Brunswick(1368,263)  Davout(1236,466)  Deroy(1265,438)  Soult(1213,387)  ?(1367,613)  Archduke Charles(1345,559)  Archduke John(1364,585)  Murat(1196,504)  ?(890,393)  Castanos(891,354)  Dumonceau(1129,301)  Massena(1310,612)  ?(1495,430)  ?(1367,363)  ?(1272,642)  10k(1290,360)  25k(942,504)  12k(890,454)  ?(1145,600)  10k(1129,412)  12k(1080,412)  10k(1310,677)
```

```
#0161  type how can I shut Britain's ports?  ->  ok
  (typed and Enter)
view: <run>\frames\0161_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=diplomatic_ledger, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok ═══════════════════════════════════════
           COMMAND REFERENCE
═══════════════════════════════════════

MILITARY COMMANDS:
  attack     - Engage enemy forces or capture region
               "Ney, attack Mack" / "attack" (nearest)

  defend     - Take defensive position (+30% bonus)
               "Davout, defend" / "hold" (alias)

  move       - Move to adjacent region
               "Lannes, move to Munich"

  retreat    - Fall back toward friendly territory (FREE)
               "Ney, retreat" - Aggressive marshals may object!

  recruit    - Raise troops (1 Admin AP + gold)
               "recruit for Davout" - his corps, where he stands
               "recruit at Paris" / "recruit" - at the depot, or the
               nearest corps: a marshal must stand within reach of it
               Infantry 10k / Cavalry 5k / Artillery 3k, from the
               manpower pools. PRICING: base 200-400g, capital -25%,
               x3 AT WAR, dearer above the FORCE LIMIT, and the
               marshal's administration prices the levy (Davout -15%,
               Murat +15% - his card explains, press G).
  substitutes - "buy substitutes for Ney" (1 Admin AP + gold)
               "purchase a levy for Ney" / "hire replacements for Ney"
               The remplacant: under the
               conscription law a called-up man could pay another
               to serve in his place. Draws NO men from the pools -
               gold alone - so it is the one purchase your TREASURY
   
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 46 px]: unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 8809 of 8809 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapArea (layer 0): unchanged
── MapControls (layer 0): unchanged
── command window, new lines ──
   returns. Watch it in the Strategic Ledger's Orders tab
   (T) or on its notice; recall him from either, free.
   THE COMPACTS - three instruments that shipped and were never
   named here, so no player could learn they exist:
   buy off    - "buy off Prussia" - a court aims a grievance at us;
   gold buys its SLEEP for a term. The price is stated
   before you offer (D4 - diplomacy has no fog), and it
   is read off how badly they want the thing.
   sponsor    - "sponsor Prussia against Hanover, 200 gold" - arm
   somebody else's grievance, per turn, for a term.
   "license Prussia against Hanover" at no gold sells
   permission instead: the same bond, a cheaper coin.
   Talleyrand refuses to aim a design at ourselves.
   guarantee  - "guarantee Saxony" - pledge to defend a border.
   Coveters read the pledge and want it less; abandon
   it and the grievance is ours to answer for.
   NOTE: a standing compact runs its TERM. There is no cancelling
   it - war on the court, or a pledge that contradicts it,
   is a RENEGE, and Europe remembers who broke a word.
   Press D for the Diplomatic Ledger - all twenty nations of Europe,
   treaties, wars, and the Balance of Europe.
   THE CONGRESS OF PARIS (how the reign is WON - the table of the
   great powers is the Diplomatic Ledger's Congress tab, press D then 7):
   summon     - "summon the congress" (1 Admin AP + 2 DP), or the
   Congress of Paris row atop the Cabinet (F1). It needs
   50 TITLED provinces - homeland, ceded by treaty, a
   client's soil, or held 12 quiet turns - with Paris
   held, the Emperor free and no satellite on the brink.
   It cannot be undone. For 8 turns every great power
   answers - RECOGNIZES, REFUSES, SUES, SHUT OUT or GONE -
   with its reason and its PRICE. Keep the 50, Paris and
   the Emperor's freedom, and declare no war: on the
   eighth turn, with every great power won over, shut out
   or gone, the Imperial Peace is signed. Otherwise the
   Congress dissolves, and may be summoned again after
   10 turns.
   sweetener  - "offer Prussia 1000 gold for recognition" - offer
   <court> <gold> gold for recognition, at the table
   while the Congress sits (1 DP): +10 for every 1,000
   gold, at most +20 a court. Gold past that is not taken.
   Ask before you act - "can we summon the congress?" names every
   term still unmet, and nothing is spent.
   SCREENS & HOTKEYS:
   F1 diplomacy wizard | T strategic ledger | G marshals
   D diplomatic ledger | L campaign log | R morning dispatch
   E end turn | Tab terminal
   YOUR MARSHALS (press G - each card shows skills, trust, ability):
   Ney "Bravest of the Brave" - devastating assaults
   Davout "Iron Resolve" - fortified patience becomes a hammer-blow
   Soult "Drillmaster of Boulogne" - sharpens his corps in a day
   Lannes "Roland of the Army" - marches to the sound of the guns
   Murat "First Horseman of Europe" - turns routs into annihilation
   Bernadotte "Eyes on a Crown" - may not march for you at all
   Massena "Child of Victory" - hardest to kill when outnumbered
   Enemy generals carry famed abilities too - intel will name them.
   GLORY AND GRIEVANCE (the ladder on the Generals screen):
   Victories earn GLORY, counted over the last 8 turns. A marshal who
   falls behind a peer starts to ENVY him - and once he does, that man
   stays his rival for as long as he is above.
   ESTATES AND RENTES CANNOT TOUCH THIS. Gold answers a marshal's
   LOYALTY; only glory answers his envy. Rewarding a jealous marshal
   is not wrong - it is simply a different quarrel.
   A grievance costs you a corps: he will not coordinate with the man
   he resents, and at the worst he will not march beside him at all.
   Watch the muster preview - it names the quarrel when it bites.
   What ENDS it is the field. An aggressive marshal needs a win against
   a real foe; a cautious one a victory won shoulder to shoulder; a
   literal one only meaningful contact with the enemy. A hard defeat
   costs glory - unless he was outnumbered, which carries no shame -
   and out-bleeding the enemy 2-to-1 earns glory even when the field is
   left undecided.
   While he is aggrieved he attacks at +15% with no marshal of yours
   counted on the field beside him. Send him alone and he fights like
   a man with something to prove.
   FREE ACTIONS: help, end turn, wait, retreat, economy
   RETREAT RECOVERY (2-4 turns - command skill drives The Rally):
   After retreating, marshals are demoralized.
   BLOCKED: attack, fortify, drill, scout
   ALLOWED: move, recruit, defend, wait, change stance
   ═══════════════════════════════════════
map: unchanged (52 labels)
```

```
#0162  click ⚓ 45 sail · BLOCKADED  ->  ok
  (clicked at (2887, 18))
view: <run>\frames\0162_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 0 of 574 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late November 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 45 sail of the line — readiness 50  (Adm. Villeneuve) /   Posture: guard — home waters covered /   Yards: Bordelais, Brittany, Normandy, Provence  (0/1 keels this turn) /  / Orders to the Admiralty /     Bloc …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Bernadotte, march to Provence>  <Lannes, march to Provence>
── BottomLeftUI (layer 0) [under a modal] [scrolled 8678 of 8678 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   5
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   2,287
   Inf:
   88,411
   Cav:
   22,000
   Art:
   12,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   After retreating, marshals are demoralized.
   BLOCKED: attack, fortify, drill, scout
   ALLOWED: move, recruit, defend, wait, change stance
   ═══════════════════════════════════════
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2149,286)  Spain(1185,881)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Britain(1397,292)  Hanover(1726,333)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  32(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney +3(1961,439)  ?(1980,302)  Brunswick(1981,263)  Davout(1850,466)  Deroy(1879,438)  Soult(1826,387)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  Murat(1810,504)  ?(1504,393)  Castanos(1504,354)  Dumonceau(1742,301)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1903,360)  25k(1556,504)  12k(1504,454)  ?(1759,600)  10k(1742,412)  12k(1694,412)  10k(1923,677)
```

```
#0163  scroll 1825 600 down 10  ->  ok
  (scrolled down 10 at (1825, 600))
view: <run>\frames\0163_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: '' (focused)
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 551 of 575 px] ──
   STRATEGIC LEDGER
   ═══ THE ADMIRALTY ═══ / Late November 1805 / The fleet, the blockades, the crossings — and every order the sea will take. Keys 1–8 turn the ledger's books (Alt+1–8 while you type). /   Fleet: 45 sail of the line — readiness 50  (Adm. Villeneuve) /   Posture: guard — home waters covered /   Yards: Bordelais, Brittany, Normandy, Provence  (0/1 keels this turn) /  / Orders to the Admiralty /     Bloc …
   controls: [Pin]  [icon @(2193,246)]  [FORCES]  [TERRITORIES]  [ECONOMY]  [INTELLIGENCE]  [MANPOWER]  [ORDERS]  [ADMIRALTY](disabled: You are reading this book)  [LAWS]  <Blockade the enemy>  <The Grand Diversion>  <Lay down ships (400g at Bordelais)>  <Bernadotte, march to Provence>  <Lannes, march to Provence>
── BottomLeftUI (layer 0) [under a modal] [scrolled 8678 of 8678 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   After retreating, marshals are demoralized.
   BLOCKED: attack, fortify, drill, scout
   ALLOWED: move, recruit, defend, wait, change stance
   ═══════════════════════════════════════
map: unchanged (54 labels)
```

```
#0164  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0164_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=['ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── StrategicLedger (layer 50) [scrolled 551 of 575 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 8678 of 8678 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   After retreating, marshals are demoralized.
   BLOCKED: attack, fortify, drill, scout
   ALLOWED: move, recruit, defend, wait, change stance
   ═══════════════════════════════════════
map: unchanged (54 labels)
```

```
#0165  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0165_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 5 — Late November 1805   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -2
   T:4
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [scrolled 8678 of 8678 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   After retreating, marshals are demoralized.
   BLOCKED: attack, fortify, drill, scout
   ALLOWED: move, recruit, defend, wait, change stance
   ═══════════════════════════════════════
map: unchanged (54 labels)
```

```
#0166  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0166_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 5
   BAVARIA / ──────────────────────────── / - Deroy holds position /  / ──────────────────────────── / Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 97 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 8702 of 8704 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,789
   Inf:
   90,223
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   THE CONGRESS OF PARIS (how the reign is WON - the table of the
   great powers is the Diplomatic Ledger's Congress tab, press D then 7):
   summon     - "summon the congress" (1 Admin AP + 2 DP), or the
   Congress of Paris row atop the Cabinet (F1). It needs
   50 TITLED provinces - homeland, ceded by treaty, a
   client's soil, or held 12 quiet turns - with Paris
   held, the Emperor free and no satellite on the brink.
   It cannot be undone. For 8 turns every great power
   answers - RECOGNIZES, REFUSES, SUES, SHUT OUT or GONE -
   with its reason and its PRICE. Keep the 50, Paris and
   the Emperor's freedom, and declare no war: on the
   eighth turn, with every great power won over, shut out
   or gone, the Imperial Peace is signed. Otherwise the
   Congress dissolves, and may be summoned again after
   10 turns.
   sweetener  - "offer Prussia 1000 gold for recognition" - offer
   <court> <gold> gold for recognition, at the table
   while the Congress sits (1 DP): +10 for every 1,000
   gold, at most +20 a court. Gold past that is not taken.
   Ask before you act - "can we summon the congress?" names every
   term still unmet, and nothing is spent.
   SCREENS & HOTKEYS:
   F1 diplomacy wizard | T strategic ledger | G marshals
   D diplomatic ledger | L campaign log | R morning dispatch
   E end turn | Tab terminal
   YOUR MARSHALS (press G - each card shows skills, trust, ability):
   Ney "Bravest of the Brave" - devastating assaults
   Davout "Iron Resolve" - fortified patience becomes a hammer-blow
   Soult "Drillmaster of Boulogne" - sharpens his corps in a day
   Lannes "Roland of the Army" - marches to the sound of the guns
   Murat "First Horseman of Europe" - turns routs into annihilation
   Bernadotte "Eyes on a Crown" - may not march for you at all
   Massena "Child of Victory" - hardest to kill when outnumbered
   Enemy generals carry famed abilities too - intel will name them.
   GLORY AND GRIEVANCE (the ladder on the Generals screen):
   Victories earn GLORY, counted over the last 8 turns. A marshal who
   falls behind a peer starts to ENVY him - and once he does, that man
   stays his rival for as long as he is above.
   ESTATES AND RENTES CANNOT TOUCH THIS. Gold answers a marshal's
   LOYALTY; only glory answers his envy. Rewarding a jealous marshal
   is not wrong - it is simply a different quarrel.
   A grievance costs you a corps: he will not coordinate with the man
   he resents, and at the worst he will not march beside him at all.
   Watch the muster preview - it names the quarrel when it bites.
   What ENDS it is the field. An aggressive marshal needs a win against
   a real foe; a cautious one a victory won shoulder to shoulder; a
   literal one only meaningful contact with the enemy. A hard defeat
   costs glory - unless he was outnumbered, which carries no shame -
   and out-bleeding the enemy 2-to-1 earns glory even when the field is
   left undecided.
   While he is aggrieved he attacks at +15% with no marshal of yours
   counted on the field beside him. Send him alone and he fights like
   a man with something to prove.
   FREE ACTIONS: help, end turn, wait, retreat, economy
   RETREAT RECOVERY (2-4 turns - command skill drives The Rally):
   After retreating, marshals are demoralized.
   BLOCKED: attack, fortify, drill, scout
   ALLOWED: move, recruit, defend, wait, change stance
   ═══════════════════════════════════════
   ► end turn
   Your unratified settlement draft with Russia (2 clauses) was set aside at turn's end.
   ═══════════════════════════════════════
   TURN 6 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -3g | Admiralty: -90g | Blockade: -328g | Other: +1731g | Upkeep: -1398g | Net: +2502g
   Treasury: 4,789g
   Actions refreshed: 4/4
   Bavaria completes a market at Swabia.
   Crowded at Swabia: Davout loses 348 troops to the press of 3 corps on one province's roads
   Crowded at Swabia: Napoleon loses 134 troops to the press of 3 corps on one province's roads
   Crowded at Swabia: Deroy loses 329 troops to the press of 3 corps on one province's roads
   Supply shortage at Tyrol: Archduke Charles loses 217 troops
   Supply shortage at Tyrol: Archduke John loses 249 troops
   Switzerland loyalty 88 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Talleyrand returns from Bavaria with excellent news: they have accepted our proposal! The sticking point appears to be unresolved concerns. (Conditions changed slightly, but the terms held.)
   Treaty signed: Alliance → Vassal with Bavaria.
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Russia and Austria grows.
   Berthier reports that Bernadotte appears envious of Murat's laurels — he has grown cold and withholding.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2149,286)  Spain(1185,881)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Britain(1397,292)  Hanover(1726,333)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  33(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney(1947,451)  Lannes(1962,425)  Bernadotte(1989,398)  ?(1980,302)  Brunswick(1981,263)  Davout(1850,466)  Napoleon(1865,438)  Deroy(1879,362)  Soult(1826,389)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  Murat(1810,504)  ?(1504,393)  Castanos(1504,354)  Dumonceau(1742,301)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1933,360)  25k(1556,504)  12k(1504,454)  ?(1759,600)  10k(1742,412)  12k(1694,412)  10k(1923,677)
```

```
#0167  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0167_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1984 of 1984 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,789
   Inf:
   90,223
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ═══════════════════════════════════════
   TURN 6 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Charges of Empire: -3g | Admiralty: -90g | Blockade: -328g | Other: +1731g | Upkeep: -1398g | Net: +2502g
   Treasury: 4,789g
   Actions refreshed: 4/4
   Bavaria completes a market at Swabia.
   Crowded at Swabia: Davout loses 348 troops to the press of 3 corps on one province's roads
   Crowded at Swabia: Napoleon loses 134 troops to the press of 3 corps on one province's roads
   Crowded at Swabia: Deroy loses 329 troops to the press of 3 corps on one province's roads
   Supply shortage at Tyrol: Archduke Charles loses 217 troops
   Supply shortage at Tyrol: Archduke John loses 249 troops
   Switzerland loyalty 88 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Talleyrand returns from Bavaria with excellent news: they have accepted our proposal! The sticking point appears to be unresolved concerns. (Conditions changed slightly, but the terms held.)
   Treaty signed: Alliance → Vassal with Bavaria.
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Russia and Austria grows.
   Berthier reports that Bernadotte appears envious of Murat's laurels — he has grown cold and withholding.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   --- Strategic Order Updates ---
   Napoleon: Napoleon marches to Swabia. 1 region to Rhineland.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — St Petersburg now pays Vienna 200 gold a turn against us. Her peace with us binds her 3 more turns.
   SITUATION
   France holds 28 regions. Treasury: 4,789g (+2,730 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — Hunted by Archduke Charles on consecutive turns — holds Milan with 26,239 men.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — Awaiting orders.
   - Murat — Franche-Comte — 15,416 — Awaiting orders.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — Awaiting orders.
   > Napoleon — Swabia — 6,598 — Moving to Rhineland — arrives next turn.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 482 men, at Swabia.
   Switzerland loyalty 88 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier reports that Bernadotte appears envious of Murat's laurels — he has grown cold and withholding.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Non-Aggression Pact.
   Talleyrand has departed for the court of Bavaria.
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   Bavaria has been established under the protection of France.
   Sire — France and Bavaria have signed the Vassalage.
   Talleyrand returns from Bavaria with a response.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-2)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0168  click Envoys (1)  ->  ok
  (clicked at (3377, 18))
view: <run>\frames\0168_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Chancery of Helvetia (Dove) of Switzerland /  / The petition: /   - Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +10, its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1984 of 1984 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,789
   Inf:
   90,223
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0169  click Grant  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0169_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 97 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3216,64)]  [icon: Settlement Ratified @(3258,64)]  [icon: Marshal Murat seeks an audience @(3300,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Bavaria @(3618,64)]  [icon: The Marshalate awaits @(3649,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -2
   T:5
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [scrolled 2050 of 2050 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,789
   Inf:
   90,223
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (57 labels)
```

```
#0170  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0170_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 6
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   At War (2)
   Treaties (8)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Prussia  —  Non-Aggression  |  +22 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +35 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2050 of 2050 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (57 labels)
```

```
#0171  click Spain  —  Alliance  ->  ok
  (clicked at (1825, 664))
view: <run>\frames\0171_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 156 px, 0 of 416 px] ──
   DIPLOMACY — Spain
   DP: 6
   TALLEYRAND'S ASSESSMENT — SPAIN / Status: Alliance   Relation: +35 (Friendly) /  / "Our alliance with Spain holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus. /  / KEY FACTORS /   + Current relations (+18) /   + Base willingness (+10) /   + D …
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Vassal (3 DP)  —  Doubtful — may counter]  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Downgrade (1 DP)]  [Reassure Ally (1 DP)  —  +4 relation/turn](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2050 of 2050 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (57 labels)
```

```
#0172  click Propose Vassal (3 DP)  ->  ok
  (clicked at (1825, 459))
view: <run>\frames\0172_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Spain /  / France demands: /   • Spain pays 595 gold per turn to France /  / Harshness: High / Acceptance estimate: ~0% (REJECT) / Key obstacle: the harshness of current demands / DP cost: 3 /  / "Sire, I must counsel caution. Demanding too much from Spain may ensure they never forgive us."
   controls: [icon: Close (Esc) @(2151,292)]  [Send my terms as ordered]  [Use Talleyrand's suggestion]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 6/7
   Threat 97 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2095 of 2095 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,789
   Inf:
   90,223
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose vassalization to Spain
map: unchanged (57 labels)
```

```
#0173  click Use Talleyrand's suggestion  ->  ok
  (clicked at (1829, 727))
view: <run>\frames\0173_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['talleyrand_objection'], region_panel=no
── TalleyrandObjectionPopup (layer 113) [scrolled 0 of 39 px] ──
   TALLEYRAND OBJECTS / MODERATE /  / "Sire, I must counsel caution. Demanding too much from Spain may ensure they never forgive us." /  / Proposed terms: /   • Vassalage (Spain becomes a subject state) /   • Spain pays 595 gold/turn /  / Acceptance estimate: ~0% (Reject) / Defiance Risk: Medium / Regarding: Vassalage with Spain
   controls: [Proceed Anyway]  [Modify Proposal]  [Cancel]
── TopBar (layer 75) [under a modal] ──
   DP: 3/7
   Threat 97 / 100
   Turn 6 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2117 of 2117 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,789
   Inf:
   90,223
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: send suggested
map: unchanged (57 labels)
```

```
#0174  click Modify Proposal  ->  ok
  (clicked at (1844, 647))
view: <run>\frames\0174_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 3/7
   Threat 97 / 100
   Turn 6 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3351,64)]  [icon: Settlement Ratified @(3393,64)]  [icon: Marshal Murat seeks an audience @(3435,64)]  [icon: Treaty with Bavaria @(3477,64)]  [icon: The Marshalate awaits @(3519,64)]  [icon: Vassalage Accepted @(3561,64)]  [+14]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -2
   T:5
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [scrolled 2183 of 2183 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   4,789
   Inf:
   90,223
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Reviewing the proposal again...
   Very well, Sire. Reconsider the matter and issue your orders anew.
map: unchanged (57 labels)
```

```
#0175  click Talleyrand: Courting → Prussia  ->  ok
  (clicked at (3218, 18))
view: <run>\frames\0175_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 112 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia (paused)
   DP: 3/7
   TALLEYRAND — Divine Right / Authority: 100/100   Skill: 10   DP: 3/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Prussia /   Wary → Neutral (+32, 4 turns) /   Status: Paused, Cost: 2 DP/turn /   Effect: +8 relation per turn; our proposals to them +2 per turn courted (max +10, no …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2183 of 2183 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose vassalization to Spain
   Directing Talleyrand: send suggested
   Reviewing the proposal again...
   Very well, Sire. Reconsider the matter and issue your orders anew.
map: unchanged (57 labels)
```

```
#0176  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0176_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 112 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2183 of 2183 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose vassalization to Spain
   Directing Talleyrand: send suggested
   Reviewing the proposal again...
   Very well, Sire. Reconsider the matter and issue your orders anew.
map: unchanged (57 labels)
```

```
#0177  type Davout, drill your corps  ->  ok
  (typed and Enter; focus by grab_focus (the click did not focus the line))
view: <run>\frames\0177_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 8.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -2
   T:5
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [scrolled 1697 of 1697 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   4,789
   Inf:
   90,223
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   MORNING DISPATCH — Turn 6
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — St Petersburg now pays Vienna 200 gold a turn against us. Her peace with us binds her 3 more turns.
   SITUATION
   France holds 28 regions. Treasury: 4,789g (+2,730 by the accounts)
   The courts at war hold 21 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — Hunted by Archduke Charles on consecutive turns — holds Milan with 26,239 men.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — Awaiting orders.
   - Murat — Franche-Comte — 15,416 — Awaiting orders.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — Awaiting orders.
   > Napoleon — Swabia — 6,598 — Moving to Rhineland — arrives next turn.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 482 men, at Swabia.
   Switzerland loyalty 88 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier reports that Bernadotte appears envious of Murat's laurels — he has grown cold and withholding.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Non-Aggression Pact.
   Talleyrand has departed for the court of Bavaria.
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   Bavaria has been established under the protection of France.
   Sire — France and Bavaria have signed the Vassalage.
   Talleyrand returns from Bavaria with a response.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-2)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► propose vassalization to Spain
   Directing Talleyrand: send suggested
   Reviewing the proposal again...
   Very well, Sire. Reconsider the matter and issue your orders anew.
   ► Davout, drill your corps
   Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 8.
   [3/4 actions remaining]
map: unchanged (57 labels)
```

```
#0178  type Soult, drill  ->  ok
  (typed and Enter)
view: <run>\frames\0178_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 6 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Soult drills his corps with Boulogne-camp precision at Rhineland. Sharpen today, strike tomorrow — bonus ready turn 7, and he remains at your orders (though he cannot shift stance until the drill ends tonight).
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1829 of 1829 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   6
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   4,789
   Inf:
   90,223
   Cav:
   23,750
   Art:
   13,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, drill
   Soult drills his corps with Boulogne-camp precision at Rhineland. Sharpen today, strike tomorrow — bonus ready turn 7, and he remains at your orders (though he cannot shift stance until the drill ends tonight).
   [2/4 actions remaining]
map: unchanged (57 labels)
```

```
#0179  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0179_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 6
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 96 / 100
   Turn 7 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1766 of 1767 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,955
   Inf:
   91,935
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Supply cost you 482 men, at Swabia.
   Switzerland loyalty 88 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier reports that Bernadotte appears envious of Murat's laurels — he has grown cold and withholding.
   Berthier notes that Davout has grown restless — he sees his own laurels counted smaller while Ney wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Non-Aggression Pact.
   Talleyrand has departed for the court of Bavaria.
   THE LANDING: Paget has put 5,000 men ashore at Lisbon.
   THE LAWS: Prussia enacts the Articles of War — infantry drafts muster at +10 morale; cures Brittle — the court's doctrine flaw — while its Staff stands.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Switzerland has arrived with a petition.
   Bavaria has been established under the protection of France.
   Sire — France and Bavaria have signed the Vassalage.
   Talleyrand returns from Bavaria with a response.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-2)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "Gold buys armies, Sire. A court bought off now is a regiment the league never fields."
   ════════════════════════════════════
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► propose vassalization to Spain
   Directing Talleyrand: send suggested
   Reviewing the proposal again...
   Very well, Sire. Reconsider the matter and issue your orders anew.
   ► Davout, drill your corps
   Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 8.
   [3/4 actions remaining]
   ► Soult, drill
   Soult drills his corps with Boulogne-camp precision at Rhineland. Sharpen today, strike tomorrow — bonus ready turn 7, and he remains at your orders (though he cannot shift stance until the drill ends tonight).
   [2/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 7 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Contributions: -110g | Charges of Empire: -243g | Admiralty: -90g | Blockade: -328g | Other: +1745g | Upkeep: -1398g | Net: +2166g
   Treasury: 6,955g
   Actions refreshed: 4/4
   Davout is now locked in intensive drill. Cannot receive orders until training completes.
   DRILL COMPLETE: Soult's corps sharpens in a single day — Drillmaster of Boulogne. +20% attack bonus ready for next battle.
   Supply shortage at Tyrol: Archduke Charles loses 278 troops
   Supply shortage at Tyrol: Archduke John loses 270 troops
   Talleyrand returns from Spain empty-handed. The proposal was rejected. Talleyrand reports the key obstacle was the harshness of current demands.
   Britain subsidizes Russia with 200 gold.
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Prussia grows.
   Russia has downgraded relations with Sweden: OPEN_BORDERS → PEACE.
   Soult's resentment of Murat has cooled with time.
   Berthier reports that Davout resents Ney's laurels again, 4 turns after the last — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Massena has grown restless — he has not seen laurels while Murat wins them. I recommend giving him meaningful orders soon.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2149,286)  Spain(1162,854)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Britain(1311,336)  Papal States(1876,778)  Portugal(1112,816)  Hanover(1726,333)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  34(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney(1947,451)  Lannes(1962,425)  Bernadotte(1989,398)  ?(1980,302)  Brunswick(1981,263)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  ?(1445,626)  Paget(1445,586)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  Murat(1810,504)  ?(1504,393)  Castanos(1504,354)  Dumonceau(1742,301)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  ?(1759,600)  10k(1742,412)  12k(1694,412)  10k(1923,677)
```

```
#0180  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0180_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2120 of 2120 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   6,955
   Inf:
   91,935
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► Davout, drill your corps
   Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 8.
   [3/4 actions remaining]
   ► Soult, drill
   Soult drills his corps with Boulogne-camp precision at Rhineland. Sharpen today, strike tomorrow — bonus ready turn 7, and he remains at your orders (though he cannot shift stance until the drill ends tonight).
   [2/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 7 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Contributions: -110g | Charges of Empire: -243g | Admiralty: -90g | Blockade: -328g | Other: +1745g | Upkeep: -1398g | Net: +2166g
   Treasury: 6,955g
   Actions refreshed: 4/4
   Davout is now locked in intensive drill. Cannot receive orders until training completes.
   DRILL COMPLETE: Soult's corps sharpens in a single day — Drillmaster of Boulogne. +20% attack bonus ready for next battle.
   Supply shortage at Tyrol: Archduke Charles loses 278 troops
   Supply shortage at Tyrol: Archduke John loses 270 troops
   Talleyrand returns from Spain empty-handed. The proposal was rejected. Talleyrand reports the key obstacle was the harshness of current demands.
   Britain subsidizes Russia with 200 gold.
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Prussia grows.
   Russia has downgraded relations with Sweden: OPEN_BORDERS → PEACE.
   Soult's resentment of Murat has cooled with time.
   Berthier reports that Davout resents Ney's laurels again, 4 turns after the last — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Massena has grown restless — he has not seen laurels while Murat wins them. I recommend giving him meaningful orders soon.
   --- Strategic Order Updates ---
   Napoleon: Napoleon arrives at Rhineland.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 7
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Paget has crossed into Gascony. No French corps stands in his path.
   • Sire — Leon has been taken by Britain.
   • Sire — not every court of the league has struck us. Britain has an open road to us — 1 march — and has not struck us. Russia has no lawful road to us — the neutrality of Prussia and Hesse bars it.
   SITUATION
   France holds 28 regions. Treasury: 6,955g (+2,166 by the accounts)
   The courts at war hold 22 regions. Estimated enemy strength: 2% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 5 turns idle.
   * Davout — Swabia — 17,079 — Drilling.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 3 turns idle.
   - Murat — Franche-Comte — 15,416 — Awaiting orders.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — Awaiting orders.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Paget — Gascony — screening force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Davout is now locked in intensive drill. Cannot receive orders until training completes.
   DRILL COMPLETE: Soult's corps sharpens in a single day — Drillmaster of Boulogne. +20% attack bonus ready for next battle.
   Soult's resentment of Murat has cooled with time.
   Berthier reports that Davout resents Ney's laurels again, 4 turns after the last — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Massena has grown restless — he has not seen laurels while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Spain.
   Intelligence reports Britain has raised Wellesley to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand returns from Spain with a response.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-2)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 96/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0181  type Murat, pursue Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0181_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Murat pursues Paget (at Gascony). Cavalry charges through Nivernais -> Burgundy. Murat: "I will have him by the collar within the week."
── TopBar (layer 75) ──
   DP: 7/7
   Threat 96 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3216,64)]  [icon: Bavaria petitions over settlement scope @(3258,64)]  [icon: Settlement Ratified @(3300,64)]  [icon: Marshal Murat seeks an audience @(3342,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Vassalage Rejected @(3649,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -3
   T:6
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [scrolled 1652 of 1653 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,955
   Inf:
   91,935
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Britain subsidizes Russia with 200 gold.
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Prussia grows.
   Russia has downgraded relations with Sweden: OPEN_BORDERS → PEACE.
   Soult's resentment of Murat has cooled with time.
   Berthier reports that Davout resents Ney's laurels again, 4 turns after the last — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Massena has grown restless — he has not seen laurels while Murat wins them. I recommend giving him meaningful orders soon.
   --- Strategic Order Updates ---
   Napoleon: Napoleon arrives at Rhineland.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 7
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Paget has crossed into Gascony. No French corps stands in his path.
   • Sire — Leon has been taken by Britain.
   • Sire — not every court of the league has struck us. Britain has an open road to us — 1 march — and has not struck us. Russia has no lawful road to us — the neutrality of Prussia and Hesse bars it.
   SITUATION
   France holds 28 regions. Treasury: 6,955g (+2,166 by the accounts)
   The courts at war hold 22 regions. Estimated enemy strength: 2% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 5 turns idle.
   * Davout — Swabia — 17,079 — Drilling.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 3 turns idle.
   - Murat — Franche-Comte — 15,416 — Awaiting orders.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — Awaiting orders.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Paget — Gascony — screening force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Davout is now locked in intensive drill. Cannot receive orders until training completes.
   DRILL COMPLETE: Soult's corps sharpens in a single day — Drillmaster of Boulogne. +20% attack bonus ready for next battle.
   Soult's resentment of Murat has cooled with time.
   Berthier reports that Davout resents Ney's laurels again, 4 turns after the last — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Massena has grown restless — he has not seen laurels while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Spain.
   Intelligence reports Britain has raised Wellesley to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand returns from Spain with a response.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-2)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 96/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► Murat, pursue Paget
   Murat pursues Paget (at Gascony). Cavalry charges through Nivernais -> Burgundy. Murat: "I will have him by the collar within the week."
   [2/4 actions remaining]
map: unchanged (59 labels)
```

```
#0182  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0182_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 7
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   At War (2)
   Treaties (8)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Prussia  —  Non-Aggression  |  +22 (Neutral)  [MISSION]]  [Spain  —  Alliance  |  +34 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1652 of 1653 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   ► Murat, pursue Paget
   Murat pursues Paget (at Gascony). Cavalry charges through Nivernais -> Burgundy. Murat: "I will have him by the collar within the week."
   [2/4 actions remaining]
map: unchanged (59 labels)
```

```
#0183  click Prussia  —  Non-Aggression  ->  ok
  (clicked at (1825, 624))
view: <run>\frames\0183_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 178 px, 0 of 498 px] ──
   DIPLOMACY — Prussia
   DP: 7
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Non-Aggression   Relation: +22 (Neutral) /  / "We have Prussia's word they will not strike. A defensive alliance would bind us closer — if the relation bears it." / Recommendation: Talleyrand recommends: Propose Defensive Alliance /  / KEY FACTORS /   + Base willingness (+25) /   + Current relations (+11) /   + Diplomatic skill advantage (+8) /   - Hegem …
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends]  [Buy Off Their Design (1200g) (1 DP + 1200g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Defensive Alliance (2 DP)  —  Uncertain — a counter is likely]  [Propose Vassal (3 DP)  —  Unlikely]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1652 of 1653 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   ► Murat, pursue Paget
   Murat pursues Paget (at Gascony). Cavalry charges through Nivernais -> Burgundy. Murat: "I will have him by the collar within the week."
   [2/4 actions remaining]
map: unchanged (59 labels)
```

```
#0184  click Sponsor Their Design (200g/turn)  ->  ok
  (clicked at (1825, 473))
view: <run>\frames\0184_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 96 / 100
   Turn 7 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3216,64)]  [icon: Bavaria petitions over settlement scope @(3258,64)]  [icon: Settlement Ratified @(3300,64)]  [icon: Marshal Murat seeks an audience @(3342,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Vassalage Rejected @(3649,64)]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1763 of 1763 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   6,955
   Inf:
   91,935
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► sponsor Prussia against Hanover, 200 gold
   France sponsors Prussia's design against Hanover — 200 gold per turn for 10 turns. Talleyrand: "Their grievance now marches on our coin. Turning on them before it lapses would be reneging, Sire."
map: unchanged (59 labels)
```

```
#0185  type Massena, drill your men at Milan  ->  ok
  (typed and Enter)
view: <run>\frames\0185_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Massena begins intensive drill exercises at Milan. Troops will be locked in training next turn, bonus ready turn 9.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1874 of 1874 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   6,955
   Inf:
   91,935
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Massena, drill your men at Milan
   Massena begins intensive drill exercises at Milan. Troops will be locked in training next turn, bonus ready turn 9.
   [1/4 actions remaining]
map: unchanged (59 labels)
```

```
#0186  type Ney, drill  ->  ok
  (typed and Enter)
view: <run>\frames\0186_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 7 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 9.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1985 of 1985 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   7
   Actions:
   0/4
   Admin:
   2/2
   Gold:
   6,955
   Inf:
   91,935
   Cav:
   25,500
   Art:
   13,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Ney, drill
   Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 9.
   [0/4 actions remaining]
map: unchanged (59 labels)
```

```
#0187  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0187_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 7
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 95 / 100
   Turn 8 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1898 of 1900 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,726
   Inf:
   93,547
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 5 turns idle.
   * Davout — Swabia — 17,079 — Drilling.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 3 turns idle.
   - Murat — Franche-Comte — 15,416 — Awaiting orders.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — Awaiting orders.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Paget — Gascony — screening force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Davout is now locked in intensive drill. Cannot receive orders until training completes.
   DRILL COMPLETE: Soult's corps sharpens in a single day — Drillmaster of Boulogne. +20% attack bonus ready for next battle.
   Soult's resentment of Murat has cooled with time.
   Berthier reports that Davout resents Ney's laurels again, 4 turns after the last — he has grown quiet in the way the staff have learned to read.
   Berthier notes that Massena has grown restless — he has not seen laurels while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Spain.
   Intelligence reports Britain has raised Wellesley to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand returns from Spain with a response.
   Britain's gold reaches Russia — the subsidy stands at 200 this season.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-2)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 96/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   ► Murat, pursue Paget
   Murat pursues Paget (at Gascony). Cavalry charges through Nivernais -> Burgundy. Murat: "I will have him by the collar within the week."
   [2/4 actions remaining]
   ► sponsor Prussia against Hanover, 200 gold
   France sponsors Prussia's design against Hanover — 200 gold per turn for 10 turns. Talleyrand: "Their grievance now marches on our coin. Turning on them before it lapses would be reneging, Sire."
   ► Massena, drill your men at Milan
   Massena begins intensive drill exercises at Milan. Troops will be locked in training next turn, bonus ready turn 9.
   [1/4 actions remaining]
   ► Ney, drill
   Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 9.
   [0/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 8 BEGINS
   ═══════════════════════════════════════
   Income: 2590g | Subsidies: -200g | Contributions: -110g | Charges of Empire: -447g | Admiralty: -90g | Blockade: -328g | Other: +1754g | Upkeep: -1398g | Net: +1771g
   Treasury: 8,726g
   Actions refreshed: 4/4
   Ney is now locked in intensive drill. Cannot receive orders until training completes.
   DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 85).
   Massena is now locked in intensive drill. Cannot receive orders until training completes.
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 429 troops
   Supply shortage at Tyrol: Archduke John loses 317 troops
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Britain and Portugal grows.
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Murat's resentment of Ney has cooled with time.
   Bernadotte's resentment of Murat has cooled with time.
   Berthier notes that Massena has grown restless — he has not seen laurels while Murat wins them. I recommend giving him meaningful orders soon.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2149,286)  Spain(1162,854)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Britain(1311,336)  Papal States(1876,778)  Portugal(1112,816)  Hanover(1726,333)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  35(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney(1947,451)  Lannes(1962,425)  Bernadotte(1989,398)  ?(1980,302)  Brunswick(1981,263)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  ?(1445,626)  Paget(1445,586)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  Murat(1660,502)  ?(1504,393)  Castanos(1504,354)  Dumonceau(1742,301)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  ?(1759,600)  10k(1742,412)  12k(1694,412)  10k(1923,677)
```

```
#0188  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0188_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1784 of 1784 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,726
   Inf:
   93,547
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Ney is now locked in intensive drill. Cannot receive orders until training completes.
   DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 85).
   Massena is now locked in intensive drill. Cannot receive orders until training completes.
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 429 troops
   Supply shortage at Tyrol: Archduke John loses 317 troops
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Britain and Portugal grows.
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Murat's resentment of Ney has cooled with time.
   Bernadotte's resentment of Murat has cooled with time.
   Berthier notes that Massena has grown restless — he has not seen laurels while Murat wins them. I recommend giving him meaningful orders soon.
   --- Strategic Order Updates ---
   Murat: Murat is pursuing Paget (0 turns remaining).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 8
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Paget has crossed into Gascony. No French corps stands in his path.
   • Sire — Britain's gold reaches Russia — the subsidy stands at 300 this season.
   • Sire — an envoy from Prussia has arrived with a proposal.
   SITUATION
   France holds 28 regions. Treasury: 8,726g (+1,771 by the accounts)
   The courts at war hold 22 regions. Estimated enemy strength: 2% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   * Massena — Milan — 26,239 — Drilling.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   * Ney — Franconia — 15,795 — Drilling.
   > Murat — Burgundy — 15,416 — Pursuing Paget.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 3 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Paget — Gascony — screening force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Ney is now locked in intensive drill. Cannot receive orders until training completes.
   DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 85).
   Massena is now locked in intensive drill. Cannot receive orders until training completes.
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Murat's resentment of Ney has cooled with time.
   Bernadotte's resentment of Murat has cooled with time.
   Berthier notes that Massena has grown restless — he has not seen laurels while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 35.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Prussia — Defensive Alliance
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-3)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0189  click Envoys (1)  ->  ok
  (clicked at (3391, 18))
view: <run>\frames\0189_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   DIPLOMATIC ENVOY / Hardenberg (Hawk) of Prussia /  / Proposes: Defensive Alliance / Terms: /   - Proposal: Defensive Alliance /   - Clause: Open borders /  / Hardenberg, stiffly: "Prussia's interest is the Rhine at peace and the army at home; Berlin signs where those two meet. Stand with them if war comes." /  / A natural progression. This arrangement serves our interests. /  / This offer will lap …
   controls: [Accept]  [Counter]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1784 of 1784 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,726
   Inf:
   93,547
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
map: unchanged (59 labels)
```

```
#0190  click Accept  ->  ok
  (clicked at (1604, 687))
view: <run>\frames\0190_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 95 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3216,64)]  [icon: Bavaria petitions over settlement scope @(3258,64)]  [icon: Settlement Ratified @(3300,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(3618,64)]  [icon: Diplomatic Action Accepted @(3649,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Britain + Russia
   -3
   T:7
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
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
   8,726
   Inf:
   93,547
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Non-Aggression → Defensive Alliance with Prussia.
map: unchanged (59 labels)
```

```
#0191  click Recall  ->  ok
  (clicked at (3566, 64))
view: <run>\frames\0191_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: 'Talleyrand, cancel mission with Prussia' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
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
   8,726
   Inf:
   93,547
   Cav:
   27,250
   Art:
   14,200
   Talleyrand, cancel mission with Prussia
   controls: [+]  [−]  [—]  [Execute]  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, last lines ──
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Non-Aggression → Defensive Alliance with Prussia.
map: unchanged (59 labels)
```

```
#0192  key Enter  ->  ok
  (pressed Enter)
view: <run>\frames\0192_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1939 of 1939 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,726
   Inf:
   93,547
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Talleyrand, cancel mission with Prussia
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
map: unchanged (59 labels)
```

```
#0193  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0193_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   At War (2)
   Treaties (8)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Britain  —  At War  |  -90 (Hostile)]  [Russia  —  At War  |  -80 (Hostile)]  [Prussia  —  Defensive Alliance  |  +35 (Friendly)  [MISSION]]  [Spain  —  Alliance  |  +33 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You have accepted Prussia's proposal. Treaty signed: Non-Aggression → Defensive Alliance with Prussia.
   ► Talleyrand, cancel mission with Prussia
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
map: unchanged (59 labels)
```

```
#0194  click Prussia  —  Defensive Alliance  ->  ok
  (clicked at (1825, 624))
view: <run>\frames\0194_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 178 px, 0 of 489 px] ──
   DIPLOMACY — Prussia
   DP: 5
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Defensive Alliance   Relation: +35 (Friendly) /  / "Our alliance with Prussia holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus. /  / KEY FACTORS /   + Current relations (+18) /   + Base willingness …
   The compact already stands.
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends](disabled: The compact already stands.)  [Buy Off Their Design (1200g) (1 DP + 1200g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Alliance (2 DP)  —  Favorable](disabled: Relations with Prussia stand at 35; an Alliance needs 40.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   You have accepted Prussia's proposal. Treaty signed: Non-Aggression → Defensive Alliance with Prussia.
   ► Talleyrand, cancel mission with Prussia
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
map: unchanged (59 labels)
```

```
#0195  click Cancel  ->  ok
  (clicked at (1884, 740))
view: <run>\frames\0195_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1939 of 1939 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   You have accepted Prussia's proposal. Treaty signed: Non-Aggression → Defensive Alliance with Prussia.
   ► Talleyrand, cancel mission with Prussia
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
map: unchanged (59 labels)
```

```
#0196  type Murat, attack Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0196_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Murat (15,416) vs Paget (screening force) at Gascony — the balance of force looks favorable.
  The band weighs more than the men: the ground favors the defender (+25%, mountains).
  Gascony feeds 30,000 — the whole muster can stand there fed.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.

[Cavalry] Murat's cavalry thunders across Limousin to strike! (Cavalry Charge: 2-region attack)

[Combat] Murat leads the charge! (Aggressive: +15% attack)
[Shield] Paget's AGGRESSIVE stance leaves flanks exposed (-10% defense)
[Shield] Paget's reckless aggression weakens defense! (Aggressive: -5% additional)
[Terrain] Paget benefits from Mountains terrain (+25% defense)
Murat struggles in a costly engagement. Brutal stalemate between Murat and Paget. Heavy casualties on both sides: Murat 1,194, Paget 1,427.
[Materiel] Guns, horses and stores lost with the fallen: France -59g, Britain -71g. Murat's pursuit of Paget is set aside.
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   BRITAIN LOSSES
   0
   0
   ⚔
   Murat ◆
   Paget ◆
   15,416 → 14,222
   4,521 → 3,094
   BATTLE OF GASCONY
   click anywhere to skip ▸
   GASCONY · TURN 8
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2003 of 2003 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   8,667
   Inf:
   93,547
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   SITUATION
   France holds 28 regions. Treasury: 8,726g (+1,771 by the accounts)
   The courts at war hold 22 regions. Estimated enemy strength: 2% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   * Massena — Milan — 26,239 — Drilling.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   * Ney — Franconia — 15,795 — Drilling.
   > Murat — Burgundy — 15,416 — Pursuing Paget.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 3 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Paget — Gascony — screening force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Castanos — Normandy — small force [partial]
   TURN EVENTS
   Ney is now locked in intensive drill. Cannot receive orders until training completes.
   DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 85).
   Massena is now locked in intensive drill. Cannot receive orders until training completes.
   Berthier notes that Murat no longer presses the matter — his quarrel with Ney has cooled.
   Murat's resentment of Ney has cooled with time.
   Bernadotte's resentment of Murat has cooled with time.
   Berthier notes that Massena has grown restless — he has not seen laurels while Murat wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   An envoy from Prussia has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 35.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Prussia — Defensive Alliance
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (-3)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 95/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "They are on our soil, Sire. The marshals await only your word."
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Non-Aggression → Defensive Alliance with Prussia.
   ► Talleyrand, cancel mission with Prussia
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
   ► Murat, attack Paget
   ⚔ Battle of Gascony ⚔
   MUSTER — Murat (15,416) vs Paget (screening force) at Gascony — the balance of force looks favorable.
   The band weighs more than the men: the ground favors the defender (+25%, mountains).
   Gascony feeds 30,000 — the whole muster can stand there fed.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Cavalry] Murat's cavalry thunders across Limousin to strike! (Cavalry Charge: 2-region attack)
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Shield] Paget's AGGRESSIVE stance leaves flanks exposed (-10% defense)
   [Shield] Paget's reckless aggression weakens defense! (Aggressive: -5% additional)
   [Terrain] Paget benefits from Mountains terrain (+25% defense)
   Murat struggles in a costly engagement. Brutal stalemate between Murat and Paget. Heavy casualties on both sides: Murat 1,194, Paget 1,427.
   [Materiel] Guns, horses and stores lost with the fallen: France -59g, Britain -71g. Murat's pursuit of Paget is set aside.
   ⚔ View the field
   [3/4 actions remaining]
   --- Berthier's Report ---
   Murat: "Blood on both sides and no verdict — I despise an unfinished page."
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 1,194 | Paget 1,427
   Strength: Murat 15,416 → 14,222 | Paget 4,521 → 3,094
   Berthier: "An inconclusive affair. Both sides bloodied but unbroken."
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2149,286)  Spain(1162,854)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Britain(1311,336)  Papal States(1876,778)  Portugal(1112,816)  Hanover(1726,333)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  35(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney(1947,451)  Lannes(1962,425)  Bernadotte(1989,398)  ?(1980,302)  Brunswick(1981,263)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Paget(1445,622)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  Murat(1660,502)  ?(1504,393)  Castanos(1504,354)  Dumonceau(1742,301)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  ?(1759,600)  10k(1742,412)  12k(1694,412)  10k(1923,677)
```

```
#0197  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Murat ◆' (PanelContainer, layer 121))
view: <run>\frames\0197_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   A BLOODY STALEMATE
   FRANCE LOSSES
   BRITAIN LOSSES
   1,194
   1,427
   ⚔
   Murat ◆
   Paget ◆
   15,416 → 14,222
   4,521 → 3,094
   Berthier: “An inconclusive affair. Both sides bloodied but unbroken.” / Paget: "Neither of us yields? Good. I prefer a foe worth killing."
   BATTLE OF GASCONY
   GASCONY · TURN 8
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2003 of 2003 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 1,194 | Paget 1,427
   Strength: Murat 15,416 → 14,222 | Paget 4,521 → 3,094
   Berthier: "An inconclusive affair. Both sides bloodied but unbroken."
map: unchanged (58 labels)
```

```
#0198  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0198_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2003 of 2003 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 1,194 | Paget 1,427
   Strength: Murat 15,416 → 14,222 | Paget 4,521 → 3,094
   Berthier: "An inconclusive affair. Both sides bloodied but unbroken."
map: unchanged (58 labels)
```

```
#0199  type Murat, attack Paget again  ->  ok
  (typed and Enter)
view: <run>\frames\0199_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Murat (14,222) vs Paget (3,094 men) at Gascony — the balance of force looks favorable.
  The band weighs more than the men: the ground favors the defender (+25%, mountains).
  Gascony feeds 30,000 — the whole muster can stand there fed.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.

[Cavalry] Murat's cavalry thunders across Limousin to strike! (Cavalry Charge: 2-region attack)

[Combat] Murat leads the charge! (Aggressive: +15% attack)
[Shield] Paget's AGGRESSIVE stance leaves flanks exposed (-10% defense)
[Shield] Paget's reckless aggression weakens defense! (Aggressive: -5% additional)
[Alert] Murat's cavalry builds momentum! (2nd charge: +5%)
[Terrain] Paget benefits from Mountains terrain (+25% defense)
Murat engages in solid combat. Murat gains the advantage over Paget. Casualties: Murat 645, Paget 1,887. Both armies remain in the field.

[Cavalry] Murat's blood is up! (Recklessness: 1) Murat advances into Gascony.
[Materiel] Guns, horses and stores lost with the fallen: France -32g, Britain -94g.
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   BRITAIN LOSSES
   0
   0
   ⚔
   Murat ◆
   Paget ◆
   14,222 → 13,577
   3,094 → 1,207
   SECOND BATTLE OF GASCONY
   click anywhere to skip ▸
   GASCONY · TURN 8
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 98 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3216,64)]  [icon: Bavaria petitions over settlement scope @(3258,64)]  [icon: Settlement Ratified @(3300,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(3618,64)]  [icon: Diplomatic Action Accepted @(3649,64)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Russia
   0
   T:7
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2687 of 2687 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   2/4
   Admin:
   2/2
   Gold:
   8,635
   Inf:
   93,547
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Murat, attack Paget again
   ⚔ Second Battle of Gascony ⚔
   MUSTER — Murat (14,222) vs Paget (3,094 men) at Gascony — the balance of force looks favorable.
   The band weighs more than the men: the ground favors the defender (+25%, mountains).
   Gascony feeds 30,000 — the whole muster can stand there fed.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Cavalry] Murat's cavalry thunders across Limousin to strike! (Cavalry Charge: 2-region attack)
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Shield] Paget's AGGRESSIVE stance leaves flanks exposed (-10% defense)
   [Shield] Paget's reckless aggression weakens defense! (Aggressive: -5% additional)
   [Alert] Murat's cavalry builds momentum! (2nd charge: +5%)
   [Terrain] Paget benefits from Mountains terrain (+25% defense)
   Murat engages in solid combat. Murat gains the advantage over Paget. Casualties: Murat 645, Paget 1,887. Both armies remain in the field.
   [Cavalry] Murat's blood is up! (Recklessness: 1) Murat advances into Gascony.
   [Materiel] Guns, horses and stores lost with the fallen: France -32g, Britain -94g.
   ⚔ View the field
   [2/4 actions remaining]
   --- Berthier's Report ---
   Murat: "They ran, Sire. I have never learned to walk after a running man."
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 645 | Paget 1,887
   Strength: Murat 14,222 → 13,577 | Paget 3,094 → 1,207
   Berthier: "A costly day for Paget: the losses ran two to one in Murat's favour, and Paget is still in the field."
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2149,286)  Spain(1162,854)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Britain(1311,336)  Papal States(1876,778)  Portugal(1112,816)  Hanover(1726,333)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  35(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney(1947,451)  Lannes(1962,425)  Bernadotte(1989,398)  ?(1980,302)  Brunswick(1981,263)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1431,622)  Paget(1460,595)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  ?(1504,393)  Castanos(1504,354)  Dumonceau(1742,301)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  ?(1759,600)  10k(1742,412)  12k(1694,412)  10k(1923,677)
```

```
#0200  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Murat ◆' (PanelContainer, layer 121))
view: <run>\frames\0200_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS OURS
   FRANCE LOSSES
   BRITAIN LOSSES
   645
   1,887
   ⚔
   Murat ◆
   Paget ◆
   14,222 → 13,577
   3,094 → 1,207
   Berthier: “A costly day for Paget: the losses ran two to one in Murat's favour, and Paget is still in the field.” / Paget: "You have my ground. Keep it warm for me."
   SECOND BATTLE OF GASCONY
   GASCONY · TURN 8
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2687 of 2687 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 645 | Paget 1,887
   Strength: Murat 14,222 → 13,577 | Paget 3,094 → 1,207
   Berthier: "A costly day for Paget: the losses ran two to one in Murat's favour, and Paget is still in the field."
map: unchanged (58 labels)
```

```
#0201  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0201_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2687 of 2687 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 645 | Paget 1,887
   Strength: Murat 14,222 → 13,577 | Paget 3,094 → 1,207
   Berthier: "A costly day for Paget: the losses ran two to one in Murat's favour, and Paget is still in the field."
map: unchanged (58 labels)
```

```
#0202  type Murat, finish off Paget  ->  ok
  (typed and Enter)
view: <run>\frames\0202_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
reply: ok MUSTER — Murat (13,577) vs Paget (1,207 men) at Gascony — the balance of force looks favorable.
  The band weighs more than the men: the ground favors the defender (+25%, mountains).
  Gascony feeds 30,000 — the whole muster can stand there fed.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.


Murat holds them at Gascony while allies attack from Burgundy! (+1 coordination)

[Combat] Murat leads the charge! (Aggressive: +15% attack)
[Shield] Paget's AGGRESSIVE stance leaves flanks exposed (-10% defense)
[Shield] Paget's reckless aggression weakens defense! (Aggressive: -5% additional)
[Alert] Murat's cavalry builds momentum! (3rd charge: +10%)
[Terrain] Paget benefits from Mountains terrain (+25% defense)
[Cavalry] Murat's cavalry is hampered by Mountains terrain (30% effectiveness)
Murat's forces press forward aggressively. Murat gains the advantage over Paget. Casualties: Murat 229, Paget 1,105. Both armies remain in the field.

[!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT!

[Cavalry] Murat is building momentum! (Recklessness: 2)
[Materiel] Guns, horses and stores lost with the fallen: France -11g, Britain -55g.
[!] Paget's broken army flees to Berry! (recovering for 3 turns)
── BattleDiorama (layer 121) ──
   FRANCE LOSSES
   BRITAIN LOSSES
   0
   0
   ⚔
   Murat ◆
   Paget ◆
   13,577 → 13,348
   1,207 → 102
   THIRD BATTLE OF GASCONY
   click anywhere to skip ▸
   GASCONY · TURN 8
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 100 / 100
   Turn 8 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3216,64)]  [icon: Bavaria petitions over settlement scope @(3258,64)]  [icon: Settlement Ratified @(3300,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(3618,64)]  [icon: Diplomatic Action Accepted @(3649,64)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Russia
   +3
   T:7
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2930 of 2930 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   8
   Actions:
   1/4
   Admin:
   2/2
   Gold:
   8,624
   Inf:
   93,547
   Cav:
   27,250
   Art:
   14,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ════════════════════════════════════
   Responding to Prussia's proposal: accepted
   You have accepted Prussia's proposal. Treaty signed: Non-Aggression → Defensive Alliance with Prussia.
   ► Talleyrand, cancel mission with Prussia
   Berthier: Matters of state are conducted at the table, Sire — not by dispatch. Take your seat in the Cabinet and the courts of Europe will answer.
   ⚜ Take your seat at the table (F1)
   ► Murat, attack Paget
   ⚔ Battle of Gascony ⚔
   MUSTER — Murat (15,416) vs Paget (screening force) at Gascony — the balance of force looks favorable.
   The band weighs more than the men: the ground favors the defender (+25%, mountains).
   Gascony feeds 30,000 — the whole muster can stand there fed.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Cavalry] Murat's cavalry thunders across Limousin to strike! (Cavalry Charge: 2-region attack)
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Shield] Paget's AGGRESSIVE stance leaves flanks exposed (-10% defense)
   [Shield] Paget's reckless aggression weakens defense! (Aggressive: -5% additional)
   [Terrain] Paget benefits from Mountains terrain (+25% defense)
   Murat struggles in a costly engagement. Brutal stalemate between Murat and Paget. Heavy casualties on both sides: Murat 1,194, Paget 1,427.
   [Materiel] Guns, horses and stores lost with the fallen: France -59g, Britain -71g. Murat's pursuit of Paget is set aside.
   ⚔ View the field
   [3/4 actions remaining]
   --- Berthier's Report ---
   Murat: "Blood on both sides and no verdict — I despise an unfinished page."
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 1,194 | Paget 1,427
   Strength: Murat 15,416 → 14,222 | Paget 4,521 → 3,094
   Berthier: "An inconclusive affair. Both sides bloodied but unbroken."
   ► Murat, attack Paget again
   ⚔ Second Battle of Gascony ⚔
   MUSTER — Murat (14,222) vs Paget (3,094 men) at Gascony — the balance of force looks favorable.
   The band weighs more than the men: the ground favors the defender (+25%, mountains).
   Gascony feeds 30,000 — the whole muster can stand there fed.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Cavalry] Murat's cavalry thunders across Limousin to strike! (Cavalry Charge: 2-region attack)
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Shield] Paget's AGGRESSIVE stance leaves flanks exposed (-10% defense)
   [Shield] Paget's reckless aggression weakens defense! (Aggressive: -5% additional)
   [Alert] Murat's cavalry builds momentum! (2nd charge: +5%)
   [Terrain] Paget benefits from Mountains terrain (+25% defense)
   Murat engages in solid combat. Murat gains the advantage over Paget. Casualties: Murat 645, Paget 1,887. Both armies remain in the field.
   [Cavalry] Murat's blood is up! (Recklessness: 1) Murat advances into Gascony.
   [Materiel] Guns, horses and stores lost with the fallen: France -32g, Britain -94g.
   ⚔ View the field
   [2/4 actions remaining]
   --- Berthier's Report ---
   Murat: "They ran, Sire. I have never learned to walk after a running man."
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 645 | Paget 1,887
   Strength: Murat 14,222 → 13,577 | Paget 3,094 → 1,207
   Berthier: "A costly day for Paget: the losses ran two to one in Murat's favour, and Paget is still in the field."
   ► Murat, finish off Paget
   ⚔ Third Battle of Gascony ⚔
   MUSTER — Murat (13,577) vs Paget (1,207 men) at Gascony — the balance of force looks favorable.
   The band weighs more than the men: the ground favors the defender (+25%, mountains).
   Gascony feeds 30,000 — the whole muster can stand there fed.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Murat holds them at Gascony while allies attack from Burgundy! (+1 coordination)
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Shield] Paget's AGGRESSIVE stance leaves flanks exposed (-10% defense)
   [Shield] Paget's reckless aggression weakens defense! (Aggressive: -5% additional)
   [Alert] Murat's cavalry builds momentum! (3rd charge: +10%)
   [Terrain] Paget benefits from Mountains terrain (+25% defense)
   [Cavalry] Murat's cavalry is hampered by Mountains terrain (30% effectiveness)
   Murat's forces press forward aggressively. Murat gains the advantage over Paget. Casualties: Murat 229, Paget 1,105. Both armies remain in the field.
   [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT!
   [Cavalry] Murat is building momentum! (Recklessness: 2)
   [Materiel] Guns, horses and stores lost with the fallen: France -11g, Britain -55g.
   [!] Paget's broken army flees to Berry! (recovering for 3 turns)
   🐴 Murat's cavalry is hampered by Mountains terrain (30% effectiveness)
   ⚔ View the field
   [1/4 actions remaining]
   --- Berthier's Report ---
   Murat: "Was it not magnificent? The plume went first through their line, Sire."
   Attack: Murat (Personality (aggressive) +15%, Recklessness +5%, Cavalry terrain (mountains) -70%, Flanking +1%)
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 229 | Paget 1,105
   Strength: Murat 13,577 → 13,348 | Paget 1,207 → 102
   Berthier: "The exchange went Murat's way, Sire — Paget paid twice what Murat did, though the day decided nothing yet."
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2149,286)  Spain(1162,854)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Britain(1311,336)  Papal States(1876,778)  Portugal(1112,816)  Hanover(1726,333)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  35(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  ?(1473,511)  Paget(1473,472)  Ney(1947,451)  Lannes(1962,425)  Bernadotte(1989,398)  ?(1980,302)  Brunswick(1981,263)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  ?(1504,393)  Castanos(1504,354)  Dumonceau(1742,301)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1910,360)  25k(1556,504)  12k(1504,442)  ?(1759,600)  10k(1742,412)  12k(1694,412)  10k(1923,677)
```

```
#0203  click_at 1800 500  ->  ok
  (clicked at (1800, 500) on Tray 'Murat ◆' (PanelContainer, layer 121))
view: <run>\frames\0203_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['battle_diorama', 'war_status_panel (not modal)'], region_panel=no
── BattleDiorama (layer 121) ──
   THE FIELD IS OURS
   FRANCE LOSSES
   BRITAIN LOSSES
   229
   1,105
   ⚔
   Murat ◆
   Paget ◆
   13,577 → 13,348
   1,207 → 102
   ROUTED
   Berthier: “The exchange went Murat's way, Sire — Paget paid twice what Murat did, though the day decided nothing yet.” / Paget: "I go to fetch more men. Do wait."
   THIRD BATTLE OF GASCONY
   GASCONY · TURN 8
   controls: [Close]  [Replay]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2930 of 2930 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 229 | Paget 1,105
   Strength: Murat 13,577 → 13,348 | Paget 1,207 → 102
   Berthier: "The exchange went Murat's way, Sire — Paget paid twice what Murat did, though the day decided nothing yet."
map: unchanged (59 labels)
```

```
#0204  click Close  ->  ok
  (clicked at (2230, 815))
view: <run>\frames\0204_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 8 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2930 of 2930 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 229 | Paget 1,105
   Strength: Murat 13,577 → 13,348 | Paget 1,207 → 102
   Berthier: "The exchange went Murat's way, Sire — Paget paid twice what Murat did, though the day decided nothing yet."
map: unchanged (59 labels)
```

```
#0205  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0205_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 8
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 97 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2955 of 2956 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,554
   Inf:
   95,059
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 1,194 | Paget 1,427
   Strength: Murat 15,416 → 14,222 | Paget 4,521 → 3,094
   Berthier: "An inconclusive affair. Both sides bloodied but unbroken."
   ► Murat, attack Paget again
   ⚔ Second Battle of Gascony ⚔
   MUSTER — Murat (14,222) vs Paget (3,094 men) at Gascony — the balance of force looks favorable.
   The band weighs more than the men: the ground favors the defender (+25%, mountains).
   Gascony feeds 30,000 — the whole muster can stand there fed.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   [Cavalry] Murat's cavalry thunders across Limousin to strike! (Cavalry Charge: 2-region attack)
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Shield] Paget's AGGRESSIVE stance leaves flanks exposed (-10% defense)
   [Shield] Paget's reckless aggression weakens defense! (Aggressive: -5% additional)
   [Alert] Murat's cavalry builds momentum! (2nd charge: +5%)
   [Terrain] Paget benefits from Mountains terrain (+25% defense)
   Murat engages in solid combat. Murat gains the advantage over Paget. Casualties: Murat 645, Paget 1,887. Both armies remain in the field.
   [Cavalry] Murat's blood is up! (Recklessness: 1) Murat advances into Gascony.
   [Materiel] Guns, horses and stores lost with the fallen: France -32g, Britain -94g.
   ⚔ View the field
   [2/4 actions remaining]
   --- Berthier's Report ---
   Murat: "They ran, Sire. I have never learned to walk after a running man."
   Attack: Murat (Personality (aggressive) +15%)
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 645 | Paget 1,887
   Strength: Murat 14,222 → 13,577 | Paget 3,094 → 1,207
   Berthier: "A costly day for Paget: the losses ran two to one in Murat's favour, and Paget is still in the field."
   ► Murat, finish off Paget
   ⚔ Third Battle of Gascony ⚔
   MUSTER — Murat (13,577) vs Paget (1,207 men) at Gascony — the balance of force looks favorable.
   The band weighs more than the men: the ground favors the defender (+25%, mountains).
   Gascony feeds 30,000 — the whole muster can stand there fed.
   Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him.
   Murat holds them at Gascony while allies attack from Burgundy! (+1 coordination)
   [Combat] Murat leads the charge! (Aggressive: +15% attack)
   [Shield] Paget's AGGRESSIVE stance leaves flanks exposed (-10% defense)
   [Shield] Paget's reckless aggression weakens defense! (Aggressive: -5% additional)
   [Alert] Murat's cavalry builds momentum! (3rd charge: +10%)
   [Terrain] Paget benefits from Mountains terrain (+25% defense)
   [Cavalry] Murat's cavalry is hampered by Mountains terrain (30% effectiveness)
   Murat's forces press forward aggressively. Murat gains the advantage over Paget. Casualties: Murat 229, Paget 1,105. Both armies remain in the field.
   [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT!
   [Cavalry] Murat is building momentum! (Recklessness: 2)
   [Materiel] Guns, horses and stores lost with the fallen: France -11g, Britain -55g.
   [!] Paget's broken army flees to Berry! (recovering for 3 turns)
   🐴 Murat's cavalry is hampered by Mountains terrain (30% effectiveness)
   ⚔ View the field
   [1/4 actions remaining]
   --- Berthier's Report ---
   Murat: "Was it not magnificent? The plume went first through their line, Sire."
   Attack: Murat (Personality (aggressive) +15%, Recklessness +5%, Cavalry terrain (mountains) -70%, Flanking +1%)
   Defense: Paget (Aggressive stance -10%, Personality (aggressive) -5%, Terrain (Mountains) +25%, The Line Holds +15%)
   Casualties: Murat 229 | Paget 1,105
   Strength: Murat 13,577 → 13,348 | Paget 1,207 → 102
   Berthier: "The exchange went Murat's way, Sire — Paget paid twice what Murat did, though the day decided nothing yet."
   ► end turn
   ═══════════════════════════════════════
   TURN 9 BEGINS
   ═══════════════════════════════════════
   Income: 2547g | Subsidies: -200g | Charges of Empire: -426g | Admiralty: -90g | Blockade: -328g | Other: +1765g | Upkeep: -1338g | Net: +1930g
   Treasury: 10,554g
   Actions refreshed: 4/4
   DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 85).
   DRILL COMPLETE: Massena's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 72).
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 504 troops
   Supply shortage at Tyrol: Archduke John loses 332 troops
   Holland loyalty 100 (+2): a common enemy, the lord's victories
   Bavaria loyalty 62 (+2): the lord's victories, relations with the lord
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Russia and Sweden grows.
   The rivalry between Bernadotte and Murat has become entrenched. The wound will not close on its own.
   Ney no longer wears the army's laurels alone — Ney and Murat now stand level at its head, and no one wears them.
   Berthier reports that Bernadotte resents Murat's laurels again, 3 turns after the last — he has grown quiet in the way the staff have learned to read.
   Berthier reports that Lannes appears envious of Murat's laurels — he has grown impatient for something worth the doing.
   Davout's resentment of Ney has cooled with time.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2149,286)  Spain(1162,854)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Britain(1311,336)  Papal States(1876,778)  Portugal(1112,816)  Hanover(1726,333)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,586)  36(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney(1947,451)  Lannes(1962,425)  Bernadotte(1989,398)  ?(1980,302)  Brunswick(1981,263)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  ?(1309,653)  Castanos(1309,613)  Dumonceau(1742,301)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  ?(1759,600)  10k(1742,412)  12k(1694,412)  10k(1923,677)
```

```
#0206  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0206_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['marshal_petition', 'war_status_panel (not modal)'], region_panel=no
── MarshalPetitionDialog (layer 114) [scrolled 0 of 119 px] ──
   BERNADOTTE — Marshal Bernadotte demands to be heard
   Give him a command is closed — There is no enemy within his reach to send him against.
   "My corps is in good order, Sire. It has been in good order for some time now." /  / Sire, Bernadotte submitted a summary of his corps' service this season. It is accurate, and it is longer than it needed to be. The breach between them has become entrenched; he presses the point with unusual heat.
   Free, and it fixes nothing. For 5 more turns he brings NONE of his 11,647 men to any battle Murat leads, quarrel or no quarrel — they are openly at odds already, and the quarrel may harden further.
   His patience is bought — the grievance shortens by 2 turns, and for 6 turns the quarrel cannot harden further.
   controls: [Let it stand   [Free]]  [Promise Glory   [1 AP]]  [Later (he will return)]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 97 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Envoy from Britain @(3216,64)]  [icon: Napoleon arrived @(3258,64)]  [icon: Bavaria petitions over settlement scope @(3300,64)]  [icon: Settlement Ratified @(3342,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Marshal Murat expects reward @(3649,64)]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Britain + Russia
   +2
   T:8
   controls: [THIRD COALITION  ▸]  [Britain + Russia]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1850 of 1850 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,554
   Inf:
   95,059
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 504 troops
   Supply shortage at Tyrol: Archduke John loses 332 troops
   Holland loyalty 100 (+2): a common enemy, the lord's victories
   Bavaria loyalty 62 (+2): the lord's victories, relations with the lord
   Britain subsidizes Russia with 300 gold.
   Territorial rivalry between Russia and Sweden grows.
   The rivalry between Bernadotte and Murat has become entrenched. The wound will not close on its own.
   Ney no longer wears the army's laurels alone — Ney and Murat now stand level at its head, and no one wears them.
   Berthier reports that Bernadotte resents Murat's laurels again, 3 turns after the last — he has grown quiet in the way the staff have learned to read.
   Berthier reports that Lannes appears envious of Murat's laurels — he has grown impatient for something worth the doing.
   Davout's resentment of Ney has cooled with time.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 9
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Marshal Murat holds the field at Gascony — Paget's corps is driven from Gascony yet again — broken, and fleeing.
   • Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
   • Sire — Austria would now join a league against us — relations −75. Britain and Russia pay her 400 gold a turn against us. A league stands declared without her; she would march in the next — the price to keep her out: Talleyrand brings her to −10 in 8 turns (8 DP); buying off her design costs 1,320 gold and shortens the road to 7 turns.
   SITUATION
   France holds 28 regions. Treasury: 10,554g (+1,930 by the accounts)
   The courts at war hold 22 regions. Estimated enemy strength: 0% of French forces (known corps only — unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 7 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 5 turns idle.
   - Murat — Gascony — 13,348 — Awaiting orders.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 4 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Castanos — Bordelais — small force [partial]
   TURN EVENTS
   DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 85).
   DRILL COMPLETE: Massena's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 72).
   2 satellites steadied — Holland and Bavaria.
   The rivalry between Bernadotte and Murat has become entrenched. The wound will not close on its own.
   Ney no longer wears the army's laurels alone — Ney and Murat now stand level at its head, and no one wears them.
   Berthier reports that Bernadotte resents Murat's laurels again, 3 turns after the last — he has grown quiet in the way the staff have learned to read.
   Berthier reports that Lannes appears envious of Murat's laurels — he has grown impatient for something worth the doing.
   Davout's resentment of Ney has cooled with time.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Defensive Alliance.
   THE LAWS: Russia enacts the Extraordinary Levy — infantry levies cost 20% less (×0.8); infantry drafts muster at -10 morale.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   An envoy from Britain has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 43.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 5 in hand); or let the war come, having been asked.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Armistice Losing
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+3)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
map: unchanged (57 labels)
```

```
#0207  click Let it stand  ->  ok
  (clicked at (1825, 526))
view: <run>\frames\0207_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 0 of 508 px] ──
   DIPLOMATIC ENVOY / Castlereagh (Hawk) of Britain /  / Proposes: Armistice / Terms: /   - Proposal: Armistice / Assessment: GENEROUS /  / War Summary / War score: 3 ^ (Battle +6) / Settlement: White Peace / Objective: Defense - the homeland — 28 of 28 provinces held (inactive) / Ticking: +0 / Duration: 7 turns   Battles: 2W / 0L / Casualties: ours 874 / theirs 2992 /  / Armistice Terms /   A 5-turn …
   controls: [Accept]  [Counter]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 97 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail · BLOCKADED]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1894 of 1894 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,554
   Inf:
   95,059
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Bernadotte's grievance runs its course.
map: unchanged (57 labels)
```

```
#0208  scroll 1825 500 down 5  ->  ok
  (scrolled down 5 at (1825, 500))
view: <run>\frames\0208_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) [scrolled 220 of 508 px] ──
   DIPLOMATIC ENVOY / Castlereagh (Hawk) of Britain /  / Proposes: Armistice / Terms: /   - Proposal: Armistice / Assessment: GENEROUS /  / War Summary / War score: 3 ^ (Battle +6) / Settlement: White Peace / Objective: Defense - the homeland — 28 of 28 provinces held (inactive) / Ticking: +0 / Duration: 7 turns   Battles: 2W / 0L / Casualties: ours 874 / theirs 2992 /  / Armistice Terms /   A 5-turn …
   controls: [Accept]  [Counter]  [Reject]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1894 of 1894 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
map: unchanged (57 labels)
```

```
#0209  click Accept  ->  ok
  (clicked at (1604, 687))
view: <run>\frames\0209_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 97 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3216,64)]  [icon: Bavaria petitions over settlement scope @(3258,64)]  [icon: Settlement Ratified @(3300,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Marshal Murat expects reward @(3618,64)]  [icon: Treaty with Britain @(3649,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Russia
   0
   T:8
   controls: [THIRD COALITION  ▸]  [Russia]  [Britain  5t]
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
   10,554
   Inf:
   95,059
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
map: unchanged (57 labels)
```

```
#0210  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0210_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   At War (1)
   Treaties (9)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Russia  —  At War  |  -80 (Hostile)]  [Britain  —  Armistice  |  -90 (Hostile)]  [Prussia  —  Defensive Alliance  |  +43 (Friendly)  [MISSION]]  [Spain  —  Alliance  |  +32 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
map: unchanged (57 labels)
```

```
#0211  click Prussia  —  Defensive Alliance  ->  ok
  (clicked at (1825, 624))
view: <run>\frames\0211_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 156 px, 0 of 466 px] ──
   DIPLOMACY — Prussia
   DP: 5
   TALLEYRAND'S ASSESSMENT — PRUSSIA / Status: Defensive Alliance   Relation: +43 (Friendly) /  / "Our alliance with Prussia holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Talleyrand recommends: Propose Alliance /  / KEY FACTORS /   + Current relations (+22) /   + Base willingness (+20) /   + Talleyrand's courting (+10) /   - Diplomat personality (-5 …
   The compact already stands.
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Hanover — gold flows, the compact binds both ends](disabled: The compact already stands.)  [Buy Off Their Design (1272g) (1 DP + 1272g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Alliance (2 DP)  —  Favorable]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1960 of 1960 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
map: unchanged (57 labels)
```

```
#0212  click Propose Alliance (2 DP)  ->  ok
  (clicked at (1825, 645))
view: <run>\frames\0212_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Prussia /  / Mutual: /   • Mutual open borders between France and Prussia /  / Harshness: Low / Acceptance estimate: ~54% (ACCEPT) / Key obstacle: personal opposition from their diplomat / DP cost: 2 /  / "Sire, regarding the Full Alliance proposal to Prussia, I have prepared terms that reflect the current diplomatic climate."
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 97 / 100
   Turn 9 — Late January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2006 of 2006 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,554
   Inf:
   95,059
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose alliance with Prussia
map: unchanged (57 labels)
```

```
#0213  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0213_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Prussia /  / France concedes: /   • France pays 500 gold to Prussia / Mutual: /   • Mutual open borders between France and Prussia /  / Harshness: Low / Acceptance estimate: ~60% (ACCEPT) / Key obstacle: personal opposition from their diplomat / DP cost: 2 /  / "A magnanimous approach, Sire. More generous terms for Prussia."
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2027 of 2027 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,554
   Inf:
   95,059
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (57 labels)
```

```
#0214  click Send these terms  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0214_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 3/7
   Threat 97 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3351,64)]  [icon: Bavaria petitions over settlement scope @(3393,64)]  [icon: Settlement Ratified @(3435,64)]  [icon: Marshal Murat expects reward @(3477,64)]  [icon: Treaty with Britain @(3519,64)]  [icon: Diplomatic Action Accepted @(3561,64)]  [+18]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Russia
   0
   T:8
   controls: [THIRD COALITION  ▸]  [Russia]  [Britain  5t]
── BottomLeftUI (layer 0) [scrolled 2093 of 2093 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,554
   Inf:
   95,059
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Prussia court with your Full Alliance proposal. Expect a response by next turn. (2 DP spent)
map: unchanged (57 labels)
```

```
#0215  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0215_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 6 of 8 terms met  ▸ the terms
   At War (1)
   Treaties (9)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action)](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Russia  —  At War  |  -80 (Hostile)]  [Britain  —  Armistice  |  -90 (Hostile)]  [Prussia  —  Defensive Alliance  |  +43 (Friendly)  [MISSION]]  [Spain  —  Alliance  |  +32 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2093 of 2093 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose alliance with Prussia
   Directing Talleyrand: modify generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Prussia court with your Full Alliance proposal. Expect a response by next turn. (2 DP spent)
map: unchanged (57 labels)
```

```
#0216  scroll 1825 600 down 15  ->  ok
  (scrolled down 15 at (1825, 600))
view: <run>\frames\0216_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 627 of 667 px] ──
   DIPLOMACY
   DP: 3
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (5)
   controls: [icon: Close (Esc) @(2075,284)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Austria  —  Peace  |  -75 (Hostile)]  [Sweden  —  Peace  |  -47 (Hostile)]  [Naples  —  Peace  |  -22 (Wary)]  [Hanover  —  Peace  |  -42 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2093 of 2093 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose alliance with Prussia
   Directing Talleyrand: modify generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Prussia court with your Full Alliance proposal. Expect a response by next turn. (2 DP spent)
map: unchanged (57 labels)
```

```
#0217  click Austria  —  Peace  ->  ok
  (clicked at (1825, 523))
view: <run>\frames\0217_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 46 px, 0 of 438 px] ──
   DIPLOMACY — Austria
   DP: 3
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -75 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus.
   Their design is aimed at France herself.
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1272g) (1 DP + 1272g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Open Borders (1 DP)  —  Hopeless](disabled: Talleyrand in transit)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2093 of 2093 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► propose alliance with Prussia
   Directing Talleyrand: modify generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Prussia court with your Full Alliance proposal. Expect a response by next turn. (2 DP spent)
map: unchanged (57 labels)
```

```
#0218  click Buy Off Their Design (1272g)  ->  ok
  (clicked at (1825, 540))
view: <run>\frames\0218_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 2/7
   Threat 97 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3351,64)]  [icon: Bavaria petitions over settlement scope @(3393,64)]  [icon: Settlement Ratified @(3435,64)]  [icon: Marshal Murat expects reward @(3477,64)]  [icon: Treaty with Britain @(3519,64)]  [icon: Diplomatic Action Accepted @(3561,64)]  [+18]
── WarStatusPanel (layer 25): unchanged
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
   9,282
   Inf:
   95,059
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1272 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (57 labels)
```

```
#0219  click Marshal Murat expects reward  ->  ok
  (clicked at (3477, 64))
view: <run>\frames\0219_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 2/7
   Threat 97 / 100
   Turn 9 — Late January 1806
   Imperial Box
   Marshal Murat expects reward
   T9
   Marshal Murat looks for 40g/turn and holds 0g. His patience holds 4 turns — settle it now with "pension Murat" (a rente, 60g/turn).
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3351,64)]  [icon: Bavaria petitions over settlement scope @(3393,64)]  [icon: Settlement Ratified @(3435,64)]  [icon: Marshal Murat expects reward @(3477,64)]  [icon: Treaty with Britain @(3519,64)]  [icon: Diplomatic Action Accepted @(3561,64)]  [+18]  [Grant rente — 60g/turn]  [Reward…]  [Keep]  [Acknowledge]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2204 of 2204 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Prussia court with your Full Alliance proposal. Expect a response by next turn. (2 DP spent)
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1272 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (57 labels)
```

```
#0220  click Grant rente — 60g/turn  ->  ok
  (clicked at (3493, 221))
view: <run>\frames\0220_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 9 — Late January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 2/7
   Threat 97 / 100
   Turn 9 — Late January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Napoleon arrived @(3247,64)]  [icon: Bavaria petitions over settlement scope @(3289,64)]  [icon: Settlement Ratified @(3331,64)]  [icon: Treaty with Britain @(3373,64)]  [icon: Diplomatic Action Accepted @(3415,64)]  [Talleyrand at Prussia — Courting]  [+17]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1740 of 1740 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   9
   Actions:
   4/4
   Admin:
   1/2
   Gold:
   9,282
   Inf:
   95,059
   Cav:
   29,000
   Art:
   14,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 7 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 5 turns idle.
   - Murat — Gascony — 13,348 — Awaiting orders.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 4 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   - Dumonceau — Amsterdam — 6,500 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   Castanos — Bordelais — small force [partial]
   TURN EVENTS
   DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 85).
   DRILL COMPLETE: Massena's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 72).
   2 satellites steadied — Holland and Bavaria.
   The rivalry between Bernadotte and Murat has become entrenched. The wound will not close on its own.
   Ney no longer wears the army's laurels alone — Ney and Murat now stand level at its head, and no one wears them.
   Berthier reports that Bernadotte resents Murat's laurels again, 3 turns after the last — he has grown quiet in the way the staff have learned to read.
   Berthier reports that Lannes appears envious of Murat's laurels — he has grown impatient for something worth the doing.
   Davout's resentment of Ney has cooled with time.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Defensive Alliance.
   THE LAWS: Russia enacts the Extraordinary Levy — infantry levies cost 20% less (×0.8); infantry drafts muster at -10 morale.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   An envoy from Britain has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 43.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 5 in hand); or let the war come, having been asked.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Armistice Losing
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+3)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   ► propose alliance with Prussia
   Directing Talleyrand: modify generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Prussia court with your Full Alliance proposal. Expect a response by next turn. (2 DP spent)
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1272 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► grant Murat a rente
   By Imperial decree, Marshal Murat is granted a rente of 40g/turn upon the treasury. With fees and arrears it will cost the crown 60g/turn — paper is dearer than land, Sire, and it buys no title. It holds his loyalty for exactly as long as it is paid.
   [4/4 actions remaining]
map: unchanged (57 labels)
```

```
#0221  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0221_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 9
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 96 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1766 of 1767 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   11,020
   Inf:
   96,471
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Ney no longer wears the army's laurels alone — Ney and Murat now stand level at its head, and no one wears them.
   Berthier reports that Bernadotte resents Murat's laurels again, 3 turns after the last — he has grown quiet in the way the staff have learned to read.
   Berthier reports that Lannes appears envious of Murat's laurels — he has grown impatient for something worth the doing.
   Davout's resentment of Ney has cooled with time.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Sire — Prussia and France have signed the Defensive Alliance.
   THE LAWS: Russia enacts the Extraordinary Levy — infantry levies cost 20% less (×0.8); infantry drafts muster at -10 morale.
   THE LAWS: Prussia enacts the Emancipation Edict — infantry levies cost 10% less (×0.9).
   An envoy from Britain has arrived with a proposal.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 43.
   Britain's gold reaches Russia — the subsidy stands at 300 this season.
   THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 5 in hand); or let the war come, having been asked.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Britain — Armistice Losing
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+3)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 97/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "The army knows it is winning, Sire. Press the advantage before their line reforms."
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   Responding to Britain's proposal: accepted
   You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain.
   ► propose alliance with Prussia
   Directing Talleyrand: modify generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Prussia court with your Full Alliance proposal. Expect a response by next turn. (2 DP spent)
   ► buy off Austria
   Austria's design — Redeem Italy — is bought off for 1272 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► grant Murat a rente
   By Imperial decree, Marshal Murat is granted a rente of 40g/turn upon the treasury. With fees and arrears it will cost the crown 60g/turn — paper is dearer than land, Sire, and it buys no title. It holds his loyalty for exactly as long as it is paid.
   [4/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 10 BEGINS
   ═══════════════════════════════════════
   Income: 2552g | Subsidies: -200g | Charges of Empire: -458g | Rentes: -60g | Admiralty: -90g | Other: +1332g | Upkeep: -1338g | Net: +1738g | Spent: 1272g
   Treasury: 11,020g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 483 troops
   Supply shortage at Tyrol: Archduke John loses 319 troops
   Holland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   Talleyrand returns from Prussia with excellent news: they have accepted our proposal! The decisive factor was goodwill between our nations.
   Treaty signed: Defensive Alliance → Alliance with Prussia.
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Prussia grows.
   Berthier reports that Davout resents Ney's laurels for the third time — he has grown cold and withholding.
   Davout seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Massena appears envious of Davout's laurels — he has grown restless for glory.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2149,286)  Spain(1185,881)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Britain(1397,292)  Hanover(1726,333)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney(1947,451)  Lannes(1962,425)  Bernadotte(1989,398)  ?(1980,302)  Brunswick(1981,263)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  ?(1759,600)  ?(1743,412)  12k(1697,412)  10k(1923,677)
```

```
#0222  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0222_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 7/7
   Threat 96 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys (2)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Holland @(3351,64)]  [icon: Settlement offer from Britain @(3393,64)]  [icon: Marshal Davout seeks an audience @(3435,64)]  [icon: Napoleon arrived @(3477,64)]  [icon: Bavaria petitions over settlement scope @(3519,64)]  [icon: Settlement Ratified @(3561,64)]  [+20]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Russia
   0
   T:9
   controls: [THIRD COALITION  ▸]  [Russia]  [Britain  4t]
── BottomLeftUI (layer 0) [scrolled 1652 of 1652 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   11,020
   Inf:
   96,471
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Prussia grows.
   Berthier reports that Davout resents Ney's laurels for the third time — he has grown cold and withholding.
   Davout seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Massena appears envious of Davout's laurels — he has grown restless for glory.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 10
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — a truce with Britain is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
   • Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
   SITUATION
   France holds 28 regions. Treasury: 11,020g (+2,238 by the accounts)
   The courts at war hold 10 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 8 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 6 turns idle.
   - Murat — Gascony — 13,348 — Awaiting orders.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 5 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   TURN EVENTS
   Holland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier reports that Davout resents Ney's laurels for the third time — he has grown cold and withholding.
   Davout seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Massena appears envious of Davout's laurels — he has grown restless for glory.
   DIPLOMATIC EVENTS
   Sire — Britain and France have signed the Armistice.
   A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes. Spain stays at war with Britain — an ally, not a client: her war runs on, and no corps of ours stands on Spanish soil.
   Talleyrand has departed for the court of Prussia.
   Britain has offered terms to settle France vs Britain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Holland has arrived with a petition.
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   Sire — France and Prussia have signed the Full Alliance.
   Talleyrand returns from Prussia with a response.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   The court of Austria takes up a new design: Primacy in Germany.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Britain — Settlement Offer
   - Holland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 96/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0223  click Envoys (2)  ->  ok
  (clicked at (3378, 18))
view: <run>\frames\0223_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'mailbox_panel'], region_panel=no
── MailboxPanel (layer 119) ──
   PENDING ENVOYS (2)
   Every envoy still awaiting your answer — diplomacy waiting on your word; ignored, it lapses. Select a row to reopen or activate it.
   ACTIVE
   Britain
   Incoming Settlement Offer
   Open ▸
   Turn 9
   Settlement offer: France vs Britain
   WAITING
   Holland
   Proposal
   Open ▸
   Turn 10
   Incoming proposal: Client's Petition
   controls: {ACTIVE}  {WAITING}  [Close]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1652 of 1652 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 96/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0224  click ACTIVE  ->  ok
  (clicked at (1829, 283))
view: <run>\frames\0224_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm', 'war_status_panel (not modal)'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   SETTLEMENT OFFER FROM BRITAIN /  / France vs Britain /  / "His Majesty's Government offers terms for France vs Britain. No indemnity is asked and none is offered; London proposes only that the guns fall silent." /  / Their proposed terms: /   • Peace /  / Covered enemies: Britain, Russia /  / "Sire, Britain has dispatched a settlement of France vs Britain. No indemnity either way — the war simply  …
   controls: [Review Settlement Offer]  [Request Revision]  [Reject Offer]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1652 of 1652 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   11,020
   Inf:
   96,471
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 96/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
map: unchanged (54 labels)
```

```
#0225  click Review Settlement Offer  ->  ok
  (clicked at (1602, 727))
view: <run>\frames\0225_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   Settlement of France vs Britain + Russia — ready for ratification / France vs Britain + Russia - Whole-war settlement / STAGED FOR REVIEW — the terms are frozen. Ratify, revise, or return to shaping. / Covered enemies: Britain, Russia / Will carry — these are the terms they offered. / Sire, this settlement of France vs Britain + Russia seats 2 courts at the table. Every court at the table will sig …
   The table /   * Britain - Their own terms (11/50) White peace /       Blocker: Settlement legitimacy /       Castlereagh for Britain: these are the terms Britain laid before France; Britain does not haggle with its own dispatch. /   * Russia - Their own terms (11/50) White peace /       Blocker: Settlement legitimacy /       Czartoryski for Russia: these are the terms Russia laid before France; Ru …
   Sire, the white peace for France vs Britain + Russia is ready: no terms exchanged, no map redrawn — only the war ends. Ratify and the field falls quiet. /  / Allies and Standing /   * Britain - Seat at settlement (Defenders, war leader) /   * France - Seat at settlement (Attackers, war leader) /   * Spain - Consulted ally (Attackers) /   * Holland - No settlement standing (Attackers) /   * Russia  …
   controls: [Ratify White Peace]  [Back Out]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 96 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1674 of 1674 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   11,020
   Inf:
   96,471
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: accept settlement offer
map: unchanged (54 labels)
```

```
#0226  click Ratify White Peace  ->  ok
  (clicked at (1457, 912))
view: <run>\frames\0226_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=['diplomatic_ledger'], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Schimmelpenninck (Loyalist) of Holland /  / The petition: /   - Grant it, and Holland's tribute of 337g a turn is remitted for 8 collections (2696g forgone): loyalty +2 (to the 100 ceiling), its bond with us rises 0 → 20 (worth +1 a turn in loyalty, now +0), for 1 DP. /   - Refuse it, and Holland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loya …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 48 / 100
   Turn 10 — Early February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── DiplomaticLedger (layer 50) [under a modal] [scrolled 0 of 1916 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 7/7
   ═══ ACTIVE TREATIES ═══ /  / Sweden ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (8 turns ago) /  / Naples ↔ Russia: Open Borders /   Clauses: None /   Duration: permanent   Cancel cost: 1 DP /   Signed: Turn 2 (8 turns ago) /  / France ↔ Prussia: Alliance /   Clauses: Gold payment: 500 (France -> Prussia) /   Duration: permanent   Cancel  …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES](disabled: You are reading this book)  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <v Settlement of France vs Britain + Russia: settlement ratified.>  <v Settlement of France vs Austria: Gold indemnity: 400 gold from France to Austria.>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1828 of 1828 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   11,020
   Inf:
   96,471
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: confirm settlement
   Settlement Ratified: France vs Britain + Russia (4 pairs resolved).
   Settlement Ratified
   4 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
map: unchanged (54 labels)
```

```
#0227  click Grant  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0227_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 6/7
   Threat 48 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified (x2) @(3216,64)]  [icon: Marshal Davout seeks an audience @(3258,64)]  [icon: Napoleon arrived @(3300,64)]  [icon: Bavaria petitions over settlement scope @(3342,64)]  [icon: The Moniteur is out (x2) @(3384,64)]  [Talleyrand at Prussia — Courting]  [Recall]
── DiplomaticLedger (layer 50) [scrolled 0 of 1916 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1895 of 1895 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   11,020
   Inf:
   96,471
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (54 labels)
```

```
#0228  click CONGRESS  ->  ok
  (clicked at (2098, 273))
view: <run>\frames\0228_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 640 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 7/7
   ═══ THE CONGRESS OF PARIS ═══ / Europe must RECOGNIZE the new order. With 45 titled provinces the Emperor may summon the great powers to Paris; each answers at every end turn, with its reason and its price, and the Congress sits 8 turns. If on the last day every court recognizes, is shut out or is gone, and the hold never broke, the Imperial Peace is proclaimed. /  / THE CONGRESS OF PARIS — 38 of  …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS](disabled: You are reading this book)  <Open the Cabinet at London →>  <Open the Cabinet at St Petersburg →>  <Open the Cabinet at Vienna →>  <Open the Cabinet at Berlin →>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1895 of 1895 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (54 labels)
```

```
#0229  scroll 1825 600 down 10  ->  ok
  (scrolled down 10 at (1825, 600))
view: <run>\frames\0229_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 617 of 641 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 7/7
   ═══ THE CONGRESS OF PARIS ═══ / Europe must RECOGNIZE the new order. With 45 titled provinces the Emperor may summon the great powers to Paris; each answers at every end turn, with its reason and its price, and the Congress sits 8 turns. If on the last day every court recognizes, is shut out or is gone, and the hold never broke, the Imperial Peace is proclaimed. /  / THE CONGRESS OF PARIS — 38 of  …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS](disabled: You are reading this book)  <Open the Cabinet at London →>  <Open the Cabinet at St Petersburg →>  <Open the Cabinet at Vienna →>  <Open the Cabinet at Berlin →>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1895 of 1895 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (54 labels)
```

```
#0230  scroll 1825 600 up 3  ->  ok
  (scrolled up 3 at (1825, 600))
view: <run>\frames\0230_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 419 of 641 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 7/7
   ═══ THE CONGRESS OF PARIS ═══ / Europe must RECOGNIZE the new order. With 45 titled provinces the Emperor may summon the great powers to Paris; each answers at every end turn, with its reason and its price, and the Congress sits 8 turns. If on the last day every court recognizes, is shut out or is gone, and the hold never broke, the Imperial Peace is proclaimed. /  / THE CONGRESS OF PARIS — 38 of  …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS](disabled: You are reading this book)  <Open the Cabinet at London →>  <Open the Cabinet at St Petersburg →>  <Open the Cabinet at Vienna →>  <Open the Cabinet at Berlin →>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1895 of 1895 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (54 labels)
```

```
#0231  click Open the Cabinet at Vienna →  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0231_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 46 px, 0 of 392 px] ──
   DIPLOMACY — Austria
   DP: 6
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -69 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus.
   Their design is aimed at France herself.
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1128g) (1 DP + 1128g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Open Borders (1 DP)  —  Hopeless](disabled: Relations with Austria stand at -69; an Open Borders needs -20.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1895 of 1895 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (54 labels)
```

```
#0232  scroll 1825 600 down 5  ->  ok
  (scrolled down 5 at (1825, 600))
view: <run>\frames\0232_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 44 px, 188 of 401 px] ──
   DIPLOMACY — Austria
   DP: 6
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -69 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus.
   Relations with Austria stand at -69; an Open Borders needs -20.
   Mission already active
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Open Borders (1 DP)  —  Hopeless](disabled: Relations with Austria stand at -69; an Open Borders needs -20.)  [Declare War (1 DP)]  [Send Ultimatum (2 DP)]  [Improve Relations (1 DP)  —  +8 relation/turn](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1895 of 1895 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (54 labels)
```

```
#0233  scroll 1825 600 up 5  ->  ok
  (scrolled up 5 at (1825, 600))
view: <run>\frames\0233_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 46 px, 0 of 392 px] ──
   DIPLOMACY — Austria
   DP: 6
   TALLEYRAND'S ASSESSMENT — AUSTRIA / Status: Peace   Relation: -69 (Hostile) /  / "Relations with Austria remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus.
   Their design is aimed at France herself.
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1128g) (1 DP + 1128g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Open Borders (1 DP)  —  Hopeless](disabled: Relations with Austria stand at -69; an Open Borders needs -20.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1895 of 1895 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
map: unchanged (54 labels)
```

```
#0234  click Buy Off Their Design (1128g)  ->  ok
  (clicked at (1825, 540))
view: <run>\frames\0234_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 48 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified (x2) @(3216,64)]  [icon: Marshal Davout seeks an audience @(3258,64)]  [icon: Napoleon arrived @(3300,64)]  [icon: Bavaria petitions over settlement scope @(3342,64)]  [icon: The Moniteur is out (x2) @(3384,64)]  [Talleyrand at Prussia — Courting]  [Recall]
── BottomLeftUI (layer 0) [scrolled 2005 of 2005 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   9,892
   Inf:
   96,471
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► buy off Austria
   Austria's design — Primacy in Germany — is bought off for 1128 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (54 labels)
```

```
#0235  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0235_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   Treaties (8)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action; and while it sits, from this end turn, your](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Prussia  —  Alliance  |  +43 (Friendly)  [MISSION]]  [Spain  —  Alliance  |  +31 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -11 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► buy off Austria
   Austria's design — Primacy in Germany — is bought off for 1128 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (54 labels)
```

```
#0236  scroll 1825 600 down 15  ->  ok
  (scrolled down 15 at (1825, 600))
view: <run>\frames\0236_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 624 of 664 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (7)
   controls: [icon: Close (Esc) @(2075,284)]  [Switzerland  —  Vassal  |  +20 (Neutral)]  [Britain  —  Peace  |  -87 (Hostile)]  [Russia  —  Peace  |  -80 (Hostile)]  [Austria  —  Peace  |  -64 (Hostile)]  [Sweden  —  Peace  |  -46 (Hostile)]  [Naples  —  Peace  |  -21 (Wary)]  [Hanover  —  Peace  |  -41 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► buy off Austria
   Austria's design — Primacy in Germany — is bought off for 1128 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (54 labels)
```

```
#0237  click Britain  —  Peace  ->  ok
  (clicked at (1825, 443))
view: <run>\frames\0237_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 46 px, 0 of 415 px] ──
   DIPLOMACY — Britain
   DP: 5
   TALLEYRAND'S ASSESSMENT — BRITAIN / Status: Peace   Relation: -87 (Hostile) /  / "Relations with Britain remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus.
   Their design is aimed at France herself.
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Fund the design they already pursue against us — a bribe, not a purch](disabled: Their design is aimed at France herself.)  [Buy Off Their Design (1116g) (1 DP + 1116g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Open Borders (1 DP)  —  Hopeless](disabled: Relations with Britain stand at -87; an Open Borders needs -20.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2005 of 2005 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► buy off Austria
   Austria's design — Primacy in Germany — is bought off for 1128 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (54 labels)
```

```
#0238  click Buy Off Their Design (1116g)  ->  ok
  (clicked at (1825, 540))
view: <run>\frames\0238_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 48 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified (x2) @(3216,64)]  [icon: Marshal Davout seeks an audience @(3258,64)]  [icon: Napoleon arrived @(3300,64)]  [icon: Bavaria petitions over settlement scope @(3342,64)]  [icon: The Moniteur is out (x2) @(3384,64)]  [Talleyrand at Prussia — Courting]  [Recall]
── BottomLeftUI (layer 0) [scrolled 2115 of 2115 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,776
   Inf:
   96,471
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (54 labels)
```

```
#0239  click Talleyrand: Courting → Prussia  ->  ok
  (clicked at (3219, 18))
view: <run>\frames\0239_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 222 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 4/7
   THE LEAGUE IS SPENT / The courts are recovering from the last coalition. Cooldown: 5 turns. Europe's alarm stands at 48; no new coalition gathers below 60. /  / TALLEYRAND — Divine Right / Authority: 100/100   Skill: 10   DP: 4/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Pruss …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2115 of 2115 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Austria
   Austria's design — Primacy in Germany — is bought off for 1128 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (54 labels)
```

```
#0240  scroll 1825 600 down 5  ->  ok
  (scrolled down 5 at (1825, 600))
view: <run>\frames\0240_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 198 of 222 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 4/7
   THE LEAGUE IS SPENT / The courts are recovering from the last coalition. Cooldown: 5 turns. Europe's alarm stands at 48; no new coalition gathers below 60. /  / TALLEYRAND — Divine Right / Authority: 100/100   Skill: 10   DP: 4/7 /   (Base 3 + Skill +1 + Authority +1) /  /     Assess the Situation    his full survey of the war, the treasury, and the courts /  / CURRENT MISSION /   Courting → Pruss …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND](disabled: You are reading this book)  [WAR BARGAINS]  [VASSALS]  [CONGRESS]  <Assess the Situation>
── BottomLeftUI (layer 0) [under a modal] [scrolled 2115 of 2115 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Austria
   Austria's design — Primacy in Germany — is bought off for 1128 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (54 labels)
```

```
#0241  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0241_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 646 px] ──
   DIPLOMACY
   DP: 4
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   Treaties (8)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action; and while it sits, from this end turn, your](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Prussia  —  Alliance  |  +43 (Friendly)  [MISSION]]  [Spain  —  Alliance  |  +31 (Friendly)]  [Ottoman Empire  —  Open Borders  |  -11 (Wary)]  [Portugal  —  Open Borders  |  -10 (Wary)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2115 of 2115 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Austria
   Austria's design — Primacy in Germany — is bought off for 1128 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (54 labels)
```

```
#0242  click Spain  —  Alliance  ->  ok
  (clicked at (1825, 581))
view: <run>\frames\0242_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 111 px, 0 of 459 px] ──
   DIPLOMACY — Spain
   DP: 4
   TALLEYRAND'S ASSESSMENT — SPAIN / Status: Alliance   Relation: +31 (Friendly) /  / "Our alliance with Spain holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus. /  / "We must exercise patience, Sire. Cooldown: 2 turns before we may approach the …
   Cooldown: 2 turns
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Vassal (3 DP)](disabled: Cooldown: 2 turns)  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Downgrade (1 DP)]  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2115 of 2115 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Austria
   Austria's design — Primacy in Germany — is bought off for 1128 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (54 labels)
```

```
#0243  click Cancel  ->  ok
  (clicked at (1884, 740))
view: <run>\frames\0243_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 2115 of 2115 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► buy off Austria
   Austria's design — Primacy in Germany — is bought off for 1128 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (54 labels)
```

```
#0244  click Marshal Davout seeks an audience  ->  ok
  (clicked at (3258, 64))
view: <run>\frames\0244_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: ''
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 48 / 100
   Turn 10 — Early February 1806
   Imperial Box
   Marshal Davout seeks an audience
   Davout asks to be heard — at your leisure, Sire; nothing waits on it. His card is on the Generals screen.
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified (x2) @(3216,64)]  [icon: Marshal Davout seeks an audience @(3258,64)]  [icon: Napoleon arrived @(3300,64)]  [icon: Bavaria petitions over settlement scope @(3342,64)]  [icon: The Moniteur is out (x2) @(3384,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [Hear him]  [Keep]
── BottomLeftUI (layer 0) [scrolled 2115 of 2115 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   ► buy off Austria
   Austria's design — Primacy in Germany — is bought off for 1128 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (54 labels)
```

```
#0245  click Hear him  ->  ok
  (clicked at (3595, 221))
view: <run>\frames\0245_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['marshal_petition'], region_panel=no
── MarshalPetitionDialog (layer 114) [scrolled 0 of 69 px] ──
   DAVOUT — Marshal Davout seeks an audience
   Give him a command is closed — There is no enemy within his reach to send him against.
   "I have said my piece before. I will not say it a third time unless you wish it." /  / Sire, Davout observes — without complaint, he is careful to say — that Ney's name reaches you before his own. The staff now speak of the quarrel openly — this is no longer a passing mood.
   Free, and it fixes nothing. For 3 more turns he brings about half the weight of his 17,079 men to any battle Ney leads, and the quarrel may harden further.
   His patience is bought — the grievance shortens by 2 turns, and for 6 turns the quarrel cannot harden further.
   controls: [Let it stand   [Free]]  [Promise Glory   [1 AP]]  [Rebuke]  [Later (he will return)]
── TopBar (layer 75) [under a modal] ──
   DP: 4/7
   Threat 48 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified (x2) @(3216,64)]  [icon: Marshal Davout seeks an audience @(3258,64)]  [icon: Napoleon arrived @(3300,64)]  [icon: Bavaria petitions over settlement scope @(3342,64)]  [icon: The Moniteur is out (x2) @(3384,64)]  [Talleyrand at Prussia — Courting]  [Recall]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2115 of 2115 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,776
   Inf:
   96,471
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ► buy off Austria
   Austria's design — Primacy in Germany — is bought off for 1128 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (54 labels)
```

```
#0246  click Promise Glory  ->  ok
  (clicked at (1825, 597))
view: <run>\frames\0246_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 10 — Early February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 48 / 100
   Turn 10 — Early February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Settlement Ratified (x2) @(3216,64)]  [icon: Napoleon arrived @(3258,64)]  [icon: Bavaria petitions over settlement scope @(3300,64)]  [icon: The Moniteur is out (x2) @(3342,64)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Treaty with Prussia @(3649,64)]
── BottomLeftUI (layer 0) [scrolled 2160 of 2160 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   10
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   8,776
   Inf:
   96,471
   Cav:
   30,000
   Art:
   15,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Davout bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
map: unchanged (54 labels)
```

```
#0247  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0247_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 10
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 46 / 100
   Turn 11 — Late February 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2139 of 2140 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,960
   Inf:
   98,971
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 5 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   TURN EVENTS
   Holland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Berthier reports that Davout resents Ney's laurels for the third time — he has grown cold and withholding.
   Davout seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Massena appears envious of Davout's laurels — he has grown restless for glory.
   DIPLOMATIC EVENTS
   Sire — Britain and France have signed the Armistice.
   A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes. Spain stays at war with Britain — an ally, not a client: her war runs on, and no corps of ours stands on Spanish soil.
   Talleyrand has departed for the court of Prussia.
   Britain has offered terms to settle France vs Britain.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   An envoy from Holland has arrived with a petition.
   Dumonceau's contingent comes home — 6,500 of 6,500 men.
   Sire — France and Prussia have signed the Full Alliance.
   Talleyrand returns from Prussia with a response.
   Prussia delivers a final demand to Hanover — it is refused. The ladder has one rung left.
   The blockade of France is broken — her ports breathe, her crews may drill again.
   The blockade of Holland is broken — her ports breathe, her crews may drill again.
   THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
   THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
   THE STRAIT: the London–Normandy crossing stands open to our armies.
   The court of Austria takes up a new design: Primacy in Germany.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 2 envoys await your reply this turn. Open Envoys before ending the turn.
   - Britain — Settlement Offer
   - Holland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Britain — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   War Purpose: Defense vs Russia — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 96/100 [Formed]
   ACTIVE: Third Coalition — Leader: Britain
   Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over."
   ════════════════════════════════════
   Directing Talleyrand: accept settlement offer
   Directing Talleyrand: confirm settlement
   Settlement Ratified: France vs Britain + Russia (4 pairs resolved).
   Settlement Ratified
   4 hostile pairs resolved. Review the settlement in the diplomatic ledger.
   Covered pairings: 4
   Opening diplomatic ledger to settlement…
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP.
   ► buy off Austria
   Austria's design — Primacy in Germany — is bought off for 1128 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► buy off Britain
   Britain's design — The Low Countries — is bought off for 1116 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   Davout bows. "I will hold you to it, Sire." His grievance shortens, and while your word stands the quarrel will go no further.
   ► end turn
   ═══════════════════════════════════════
   TURN 11 BEGINS
   ═══════════════════════════════════════
   Income: 2557g | Subsidies: -200g | Charges of Empire: -216g | Rentes: -60g | Admiralty: -90g | Other: +1531g | Upkeep: -1338g | Net: +2184g | Spent: 2244g
   Treasury: 10,960g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 561 troops
   Supply shortage at Tyrol: Archduke John loses 332 troops
   Prussia declares war on Hanover — The Hanoverian Prize.
   Ottoman buys off Austria's design for 1,272 gold.
   Davout's grievance is satisfied — he has surpassed Ney in glory. He holds with renewed purpose (+10% defense this turn).
   Berthier reports that Davout appears envious of Murat's laurels — he has grown cold and withholding. He asked for an audience on turn 9, and will not ask again before turn 15.
   Berthier notes that Murat's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2149,286)  Spain(1185,881)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Britain(1397,292)  Hanover(1726,333)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney(1947,451)  Lannes(1962,425)  Bernadotte(1989,398)  ?(1971,302)  Brunswick(1972,263)  ?(2000,302)  Yorck(1990,236)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  ?(1759,600)  ?(1743,412)  12k(1697,412)  10k(1923,677)
```

```
#0248  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0248_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 46 / 100
   Turn 11 — Late February 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: European Courts Concerned @(3351,64)]  [icon: France Joins Offensive! @(3393,64)]  [icon: Prussia Declares War! @(3435,64)]  [icon: Settlement Ratified (x2) @(3477,64)]  [icon: Napoleon arrived @(3519,64)]  [icon: Bavaria petitions over settlement scope @(3561,64)]  [+24]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Hanover
   0
   T:0
   controls: [Hanover]
── BottomLeftUI (layer 0) [scrolled 1897 of 1897 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,960
   Inf:
   98,971
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► end turn
   ═══════════════════════════════════════
   TURN 11 BEGINS
   ═══════════════════════════════════════
   Income: 2557g | Subsidies: -200g | Charges of Empire: -216g | Rentes: -60g | Admiralty: -90g | Other: +1531g | Upkeep: -1338g | Net: +2184g | Spent: 2244g
   Treasury: 10,960g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 561 troops
   Supply shortage at Tyrol: Archduke John loses 332 troops
   Prussia declares war on Hanover — The Hanoverian Prize.
   Ottoman buys off Austria's design for 1,272 gold.
   Davout's grievance is satisfied — he has surpassed Ney in glory. He holds with renewed purpose (+10% defense this turn).
   Berthier reports that Davout appears envious of Murat's laurels — he has grown cold and withholding. He asked for an audience on turn 9, and will not ask again before turn 15.
   Berthier notes that Murat's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   ════════════════════════════════════
   MORNING DISPATCH — Turn 11
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — our peace binds Britain for 4 more turns and Russia for 4 more turns; then each may join a league (relations −81 and −79).
   • Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
   • Sire — Austria moves toward war with Ottoman Empire. The design is open; the timing is not.
   SITUATION
   France holds 28 regions. Treasury: 10,960g (+2,184 by the accounts)
   The courts at war hold 6 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 9 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 7 turns idle.
   - Murat — Gascony — 13,348 — Awaiting orders.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 6 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Yorck — Berlin — small force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   TURN EVENTS
   Davout's grievance is satisfied — he has surpassed Ney in glory. He holds with renewed purpose (+10% defense this turn).
   Berthier reports that Davout appears envious of Murat's laurels — he has grown cold and withholding. He asked for an audience on turn 9, and will not ask again before turn 15.
   Berthier notes that Murat's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   The coalition against France has dissolved — but Hanover remains at war with us.
   Settlement of France vs Britain + Russia: settlement ratified.
   Intelligence reports Prussia has raised Yorck to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 51.
   France has joined Prussia's war against Hanover, honoring their alliance.
   Prussia has declared war on Hanover, with 1 allied court poised to follow.
   THE BREWING CRISIS: Austria will move on Ottoman. You may compensate (1,272g — you can afford it); guarantee Ottoman (1 DP — 5 in hand); or let the war come, having been asked.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   The court of Russia takes up a new design: The Gulf and the Straits.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   Relations with Hanover have worsened significantly (-19 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A peace binds only while its ink is wet, Sire. Use the turns it gives."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0249  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0249_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   At War (1)
   Treaties (8)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action; and while it sits, from this end turn, your](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Hanover  —  At War  |  -60 (Hostile)]  [Prussia  —  Alliance  |  +36 (Friendly)  [MISSION]]  [Spain  —  Alliance  |  +30 (Friendly)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1897 of 1897 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A peace binds only while its ink is wet, Sire. Use the turns it gives."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0250  click Hanover  —  At War  ->  ok
  (clicked at (1825, 541))
view: <run>\frames\0250_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 200 px, 0 of 324 px] ──
   DIPLOMACY — Hanover
   DP: 5
   TALLEYRAND'S ASSESSMENT — HANOVER / Status: At War   Relation: -60 (Hostile) /  / "The war with Hanover grinds on without decisive result. Both sides bleed. An armistice may find receptive ears." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus. /  / KEY FACTORS /   + Base willingness (+20) /   + Diplomatic skill advant …
   Only the war leader can settle this side.
   Only the war leader can settle this side.
   Mission already active
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Armistice (1 DP)  —  Unlikely]  [Open Settlement](disabled: Only the war leader can settle this side.)  [Propose White Peace](disabled: Only the war leader can settle this side.)  [Gather Intel (1 DP)  —  3 turns, then full intel for 5](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1897 of 1897 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A peace binds only while its ink is wet, Sire. Use the turns it gives."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0251  click Cancel  ->  ok
  (clicked at (1884, 739))
view: <run>\frames\0251_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1897 of 1897 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A peace binds only while its ink is wet, Sire. Use the turns it gives."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0252  type which Hanoverian province can Soult reach from Rhineland?  ->  ok
  (typed and Enter)
view: <run>\frames\0252_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: ok Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."

What I CAN do today:
  Ney, march to Dresden
  Davout, fortify
  recruit infantry in Rhineland — 680g for 3,000 men under Soult
  build supply depot in Rhineland — 300g

For any matter of state, press F1 for the Cabinet.
Type 'help' for the full command reference.
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2183 of 2183 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,960
   Inf:
   98,971
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► which Hanoverian province can Soult reach from Rhineland?
   Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
   What I CAN do today:
   Ney, march to Dresden
   Davout, fortify
   recruit infantry in Rhineland — 680g for 3,000 men under Soult
   build supply depot in Rhineland — 300g
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
map: unchanged (56 labels)
```

```
#0253  type Soult, attack Hanover  ->  ok
  (typed and Enter)
view: <run>\frames\0253_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 11 — Late February 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
reply: Soult cannot reach Hanover from Rhineland! Range: 1, Distance: 3
No enemies within range. Try 'move to Hanover' to get closer first
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 2295 of 2295 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   11
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   10,960
   Inf:
   98,971
   Cav:
   30,000
   Art:
   16,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► Soult, attack Hanover
   Soult cannot reach Hanover from Rhineland! Range: 1, Distance: 3
   No enemies within range. Try 'move to Hanover' to get closer first
map: unchanged (56 labels)
```

```
#0254  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0254_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2116 of 2118 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,061
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Sire — our peace binds Britain for 4 more turns and Russia for 4 more turns; then each may join a league (relations −81 and −79).
   • Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
   • Sire — Austria moves toward war with Ottoman Empire. The design is open; the timing is not.
   SITUATION
   France holds 28 regions. Treasury: 10,960g (+2,184 by the accounts)
   The courts at war hold 6 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 9 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 7 turns idle.
   - Murat — Gascony — 13,348 — Awaiting orders.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 6 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Berlin — large force [partial]
   Yorck — Berlin — small force [partial]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   TURN EVENTS
   Davout's grievance is satisfied — he has surpassed Ney in glory. He holds with renewed purpose (+10% defense this turn).
   Berthier reports that Davout appears envious of Murat's laurels — he has grown cold and withholding. He asked for an audience on turn 9, and will not ask again before turn 15.
   Berthier notes that Murat's recent victories have made him the most celebrated commander in the army. (+1 shock, +1 defense, +1 administration while he holds the laurels)
   DIPLOMATIC EVENTS
   The coalition against France has dissolved — but Hanover remains at war with us.
   Settlement of France vs Britain + Russia: settlement ratified.
   Intelligence reports Prussia has raised Yorck to high command.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 51.
   France has joined Prussia's war against Hanover, honoring their alliance.
   Prussia has declared war on Hanover, with 1 allied court poised to follow.
   THE BREWING CRISIS: Austria will move on Ottoman. You may compensate (1,272g — you can afford it); guarantee Ottoman (1 DP — 5 in hand); or let the war come, having been asked.
   The blockade of Spain is broken — her ports breathe, her crews may drill again.
   The court of Russia takes up a new design: The Gulf and the Straits.
   The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
   Relations with Hanover have worsened significantly (-19 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A peace binds only while its ink is wet, Sire. Use the turns it gives."
   ════════════════════════════════════
   ► which Hanoverian province can Soult reach from Rhineland?
   Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
   What I CAN do today:
   Ney, march to Dresden
   Davout, fortify
   recruit infantry in Rhineland — 680g for 3,000 men under Soult
   build supply depot in Rhineland — 300g
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
   ► Soult, attack Hanover
   Soult cannot reach Hanover from Rhineland! Range: 1, Distance: 3
   No enemies within range. Try 'move to Hanover' to get closer first
   ► end turn
   ═══════════════════════════════════════
   TURN 12 BEGINS
   ═══════════════════════════════════════
   Income: 2562g | Subsidies: -200g | Charges of Empire: -315g | Rentes: -60g | Admiralty: -90g | Other: +1542g | Upkeep: -1338g | Net: +2101g
   Treasury: 13,061g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 537 troops
   Supply shortage at Tyrol: Archduke John loses 318 troops
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Sweden grows.
   Massena's resentment of Davout has cooled with time.
   Berthier notes that Massena has grown restless — he has not seen laurels while Davout wins them. I recommend giving him meaningful orders soon.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2116,290)  Spain(1185,881)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Britain(1397,292)  Naples(1802,904)  Hanover(1690,318)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney(1947,451)  Lannes(1962,425)  Bernadotte(1989,398)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  ?(1822,292)  Brunswick(1823,252)  ?(1851,292)  Yorck(1840,225)  Murat(1445,622)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  ?(1759,600)  ?(1743,412)  12k(1697,412)  10k(1923,677)
```

```
#0255  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0255_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: European Courts Concerned @(3351,64)]  [icon: France Joins Offensive! @(3393,64)]  [icon: Prussia Declares War! @(3435,64)]  [icon: Settlement Ratified (x2) @(3477,64)]  [icon: Napoleon arrived @(3519,64)]  [icon: Bavaria petitions over settlement scope @(3561,64)]  [+24]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Hanover
   0
   T:1
   controls: [Hanover]
── BottomLeftUI (layer 0) [scrolled 2231 of 2231 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,061
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   COALITION THREAT
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A peace binds only while its ink is wet, Sire. Use the turns it gives."
   ════════════════════════════════════
   ► which Hanoverian province can Soult reach from Rhineland?
   Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
   What I CAN do today:
   Ney, march to Dresden
   Davout, fortify
   recruit infantry in Rhineland — 680g for 3,000 men under Soult
   build supply depot in Rhineland — 300g
   For any matter of state, press F1 for the Cabinet.
   Type 'help' for the full command reference.
   ► Soult, attack Hanover
   Soult cannot reach Hanover from Rhineland! Range: 1, Distance: 3
   No enemies within range. Try 'move to Hanover' to get closer first
   ► end turn
   ═══════════════════════════════════════
   TURN 12 BEGINS
   ═══════════════════════════════════════
   Income: 2562g | Subsidies: -200g | Charges of Empire: -315g | Rentes: -60g | Admiralty: -90g | Other: +1542g | Upkeep: -1338g | Net: +2101g
   Treasury: 13,061g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 537 troops
   Supply shortage at Tyrol: Archduke John loses 318 troops
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Sweden grows.
   Massena's resentment of Davout has cooled with time.
   Berthier notes that Massena has grown restless — he has not seen laurels while Davout wins them. I recommend giving him meaningful orders soon.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 12
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
   • Sire — Austria moves toward war with Ottoman Empire. The design is open; the timing is not.
   • Sire — Austria stands down over Ottoman Empire; the design was bought off, and the bargain stands.
   SITUATION
   France holds 28 regions. Treasury: 13,061g (+2,101 by the accounts)
   The courts at war hold 5 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 10 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 8 turns idle.
   - Murat — Gascony — 13,348 — 3 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 7 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   TURN EVENTS
   Massena's resentment of Davout has cooled with time.
   Berthier notes that Massena has grown restless — he has not seen laurels while Davout wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LAWS: Austria enacts the Corps d'Armée — +1 order of the day, from the next refill; cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Austria brings the Corps d'Armée into force beside its Staff — The Hofkriegsrat is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Talleyrand's efforts in Prussia continue. Relations now at 44.
   Austria stands down over Ottoman, Sire — the design was bought off — compensation stands.
   THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,200g — you can afford it); guarantee Sweden (1 DP — 5 in hand); or let the war come, having been asked.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0256  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0256_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   DIPLOMACY
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   At War (1)
   Treaties (8)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action; and while it sits, from this end turn, your](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Hanover  —  At War  |  -60 (Hostile)]  [Prussia  —  Alliance  |  +44 (Friendly)  [MISSION]]  [Spain  —  Alliance  |  +29 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2231 of 2231 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0257  click Spain  —  Alliance  ->  ok
  (clicked at (1825, 644))
view: <run>\frames\0257_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 156 px, 0 of 416 px] ──
   DIPLOMACY — Spain
   DP: 5
   TALLEYRAND'S ASSESSMENT — SPAIN / Status: Alliance   Relation: +29 (Neutral) /  / "Our alliance with Spain holds, but the bond frays. Tread carefully — a break now would cost us dearly." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus. /  / KEY FACTORS /   + Current relations (+14) /   + Base willingness (+10) /   + Di …
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Vassal (3 DP)  —  Doubtful — may counter]  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Downgrade (1 DP)]  [Reassure Ally (1 DP)  —  +4 relation/turn](disabled: Mission already active)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2231 of 2231 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
map: unchanged (56 labels)
```

```
#0258  click Propose Vassal (3 DP)  ->  ok
  (clicked at (1825, 459))
view: <run>\frames\0258_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Spain /  / France demands: /   • Spain pays 779 gold per turn to France /  / Harshness: Very High / Acceptance estimate: ~0% (REJECT) / Key obstacle: the harshness of current demands / DP cost: 3 /  / "Sire, I must counsel caution. Demanding too much from Spain may ensure they never forgive us."
   controls: [icon: Close (Esc) @(2151,292)]  [Send my terms as ordered]  [Use Talleyrand's suggestion]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 12 — Early March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2275 of 2275 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,061
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose vassalization to Spain
map: unchanged (56 labels)
```

```
#0259  click Not Now  ->  ok
  (clicked at (2056, 727))
view: <run>\frames\0259_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['talleyrand_objection'], region_panel=no
── TalleyrandObjectionPopup (layer 113) [scrolled 0 of 39 px] ──
   TALLEYRAND OBJECTS / MODERATE /  / "Sire, I must counsel caution. Demanding too much from Spain may ensure they never forgive us." /  / Proposed terms: /   • Vassalage (Spain becomes a subject state) /   • Spain pays 779 gold/turn /  / Acceptance estimate: ~0% (Reject) / Defiance Risk: Medium / Regarding: Vassalage with Spain
   controls: [Proceed Anyway]  [Modify Proposal]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2296 of 2296 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,061
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: reconsider
map: unchanged (56 labels)
```

```
#0260  click Cancel  ->  ok
  (clicked at (1989, 647))
view: <run>\frames\0260_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 12 — Early March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 12 — Early March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: European Courts Concerned @(3351,64)]  [icon: France Joins Offensive! @(3393,64)]  [icon: Prussia Declares War! @(3435,64)]  [icon: Settlement Ratified (x2) @(3477,64)]  [icon: Napoleon arrived @(3519,64)]  [icon: Bavaria petitions over settlement scope @(3561,64)]  [+24]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Hanover
   0
   T:1
   controls: [Hanover]
── BottomLeftUI (layer 0) [scrolled 2362 of 2362 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   12
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   13,061
   Inf:
   100,000
   Cav:
   30,000
   Art:
   16,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Proposal cancelled.
   Very well, Sire. The matter is set aside.
map: unchanged (56 labels)
```

```
#0261  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0261_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 12
   PRUSSIA / ──────────────────────────── / - Brunswick attacks Hanover /     Assault on the garrison of Hanover /       Garrison: 5,000 lost, 5,000 still under arms /       The assault cost them 2,338. / - Brunswick attacks Hanover /     Region captured: Hanover (was Hanover) (secured) /  / ──────────────────────────── / Britain, Russia, Austria and 5 other courts stirred as well, but their formatio …
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 13 — Late March 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2074 of 2075 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   15,070
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 537 troops
   Supply shortage at Tyrol: Archduke John loses 318 troops
   Territorial rivalry between Russia and Austria grows.
   Territorial rivalry between Russia and Sweden grows.
   Massena's resentment of Davout has cooled with time.
   Berthier notes that Massena has grown restless — he has not seen laurels while Davout wins them. I recommend giving him meaningful orders soon.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 12
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
   • Sire — Austria moves toward war with Ottoman Empire. The design is open; the timing is not.
   • Sire — Austria stands down over Ottoman Empire; the design was bought off, and the bargain stands.
   SITUATION
   France holds 28 regions. Treasury: 13,061g (+2,101 by the accounts)
   The courts at war hold 5 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 10 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 8 turns idle.
   - Murat — Gascony — 13,348 — 3 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 7 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   TURN EVENTS
   Massena's resentment of Davout has cooled with time.
   Berthier notes that Massena has grown restless — he has not seen laurels while Davout wins them. I recommend giving him meaningful orders soon.
   DIPLOMATIC EVENTS
   THE LAWS: Austria enacts the Corps d'Armée — +1 order of the day, from the next refill; cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands.
   THE DOCTRINES: Austria brings the Corps d'Armée into force beside its Staff — The Hofkriegsrat is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Emperor has taken the field — Talleyrand holds the portfolio at the capital.
   Talleyrand's efforts in Prussia continue. Relations now at 44.
   Austria stands down over Ottoman, Sire — the design was bought off — compensation stands.
   THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,200g — you can afford it); guarantee Sweden (1 DP — 5 in hand); or let the war come, having been asked.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
   ► propose vassalization to Spain
   Directing Talleyrand: reconsider
   Proposal cancelled.
   Very well, Sire. The matter is set aside.
   ► end turn
   ═══════════════════════════════════════
   TURN 13 BEGINS
   ═══════════════════════════════════════
   Income: 2567g | Subsidies: -200g | Charges of Empire: -424g | Rentes: -60g | Admiralty: -90g | Other: +1554g | Upkeep: -1338g | Net: +2009g
   Treasury: 15,070g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 515 troops
   Supply shortage at Tyrol: Archduke John loses 305 troops
   Garrison at Hanover reinforced: 0 -> 2,000
   Diplomatic blowback! Prussia discovered our scheming. (-3 relation)
   Territorial rivalry between Austria and Ottoman grows.
   Berthier reports that Massena appears envious of Murat's laurels — he has grown loud at the staff table about who is given the honours.
   Massena seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Ney appears envious of Murat's laurels — he has grown restless for glory.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2105,289)  Spain(1185,881)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Britain(1397,292)  Naples(1802,904)  Hanover(1669,327)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney(1947,451)  Lannes(1962,425)  Bernadotte(1989,398)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  ?(1831,292)  Yorck(1846,252)  Murat(1445,622)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  Brunswick(1769,250)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  2k(1769,315)  ?(1743,412)  12k(1697,412)  10k(1923,677)
```

```
#0262  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0262_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 13 — Late March 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 13 — Late March 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Marshal Massena seeks an audience @(3492,64)]  [icon: European Courts Concerned @(3534,64)]  [icon: France Joins Offensive! @(3576,64)]  [icon: Prussia Declares War! @(3618,64)]  [icon: Settlement Ratified (x2) @(3649,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Hanover
   0
   T:2
   controls: [Hanover]
── BottomLeftUI (layer 0) [scrolled 2208 of 2208 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   13
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   15,070
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Austria stands down over Ottoman, Sire — the design was bought off — compensation stands.
   THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,200g — you can afford it); guarantee Sweden (1 DP — 5 in hand); or let the war come, having been asked.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 4 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
   ► propose vassalization to Spain
   Directing Talleyrand: reconsider
   Proposal cancelled.
   Very well, Sire. The matter is set aside.
   ► end turn
   ═══════════════════════════════════════
   TURN 13 BEGINS
   ═══════════════════════════════════════
   Income: 2567g | Subsidies: -200g | Charges of Empire: -424g | Rentes: -60g | Admiralty: -90g | Other: +1554g | Upkeep: -1338g | Net: +2009g
   Treasury: 15,070g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 515 troops
   Supply shortage at Tyrol: Archduke John loses 305 troops
   Garrison at Hanover reinforced: 0 -> 2,000
   Diplomatic blowback! Prussia discovered our scheming. (-3 relation)
   Territorial rivalry between Austria and Ottoman grows.
   Berthier reports that Massena appears envious of Murat's laurels — he has grown loud at the staff table about who is given the honours.
   Massena seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Ney appears envious of Murat's laurels — he has grown restless for glory.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 13
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Russia moves toward war with Sweden. The design is open; the timing is not.
   • Sire — Austria stands down over Ottoman Empire; the design was bought off, and the bargain stands.
   SITUATION
   France holds 28 regions. Treasury: 15,070g (+2,009 by the accounts)
   The courts at war hold 4 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 11 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 9 turns idle.
   - Murat — Gascony — 13,348 — 4 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 8 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Hanover — 44,245 [confirmed]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   TURN EVENTS
   Berthier reports that Massena appears envious of Murat's laurels — he has grown loud at the staff table about who is given the honours.
   Massena seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Ney appears envious of Murat's laurels — he has grown restless for glory.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 52.
   Blowback from Talleyrand's mission: Prussia discovered our scheming: -3 to relations (relations now 49).
   Russia delivers a final demand to Sweden — it is refused. The ladder has one rung left.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 1 more province. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 5 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
map: unchanged (55 labels)
```

```
#0263  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0263_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2074 of 2074 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   16,970
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ═══════════════════════════════════════
   Income: 2567g | Subsidies: -200g | Charges of Empire: -424g | Rentes: -60g | Admiralty: -90g | Other: +1554g | Upkeep: -1338g | Net: +2009g
   Treasury: 15,070g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 515 troops
   Supply shortage at Tyrol: Archduke John loses 305 troops
   Garrison at Hanover reinforced: 0 -> 2,000
   Diplomatic blowback! Prussia discovered our scheming. (-3 relation)
   Territorial rivalry between Austria and Ottoman grows.
   Berthier reports that Massena appears envious of Murat's laurels — he has grown loud at the staff table about who is given the honours.
   Massena seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Ney appears envious of Murat's laurels — he has grown restless for glory.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 13
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Russia moves toward war with Sweden. The design is open; the timing is not.
   • Sire — Austria stands down over Ottoman Empire; the design was bought off, and the bargain stands.
   SITUATION
   France holds 28 regions. Treasury: 15,070g (+2,009 by the accounts)
   The courts at war hold 4 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 11 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 9 turns idle.
   - Murat — Gascony — 13,348 — 4 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 8 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Hanover — 44,245 [confirmed]
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   TURN EVENTS
   Berthier reports that Massena appears envious of Murat's laurels — he has grown loud at the staff table about who is given the honours.
   Massena seeks an audience, Sire — his card waits on the Generals screen and on the rail.
   Berthier reports that Ney appears envious of Murat's laurels — he has grown restless for glory.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 52.
   Blowback from Talleyrand's mission: Prussia discovered our scheming: -3 to relations (relations now 49).
   Russia delivers a final demand to Sweden — it is refused. The ladder has one rung left.
   REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 1 more province. A new design hardens in their court.
   The court of Hanover takes up a new design: its own survival.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 5 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Britain and Russia. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The instruments are on the table, Sire — compensate, guarantee, or let it come having been asked."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 14 BEGINS
   ═══════════════════════════════════════
   Income: 2570g | Subsidies: -200g | Charges of Empire: -543g | Rentes: -60g | Admiralty: -90g | Other: +1561g | Upkeep: -1338g | Net: +1900g
   Treasury: 16,970g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 593 troops
   Supply shortage at Tyrol: Archduke John loses 318 troops
   Garrison at Hanover reinforced: 2,000 -> 4,000
   Russia declares war on Sweden — The Gulf and the Straits.
   Davout's resentment of Murat has cooled with time.
   Bernadotte's resentment of Murat has cooled for now. What was settled between them at the staff table has not been.
   Berthier reports that Lannes resents Murat's laurels again, 5 turns after the last — he has grown impatient for something worth the doing.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2076,292)  Spain(1185,881)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Britain(1397,292)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)  Hanover(1616,325)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney(1947,451)  Lannes(1962,425)  Bernadotte(1989,398)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  ?(1980,613)  Archduke Charles(1959,559)  Archduke John(1977,585)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  ?(1885,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  4k(1769,315)  12k(1697,412)  10k(1923,677)
```

```
#0264  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0264_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Britain Joins Offensive! @(3351,64)]  [icon: Austria Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: Marshal Massena seeks an audience @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: France Joins Offensive! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Hanover
   0
   T:3
   FOREIGN WARS
   controls: [Hanover]  [Russia + Austria + Britain vs Sweden]
── BottomLeftUI (layer 0) [scrolled 1655 of 1655 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   16,970
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► end turn
   ═══════════════════════════════════════
   TURN 14 BEGINS
   ═══════════════════════════════════════
   Income: 2570g | Subsidies: -200g | Charges of Empire: -543g | Rentes: -60g | Admiralty: -90g | Other: +1561g | Upkeep: -1338g | Net: +1900g
   Treasury: 16,970g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Supply shortage at Tyrol: Archduke Charles loses 593 troops
   Supply shortage at Tyrol: Archduke John loses 318 troops
   Garrison at Hanover reinforced: 2,000 -> 4,000
   Russia declares war on Sweden — The Gulf and the Straits.
   Davout's resentment of Murat has cooled with time.
   Bernadotte's resentment of Murat has cooled for now. What was settled between them at the staff table has not been.
   Berthier reports that Lannes resents Murat's laurels again, 5 turns after the last — he has grown impatient for something worth the doing.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 14
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
   SITUATION
   France holds 28 regions. Treasury: 16,970g (+1,900 by the accounts)
   The courts at war hold 2 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 12 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 10 turns idle.
   - Murat — Gascony — 13,348 — 5 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 9 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   TURN EVENTS
   Davout's resentment of Murat has cooled with time.
   Bernadotte's resentment of Murat has cooled for now. What was settled between them at the staff table has not been.
   Berthier reports that Lannes resents Murat's laurels again, 5 turns after the last — he has grown impatient for something worth the doing.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   THE DOCTRINES: Britain brings the Militia Transfer into force beside its Staff — Irreplaceable is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 57.
   Austria has joined Russia's war against Sweden, honoring their alliance.
   BLOCKADE: Britain closes Sweden's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   The compact with Sweden lies torn — Britain is named the breaker in every chancery of Europe.
   The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
   Relations with Russia have worsened significantly (-14 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0265  click Diplomacy (D)  ->  ok
  (clicked at (331, 18))
view: <run>\frames\0265_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 3000 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  / How Europe Reads France /   Read as: The hegemon of Europe — 49% of the continent's weight. /   The courts believe he will go as far as alliance (alarm 45). /   They think he is coming for Hesse — his corps stand against their soil. /  / The Empe …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1655 of 1655 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0266  click VASSALS  ->  ok
  (clicked at (2018, 273))
view: <run>\frames\0266_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 684 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 5/7
   ═══ CLIENT STATES ═══ /  / 4 client states remit +1,174g/turn in tribute. /  /   Bavaria  Satellite  (sworn by treaty, Turn 6) /      Loyalty 62/100  ≈ steady /   Tribute: +633g/turn (75% of their income)   Answers the call to arms /   Standing: bonded — nothing to ask /   Bond: +2/turn — a bond worth two honoured petitions (bond 52) /   No garrison — a corps in Munich would add a standing +2/turn …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS](disabled: You are reading this book)  [CONGRESS]  <Invest>  <Loosen Rein>  <Tighten Rein>  <Release>  <Invest>  <Loosen Rein>  <Tighten Rein>  <Release>  <Loosen Rein>  <Tighten Rein>  <Release>  <Invest>  <Loosen Rein>  <Tighten Rein>  <Release>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1655 of 1655 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
map: unchanged (51 labels)
```

```
#0267  click#1 Invest  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0267_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 45 / 100
   Turn 14 — Early April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G) (1)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Britain Joins Offensive! @(3351,64)]  [icon: Austria Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: Marshal Massena seeks an audience @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: France Joins Offensive! @(3561,64)]  [+28]
── DiplomaticLedger (layer 50) [scrolled 0 of 684 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 4/7
   ═══ CLIENT STATES ═══ /  / 4 client states remit +1,174g/turn in tribute. /  /   Bavaria  Satellite  (sworn by treaty, Turn 6) /      Loyalty 72/100  ≈ steady /   Tribute: +633g/turn (75% of their income)   Answers the call to arms /   Standing: bonded — nothing to ask /   Bond: +2/turn — a bond worth two honoured petitions (bond 52) /   No garrison — a corps in Munich would add a standing +2/turn …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS](disabled: You are reading this book)  [CONGRESS]  <Loosen Rein>  <Tighten Rein>  <Release>  <Invest>  <Loosen Rein>  <Tighten Rein>  <Release>  <Loosen Rein>  <Tighten Rein>  <Release>  <Invest>  <Loosen Rein>  <Tighten Rein>  <Release>
── BottomLeftUI (layer 0) [under a modal] [scrolled 1743 of 1743 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   16,770
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► invest in Bavaria
   Invested in Bavaria: +10 loyalty (62 → 72). Cost: 1 DP + 200g. Cooldown: 3 turns.
map: unchanged (51 labels)
```

```
#0268  type Lannes, move to Munich and garrison it  ->  ok
  (typed and Enter)
view: <run>\frames\0268_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
reply: ok Lannes moves from Franconia to Munich (232 lost to march)
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 684 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1854 of 1854 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   14
   Actions:
   3/4
   Admin:
   2/2
   Gold:
   16,770
   Inf:
   100,000
   Cav:
   30,000
   Art:
   17,800
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► Lannes, move to Munich and garrison it
   → Lannes moves from Franconia to Munich (232 lost to march)
   [3/4 actions remaining]
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2076,292)  Spain(1185,881)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Britain(1397,292)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)  Hanover(1616,325)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  10(1943,203)  5(1799,839)  Ney(1947,451)  Bernadotte(1976,425)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  ?(1980,605)  Archduke Charles(1959,577)  Archduke John(2017,538)  Lannes(1913,549)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  10k(1882,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  4k(1769,315)  12k(1697,412)  10k(1923,677)
```

```
#0269  click End Turn (E)  ->  ERROR: no visible control's text holds "End Turn (E)"
view: <run>\frames\0269_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: '' (focused)
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 684 px]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1854 of 1854 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Invested in Bavaria: +10 loyalty (62 → 72). Cost: 1 DP + 200g. Cooldown: 3 turns.
   ► Lannes, move to Munich and garrison it
   → Lannes moves from Franconia to Munich (232 lost to march)
   [3/4 actions remaining]
map: unchanged (51 labels)
```

```
#0270  click_at 2213 236  ->  ok
  (clicked at (2213, 236) on CloseButton  (Button, layer 50))
view: <run>\frames\0270_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 14 — Early April 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Hanover
   0
   T:3
   FOREIGN WARS
   controls: [Hanover]  [Russia + Austria + Britain vs Sweden]
── BottomLeftUI (layer 0) [scrolled 1854 of 1854 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Invested in Bavaria: +10 loyalty (62 → 72). Cost: 1 DP + 200g. Cooldown: 3 turns.
   ► Lannes, move to Munich and garrison it
   → Lannes moves from Franconia to Munich (232 lost to march)
   [3/4 actions remaining]
map: unchanged (51 labels)
```

```
#0271  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0271_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 14
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1809 of 1811 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   18,786
   Inf:
   100,000
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ════════════════════════════════════
   Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
   SITUATION
   France holds 28 regions. Treasury: 16,970g (+1,900 by the accounts)
   The courts at war hold 2 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 12 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 10 turns idle.
   - Murat — Gascony — 13,348 — 5 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Franconia — 11,639 — 9 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Tyrol — substantial force [partial]
   Archduke John — Tyrol — substantial force [partial]
   TURN EVENTS
   Davout's resentment of Murat has cooled with time.
   Bernadotte's resentment of Murat has cooled for now. What was settled between them at the staff table has not been.
   Berthier reports that Lannes resents Murat's laurels again, 5 turns after the last — he has grown impatient for something worth the doing.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
   THE DOCTRINES: Britain brings the Militia Transfer into force beside its Staff — Irreplaceable is over; its army gathers as ours does.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 57.
   Austria has joined Russia's war against Sweden, honoring their alliance.
   BLOCKADE: Britain closes Sweden's ports. Trade is cut by 62% (the Orders in Council) and the fleet is pinned at anchor, where crews rot.
   The compact with Sweden lies torn — Britain is named the breaker in every chancery of Europe.
   The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
   Relations with Russia have worsened significantly (-14 this turn).
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 6 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Austria and 3 lesser courts would march. Bound for now by a fresh peace: Russia and Britain. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
   ► invest in Bavaria
   Invested in Bavaria: +10 loyalty (62 → 72). Cost: 1 DP + 200g. Cooldown: 3 turns.
   ► Lannes, move to Munich and garrison it
   → Lannes moves from Franconia to Munich (232 lost to march)
   [3/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 15 BEGINS
   ═══════════════════════════════════════
   Income: 2572g | Subsidies: -200g | Charges of Empire: -661g | Rentes: -60g | Admiralty: -90g | Other: +1793g | Upkeep: -1338g | Net: +2016g | Spent: 200g
   Treasury: 18,786g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 74 (+2): the garrison's presence, relations with the lord
   Relations between Austria and Russia are deteriorating. Alliance may collapse in 2 turns.
   Russia has downgraded relations with Naples: OPEN_BORDERS → PEACE.
   The feud between Bernadotte and Murat is now mutual — each schemes against the other. Separate them, Sire, or accept the friction.
   Berthier reports that Bernadotte resents Murat's laurels for the third time — he has grown careful about what he commits to paper.
   Berthier reports that Murat appears envious of Bernadotte's laurels — he has grown impatient for something worth the doing.
   Berthier reports that Davout resents Murat's laurels again, 4 turns after the last — he has grown cold and withholding. He asked for an audience on turn 9, and will not ask again before turn 15.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2065,293)  Spain(1185,881)  Sweden(1905,32)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Britain(1397,292)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)  Hanover(1726,333)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  11(1943,203)  5(1799,839)  Ney(1947,451)  Bernadotte(1976,425)  ?(1580,371)  Brunswick(1580,331)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  Lannes(1913,549)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  10k(1882,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  ?(1769,299)  12k(1697,412)  10k(1923,677)
```

```
#0272  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0272_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['marshal_petition', 'war_status_panel (not modal)'], region_panel=no
── MarshalPetitionDialog (layer 114) [scrolled 0 of 69 px] ──
   BERNADOTTE — Marshal Bernadotte demands to be heard
   Give him a command is closed — There is no enemy within his reach to send him against.
   "I have said my piece before. I will not say it a third time unless you wish it." /  / Sire, Bernadotte observes — without complaint, he is careful to say — that Murat's name reaches you before his own. The feud with Murat is now mutual and the army knows it. He asks, plainly, where the Emperor stands.
   Free, and it fixes nothing. For 5 more turns he brings NONE of his 11,647 men to any battle Murat leads, quarrel or no quarrel — they are openly at odds already; the quarrel can grow no worse.
   His patience is bought — the grievance shortens by 2 turns.
   controls: [Let it stand   [Free]]  [Promise Glory   [1 AP]]  [Rebuke]  [Later (he will return)]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Petition from Switzerland @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Austria Joins Offensive! @(3435,64)]  [icon: Russia Declares War! @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: France Joins Offensive! @(3561,64)]  [+29]
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Hanover
   0
   T:4
   FOREIGN WARS
   controls: [Hanover]  [Russia + Austria + Britain vs Sweden]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2055 of 2055 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   18,786
   Inf:
   100,000
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Berthier: "A war we are not in, Sire — for now. Both courts will come asking; the question is what our neutrality is worth."
   ════════════════════════════════════
   ► invest in Bavaria
   Invested in Bavaria: +10 loyalty (62 → 72). Cost: 1 DP + 200g. Cooldown: 3 turns.
   ► Lannes, move to Munich and garrison it
   → Lannes moves from Franconia to Munich (232 lost to march)
   [3/4 actions remaining]
   ► end turn
   ═══════════════════════════════════════
   TURN 15 BEGINS
   ═══════════════════════════════════════
   Income: 2572g | Subsidies: -200g | Charges of Empire: -661g | Rentes: -60g | Admiralty: -90g | Other: +1793g | Upkeep: -1338g | Net: +2016g | Spent: 200g
   Treasury: 18,786g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 74 (+2): the garrison's presence, relations with the lord
   Relations between Austria and Russia are deteriorating. Alliance may collapse in 2 turns.
   Russia has downgraded relations with Naples: OPEN_BORDERS → PEACE.
   The feud between Bernadotte and Murat is now mutual — each schemes against the other. Separate them, Sire, or accept the friction.
   Berthier reports that Bernadotte resents Murat's laurels for the third time — he has grown careful about what he commits to paper.
   Berthier reports that Murat appears envious of Bernadotte's laurels — he has grown impatient for something worth the doing.
   Berthier reports that Davout resents Murat's laurels again, 4 turns after the last — he has grown cold and withholding. He asked for an audience on turn 9, and will not ask again before turn 15.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 15
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Britain and Russia would now join a league against us (relations −77 and −90). The Balance of Europe names the price to keep each out.
   • Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
   SITUATION
   France holds 28 regions. Treasury: 18,786g (+2,016 by the accounts)
   The courts at war hold 1 region. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 13 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 11 turns idle.
   - Murat — Gascony — 13,348 — 6 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Munich — 11,407 — Awaiting orders.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Artois — substantial force [partial]
   TURN EVENTS
   Bavaria loyalty 74 (+2): the garrison's presence, relations with the lord
   The feud between Bernadotte and Murat is now mutual — each schemes against the other. Separate them, Sire, or accept the friction.
   Berthier reports that Bernadotte resents Murat's laurels for the third time — he has grown careful about what he commits to paper.
   Berthier reports that Murat appears envious of Bernadotte's laurels — he has grown impatient for something worth the doing.
   Berthier reports that Davout resents Murat's laurels again, 4 turns after the last — he has grown cold and withholding. He asked for an audience on turn 9, and will not ask again before turn 15.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   THE LANDING: Paget has put 8,991 men ashore at Estonia.
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 65.
   An envoy from Switzerland has arrived with a petition.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0273  click Let it stand  ->  ok
  (clicked at (1825, 501))
view: <run>\frames\0273_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Chancery of Helvetia (Dove) of Switzerland /  / The petition: /   - Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +9 (to the 100 ceiling), its bond with us rises 20 → 40 (worth +2 a turn in loyalty, now +1), for 1 DP. /   - Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (20 → 0: worth +0 a  …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 15 — Late April 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2098 of 2098 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   18,786
   Inf:
   100,000
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Bernadotte's grievance runs its course.
map: unchanged (50 labels)
```

```
#0274  click Envoys (1)  ->  ERROR: no visible control's text holds "Envoys (1)"
view: <run>\frames\0274_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2098 of 2098 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
map: unchanged (50 labels)
```

```
#0275  click Grant  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0275_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 45 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Britain Joins Offensive! @(3351,64)]  [icon: Austria Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: European Courts Concerned @(3477,64)]  [icon: France Joins Offensive! @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Hanover
   0
   T:4
   FOREIGN WARS
   controls: [Hanover]  [Russia + Austria + Britain vs Sweden]
── BottomLeftUI (layer 0) [scrolled 2164 of 2164 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   18,786
   Inf:
   100,000
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (50 labels)
```

```
#0276  click Diplomacy (D)  ->  ok
  (clicked at (313, 18))
view: <run>\frames\0276_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 2956 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 4/7
   ═══ NATION OVERVIEW ═══ / Every court of Europe — its temper toward France, and the instruments to move it. Press F1 to treat; D closes this ledger. /  / How Europe Reads France /   Read as: The hegemon of Europe — 49% of the continent's weight. /   The courts believe he will go as far as alliance (alarm 45). /   They think he is coming for Hesse — his corps stand against their soil. /  / The Empe …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS](disabled: You are reading this book)  [TREATIES]  [THREAT & COALITION]  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2164 of 2164 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (50 labels)
```

```
#0277  click THREAT & COALITION  ->  ok
  (clicked at (1670, 273))
view: <run>\frames\0277_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 0 of 376 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 4/7
   BALANCE OF EUROPE / ──────────────── / French-led alignment holds 49% of active European bloc power. / Power score: 145 / 293. / This counts France's direct allies and vassal bloc against all active courts. Alliance networks can overlap; the headline shows the current largest alignment. / Bloc members: Bavaria, France, Holland, Kingdom of Italy, Prussia, Spain, Switzerland. / Warning bands: 33% no …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [THREAT & COALITION](disabled: You are reading this book)  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2164 of 2164 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (50 labels)
```

```
#0278  scroll 1825 600 down 10  ->  ok
  (scrolled down 10 at (1825, 600))
view: <run>\frames\0278_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=['diplomatic_ledger'], pinned=-, popups=[], region_panel=no
── TopBar (layer 75): unchanged
── DiplomaticLedger (layer 50) [scrolled 353 of 377 px] ──
   DIPLOMATIC LEDGER
   Talleyrand: Courting → Prussia
   DP: 4/7
   BALANCE OF EUROPE / ──────────────── / French-led alignment holds 49% of active European bloc power. / Power score: 145 / 293. / This counts France's direct allies and vassal bloc against all active courts. Alliance networks can overlap; the headline shows the current largest alignment. / Bloc members: Bavaria, France, Holland, Kingdom of Italy, Prussia, Spain, Switzerland. / Warning bands: 33% no …
   controls: [Pin]  [icon @(2213,236)]  [NATIONS]  [TREATIES]  [THREAT & COALITION](disabled: You are reading this book)  [TALLEYRAND]  [WAR BARGAINS]  [VASSALS]  [CONGRESS]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2164 of 2164 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (50 labels)
```

```
#0279  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0279_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 686 px] ──
   DIPLOMACY
   DP: 4
   "Your Excellency, which nation requires our diplomatic attention?"
   The Congress of Paris — 7 of 8 terms met  ▸ the terms
   At War (1)
   Treaties (8)
   controls: [icon: Close (Esc) @(2075,284)]  <▸ the terms>  [Summon the Congress of Paris (2 diplomatic points + 1 administrative action; and while it sits, from this end turn, your](disabled: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and )  [View the table]  [Formable Nations — states that could yet exist]  [Hanover  —  At War  |  -60 (Hostile)]  [Prussia  —  Alliance  |  +65 (Loyal)  [MISSION]]  [Spain  —  Alliance  |  +26 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal] ──
   ACTIVE WARS
   Hanover
   0
   T:4
   FOREIGN WARS
   controls: [Hanover]  [Russia + Austria + Britain vs Sweden]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2164 of 2164 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (50 labels)
```

```
#0280  scroll 1825 600 down 15  ->  ok
  (scrolled down 15 at (1825, 600))
view: <run>\frames\0280_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 566 of 686 px] ──
   DIPLOMACY
   DP: 4
   "Your Excellency, which nation requires our diplomatic attention?"
   Neutral (6)
   controls: [icon: Close (Esc) @(2075,284)]  [Bavaria  —  Vassal  |  +52 (Friendly)]  [Holland  —  Vassal  |  +20 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  +40 (Friendly)]  [Britain  —  Peace  |  -77 (Hostile)]  [Russia  —  Peace  |  -90 (Hostile)]  [Austria  —  Peace  |  -59 (Hostile)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2164 of 2164 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (50 labels)
```

```
#0281  click Russia  —  Peace  ->  ok
  (clicked at (1825, 604))
view: <run>\frames\0281_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: ''
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 46 px, 0 of 369 px] ──
   DIPLOMACY — Russia
   DP: 4
   TALLEYRAND'S ASSESSMENT — RUSSIA / Status: Peace   Relation: -90 (Hostile) /  / "Relations with Russia remain cold. They eye us with suspicion. Little can be achieved diplomatically until the temperature changes." / Recommendation: Relations must improve before proposals will find purchase. A battlefield victory would change their calculus.
   Relations with Russia stand at -90; an Open Borders needs -20.
   controls: [icon: Close (Esc) @(2075,284)]  [Sponsor Their Design (200g/turn) (1 DP + 200g)  —  Aim their court at Sweden — gold flows, the compact binds both ends (]  [Buy Off Their Design (1320g) (1 DP + 1320g)  —  The design sleeps while the bargain stands — and waking it by betrayal i]  [Guarantee Their Borders (1 DP)  —  Raises every coveter's bar for war (-8 weight) — and stakes French credibility on the]  [Propose Open Borders (1 DP)  —  Hopeless](disabled: Relations with Russia stand at -90; an Open Borders needs -20.)  [Back]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2164 of 2164 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (50 labels)
```

```
#0282  click Buy Off Their Design (1320g)  ->  ok
  (clicked at (1825, 517))
view: <run>\frames\0282_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 15 — Late April 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 3/7
   Threat 45 / 100
   Turn 15 — Late April 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Britain Joins Offensive! @(3351,64)]  [icon: Austria Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: European Courts Concerned @(3477,64)]  [icon: France Joins Offensive! @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+28]
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1719 of 1719 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   15
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   17,466
   Inf:
   100,000
   Cav:
   30,000
   Art:
   18,400
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 74 (+2): the garrison's presence, relations with the lord
   Relations between Austria and Russia are deteriorating. Alliance may collapse in 2 turns.
   Russia has downgraded relations with Naples: OPEN_BORDERS → PEACE.
   The feud between Bernadotte and Murat is now mutual — each schemes against the other. Separate them, Sire, or accept the friction.
   Berthier reports that Bernadotte resents Murat's laurels for the third time — he has grown careful about what he commits to paper.
   Berthier reports that Murat appears envious of Bernadotte's laurels — he has grown impatient for something worth the doing.
   Berthier reports that Davout resents Murat's laurels again, 4 turns after the last — he has grown cold and withholding. He asked for an audience on turn 9, and will not ask again before turn 15.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 15
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Britain and Russia would now join a league against us (relations −77 and −90). The Balance of Europe names the price to keep each out.
   • Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
   SITUATION
   France holds 28 regions. Treasury: 18,786g (+2,016 by the accounts)
   The courts at war hold 1 region. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 13 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 11 turns idle.
   - Murat — Gascony — 13,348 — 6 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Munich — 11,407 — Awaiting orders.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Artois — substantial force [partial]
   TURN EVENTS
   Bavaria loyalty 74 (+2): the garrison's presence, relations with the lord
   The feud between Bernadotte and Murat is now mutual — each schemes against the other. Separate them, Sire, or accept the friction.
   Berthier reports that Bernadotte resents Murat's laurels for the third time — he has grown careful about what he commits to paper.
   Berthier reports that Murat appears envious of Bernadotte's laurels — he has grown impatient for something worth the doing.
   Berthier reports that Davout resents Murat's laurels again, 4 turns after the last — he has grown cold and withholding. He asked for an audience on turn 9, and will not ask again before turn 15.
   The staff report 1 further matter among the marshals — the Generals screen has the particulars.
   DIPLOMATIC EVENTS
   THE LANDING: Paget has put 8,991 men ashore at Estonia.
   THE LAWS: Austria enacts the Landwehr — infantry manpower returns 25% faster.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 65.
   An envoy from Switzerland has arrived with a petition.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP.
   ► buy off Russia
   Russia's design — The Gulf and the Straits — is bought off for 1320 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
map: unchanged (50 labels)
```

```
#0283  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0283_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2117 of 2117 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   16
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   19,185
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 16 BEGINS
   ═══════════════════════════════════════
   Income: 2574g | Subsidies: -200g | Charges of Empire: -742g | Rentes: -60g | Admiralty: -90g | Other: +1575g | Upkeep: -1338g | Net: +1719g | Spent: 1320g
   Treasury: 19,185g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 76 (+2): the garrison's presence, relations with the lord
   Territorial rivalry between Britain and Russia grows.
   Murat's grievance is satisfied — he has surpassed Bernadotte in glory. He fights with renewed purpose (+10% attack this turn).
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2065,293)  Spain(1185,881)  Sweden(1894,85)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Britain(1391,217)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)  Hanover(1726,333)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  12(1943,203)  5(1799,839)  Ney(1947,451)  Bernadotte(1976,425)  ?(1580,371)  Brunswick(1580,331)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  Lannes(1913,549)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  10k(1882,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  ?(1769,299)  12k(1697,412)  10k(1923,677)
```

```
#0284  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0284_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 16 — Early May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 16 — Early May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Britain Joins Offensive! @(3351,64)]  [icon: Austria Joins Offensive! @(3393,64)]  [icon: Russia Declares War! @(3435,64)]  [icon: European Courts Concerned @(3477,64)]  [icon: France Joins Offensive! @(3519,64)]  [icon: Prussia Declares War! @(3561,64)]  [+28]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   Hanover
   0
   T:5
   FOREIGN WARS
   controls: [Hanover]  [Russia + Austria + Britain vs Sweden]
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
   19,185
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Switzerland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 7 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "A court that would march can still be talked out of it, Sire. The Balance of Europe names the price."
   ════════════════════════════════════
   Bernadotte's grievance runs its course.
   Responding to Switzerland's proposal: accepted
   Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP.
   ► buy off Russia
   Russia's design — The Gulf and the Straits — is bought off for 1320 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► end turn
   ═══════════════════════════════════════
   TURN 16 BEGINS
   ═══════════════════════════════════════
   Income: 2574g | Subsidies: -200g | Charges of Empire: -742g | Rentes: -60g | Admiralty: -90g | Other: +1575g | Upkeep: -1338g | Net: +1719g | Spent: 1320g
   Treasury: 19,185g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 76 (+2): the garrison's presence, relations with the lord
   Territorial rivalry between Britain and Russia grows.
   Murat's grievance is satisfied — he has surpassed Bernadotte in glory. He fights with renewed purpose (+10% attack this turn).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 16
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Sweden will not forgive Britain the loss of Uleaborg and 1 more province. A new design hardens in their court.
   • Sire — Europe has watched us 8 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 19,185g (+1,719 by the accounts)
   The courts at war hold 1 region. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 14 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 12 turns idle.
   - Murat — Gascony — 13,348 — 7 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Munich — 11,407 — Awaiting orders.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Artois — substantial force [partial]
   TURN EVENTS
   Bavaria loyalty 76 (+2): the garrison's presence, relations with the lord
   Murat's grievance is satisfied — he has surpassed Bernadotte in glory. He fights with renewed purpose (+10% attack this turn).
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 73.
   REVANCHE: Sweden will not forgive Britain the loss of Uleaborg and 1 more province. A new design hardens in their court.
   The court of Sweden takes up a new design: Revanche.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Lannes nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (50 labels)
```

```
#0285  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0285_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1966 of 1968 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   21,540
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ► buy off Russia
   Russia's design — The Gulf and the Straits — is bought off for 1320 gold. Talleyrand: "The want sleeps, Sire; it does not die. The bargain is a hostage we have given — renege on it and it returns the heavier."
   ► end turn
   ═══════════════════════════════════════
   TURN 16 BEGINS
   ═══════════════════════════════════════
   Income: 2574g | Subsidies: -200g | Charges of Empire: -742g | Rentes: -60g | Admiralty: -90g | Other: +1575g | Upkeep: -1338g | Net: +1719g | Spent: 1320g
   Treasury: 19,185g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 76 (+2): the garrison's presence, relations with the lord
   Territorial rivalry between Britain and Russia grows.
   Murat's grievance is satisfied — he has surpassed Bernadotte in glory. He fights with renewed purpose (+10% attack this turn).
   ════════════════════════════════════
   MORNING DISPATCH — Turn 16
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Sweden will not forgive Britain the loss of Uleaborg and 1 more province. A new design hardens in their court.
   • Sire — Europe has watched us 8 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 19,185g (+1,719 by the accounts)
   The courts at war hold 1 region. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 14 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 12 turns idle.
   - Murat — Gascony — 13,348 — 7 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Munich — 11,407 — Awaiting orders.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Artois — substantial force [partial]
   TURN EVENTS
   Bavaria loyalty 76 (+2): the garrison's presence, relations with the lord
   Murat's grievance is satisfied — he has surpassed Bernadotte in glory. He fights with renewed purpose (+10% attack this turn).
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 73.
   REVANCHE: Sweden will not forgive Britain the loss of Uleaborg and 1 more province. A new design hardens in their court.
   The court of Sweden takes up a new design: Revanche.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Lannes nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 2576g | Subsidies: -200g | Charges of Empire: -206g | Rentes: -60g | Other: +1583g | Upkeep: -1338g | Net: +2355g
   Treasury: 21,540g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 78 (+2): the garrison's presence, relations with the lord
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   Ney's resentment of Murat has cooled with time.
   Massena's resentment of Murat has cooled with time.
   Murat's laurels have faded, Sire — for now no commander in the army stands above the rest.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2061,255)  Spain(1185,881)  Sweden(1863,83)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Britain(1391,217)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  13(1943,203)  5(1799,839)  Ney(1947,451)  Bernadotte(1976,425)  ?(1580,371)  Brunswick(1580,331)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  Lannes(1913,549)  Massena(1923,612)  ?(2108,430)  ?(1981,363)  10k(1882,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  12k(1697,412)  10k(1923,677)
```

```
#0286  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0286_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 17 — Late May 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 17 — Late May 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Hanover Eliminated! @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Austria Joins Offensive! @(3435,64)]  [icon: Russia Declares War! @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: France Joins Offensive! @(3561,64)]  [+30]
── BottomLeftUI (layer 0) [scrolled 2009 of 2009 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   17
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   21,540
   Inf:
   100,000
   Cav:
   30,000
   Art:
   19,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 73.
   REVANCHE: Sweden will not forgive Britain the loss of Uleaborg and 1 more province. A new design hardens in their court.
   The court of Sweden takes up a new design: Revanche.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 8 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Lannes nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 17 BEGINS
   ═══════════════════════════════════════
   Income: 2576g | Subsidies: -200g | Charges of Empire: -206g | Rentes: -60g | Other: +1583g | Upkeep: -1338g | Net: +2355g
   Treasury: 21,540g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 78 (+2): the garrison's presence, relations with the lord
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   Ney's resentment of Murat has cooled with time.
   Massena's resentment of Murat has cooled with time.
   Murat's laurels have faded, Sire — for now no commander in the army stands above the rest.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 17
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Hanover is knocked out of the war. No army remains beneath their colours.
   SITUATION
   France holds 28 regions. Treasury: 21,540g (+2,355 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 15 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 13 turns idle.
   - Murat — Gascony — 13,348 — 8 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Munich — 11,407 — Awaiting orders.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Artois — substantial force [partial]
   TURN EVENTS
   Bavaria loyalty 78 (+2): the garrison's presence, relations with the lord
   Ney's resentment of Murat has cooled with time.
   Massena's resentment of Murat has cooled with time.
   Murat's laurels have faded, Sire — for now no commander in the army stands above the rest.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Commissariat — fed provinces feed 25% more men (×1.25).
   Sire — Hanover has been eliminated from the war.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 81.
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   The court of Prussia takes up a new design: Armed Neutrality.
   The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 9 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "One enemy the fewer, Sire. Every court in Europe is doing its arithmetic tonight."
   ════════════════════════════════════
map: unchanged (48 labels)
```

```
#0287  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0287_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 17
   BRITAIN / ──────────────────────────── / - Shrapnel abandons fortified position / - Shrapnel moves to Cornwall / - Shrapnel embarks an expedition for Stockholm /     Assault on the garrison of Stockholm /       Garrison: 1,569 lost, 13,431 still under arms /       The assault cost them 1,917. /  / ──────────────────────────── / Russia, Austria, Prussia and 5 other courts stirred as well, but their …
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 18 — Early June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
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
   24,076
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ═══════════════════════════════════════
   Income: 2576g | Subsidies: -200g | Charges of Empire: -206g | Rentes: -60g | Other: +1583g | Upkeep: -1338g | Net: +2355g
   Treasury: 21,540g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 78 (+2): the garrison's presence, relations with the lord
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   Ney's resentment of Murat has cooled with time.
   Massena's resentment of Murat has cooled with time.
   Murat's laurels have faded, Sire — for now no commander in the army stands above the rest.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 17
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Hanover is knocked out of the war. No army remains beneath their colours.
   SITUATION
   France holds 28 regions. Treasury: 21,540g (+2,355 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 15 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 13 turns idle.
   - Murat — Gascony — 13,348 — 8 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Munich — 11,407 — Awaiting orders.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Brunswick — Artois — substantial force [partial]
   TURN EVENTS
   Bavaria loyalty 78 (+2): the garrison's presence, relations with the lord
   Ney's resentment of Murat has cooled with time.
   Massena's resentment of Murat has cooled with time.
   Murat's laurels have faded, Sire — for now no commander in the army stands above the rest.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts the Commissariat — fed provinces feed 25% more men (×1.25).
   Sire — Hanover has been eliminated from the war.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 81.
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   The court of Prussia takes up a new design: Armed Neutrality.
   The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 9 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "One enemy the fewer, Sire. Every court in Europe is doing its arithmetic tonight."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 18 BEGINS
   ═══════════════════════════════════════
   Income: 2578g | Charges of Empire: -234g | Rentes: -60g | Other: +1590g | Upkeep: -1338g | Net: +2536g
   Treasury: 24,076g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Garrison at Stockholm reinforced: 13,431 -> 15,000
   Bavaria loyalty 80 (+2): the garrison's presence, relations with the lord
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2061,255)  Spain(1185,881)  Sweden(1860,83)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Britain(1391,217)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  14(1943,203)  5(1799,839)  Shrapnel(1829,41)  ?(2057,485)  Mack(2058,445)  Ney(1947,451)  Bernadotte(1976,425)  ?(1580,371)  Brunswick(1580,331)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  Lannes(1913,549)  Massena(1923,612)  15k(1829,135)  ?(2108,430)  ?(2057,545)  ?(1981,363)  10k(1882,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  12k(1697,412)  10k(1923,677)
```

```
#0288  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0288_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 18 — Early June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 18 — Early June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Hanover Eliminated! @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Austria Joins Offensive! @(3435,64)]  [icon: Russia Declares War! @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: France Joins Offensive! @(3561,64)]  [+30]
── BottomLeftUI (layer 0) [scrolled 1877 of 1877 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   18
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   24,076
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Talleyrand's efforts in Prussia continue. Relations now at 81.
   Relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
   The court of Prussia takes up a new design: Armed Neutrality.
   The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 9 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "One enemy the fewer, Sire. Every court in Europe is doing its arithmetic tonight."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 18 BEGINS
   ═══════════════════════════════════════
   Income: 2578g | Charges of Empire: -234g | Rentes: -60g | Other: +1590g | Upkeep: -1338g | Net: +2536g
   Treasury: 24,076g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Garrison at Stockholm reinforced: 13,431 -> 15,000
   Bavaria loyalty 80 (+2): the garrison's presence, relations with the lord
   ════════════════════════════════════
   MORNING DISPATCH — Turn 18
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Austria enacts the Generalissimus — every levy costs 10% less (×0.9).
   • Sire — Shrapnel has put 5,480 men ashore at Stockholm.
   • Sire — Europe has watched us 10 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 24,076g (+2,536 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 16 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 14 turns idle.
   - Murat — Gascony — 13,348 — 9 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Munich — 11,407 — 3 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Shrapnel — Stockholm — 3,563 [confirmed]
   Mack — Bohemia — substantial force [partial]
   Brunswick — Artois — substantial force [partial]
   TURN EVENTS
   Bavaria loyalty 80 (+2): the garrison's presence, relations with the lord
   DIPLOMATIC EVENTS
   THE LANDING: Shrapnel has put 5,480 men ashore at Stockholm.
   THE LAWS: Austria enacts the Generalissimus — every levy costs 10% less (×0.9).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 89.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Lannes nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0289  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0289_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 18
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 19 — Late June 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1720 of 1722 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   26,929
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Treasury: 24,076g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Garrison at Stockholm reinforced: 13,431 -> 15,000
   Bavaria loyalty 80 (+2): the garrison's presence, relations with the lord
   ════════════════════════════════════
   MORNING DISPATCH — Turn 18
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Austria enacts the Generalissimus — every levy costs 10% less (×0.9).
   • Sire — Shrapnel has put 5,480 men ashore at Stockholm.
   • Sire — Europe has watched us 10 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 24,076g (+2,536 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 16 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 14 turns idle.
   - Murat — Gascony — 13,348 — 9 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Munich — 11,407 — 3 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Shrapnel — Stockholm — 3,563 [confirmed]
   Mack — Bohemia — substantial force [partial]
   Brunswick — Artois — substantial force [partial]
   TURN EVENTS
   Bavaria loyalty 80 (+2): the garrison's presence, relations with the lord
   DIPLOMATIC EVENTS
   THE LANDING: Shrapnel has put 5,480 men ashore at Stockholm.
   THE LAWS: Austria enacts the Generalissimus — every levy costs 10% less (×0.9).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 89.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Lannes nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 19 BEGINS
   ═══════════════════════════════════════
   Income: 2581g | Charges of Empire: -264g | Rentes: -60g | Other: +1934g | Upkeep: -1338g | Net: +2853g
   Treasury: 26,929g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Diplomatic blowback! Prussia discovered our scheming. (-3 relation)
   Bavaria loyalty 82 (+2): the garrison's presence, relations with the lord
   Territorial rivalry between Britain and Russia grows.
   Davout's resentment of Murat has cooled with time.
   Lannes's resentment of Murat has cooled with time.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2061,255)  Spain(1185,881)  Sweden(1860,83)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Britain(1391,217)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  15(1943,203)  5(1799,839)  Shrapnel(1829,41)  ?(2057,485)  Mack(2058,445)  Ney(1947,451)  Bernadotte(1976,425)  ?(1580,371)  Brunswick(1580,331)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  Lannes(1913,549)  Massena(1923,612)  15k(1829,135)  ?(2108,430)  ?(2057,545)  ?(1981,363)  10k(1882,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  12k(1697,412)  10k(1923,677)
```

```
#0290  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0290_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Petition from Holland @(3492,64)]  [icon: Hanover Eliminated! @(3534,64)]  [icon: Britain Joins Offensive! @(3576,64)]  [icon: Austria Joins Offensive! @(3618,64)]  [icon: Russia Declares War! @(3649,64)]
── BottomLeftUI (layer 0) [scrolled 1921 of 1921 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   26,929
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 10 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The marshals' rivalries demand attention, Sire — Bernadotte, Lannes nurse a grievance, Bernadotte's the deepest."
   ════════════════════════════════════
   ► end turn
   ═══════════════════════════════════════
   TURN 19 BEGINS
   ═══════════════════════════════════════
   Income: 2581g | Charges of Empire: -264g | Rentes: -60g | Other: +1934g | Upkeep: -1338g | Net: +2853g
   Treasury: 26,929g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Diplomatic blowback! Prussia discovered our scheming. (-3 relation)
   Bavaria loyalty 82 (+2): the garrison's presence, relations with the lord
   Territorial rivalry between Britain and Russia grows.
   Davout's resentment of Murat has cooled with time.
   Lannes's resentment of Murat has cooled with time.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 19
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — an envoy from Holland has arrived with a petition.
   • Sire — Europe has watched us 11 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 26,929g (+2,853 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 17 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 15 turns idle.
   - Murat — Gascony — 13,348 — 10 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Munich — 11,407 — 4 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Shrapnel — Stockholm — 3,563 [confirmed]
   Mack — Bohemia — large force [partial]
   Brunswick — Artois — substantial force [partial]
   TURN EVENTS
   Bavaria loyalty 82 (+2): the garrison's presence, relations with the lord
   Davout's resentment of Murat has cooled with time.
   Lannes's resentment of Murat has cooled with time.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 97.
   Blowback from Talleyrand's mission: Prussia discovered our scheming: -3 to relations (relations now 94).
   An envoy from Holland has arrived with a petition.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Holland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Bernadotte nurses a grievance against Murat, Sire — and has stood idle 16 turns. Those are the same fact."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0291  click Envoys (1)  ->  ok
  (clicked at (3404, 18))
view: <run>\frames\0291_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['incoming_proposal'], region_panel=no
── IncomingProposalPopup (layer 112) ──
   A CLIENT'S PETITION / Schimmelpenninck (Loyalist) of Holland /  / The petition: /   - Grant it, and Holland's tribute of 337g a turn is remitted for 8 collections (2696g forgone): loyalty +9 (to the 100 ceiling), its bond with us rises 20 → 40 (worth +2 a turn in loyalty, now +1), for 1 DP. /   - Refuse it, and Holland loses 10 loyalty and its bond with us falls 20 (20 → 0: worth +0 a turn in loya …
   controls: [Grant]  [Refuse]  [Not Now]
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1921 of 1921 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   26,929
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 45/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Bernadotte nurses a grievance against Murat, Sire — and has stood idle 16 turns. Those are the same fact."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0292  click Grant  ->  ok
  (clicked at (1679, 687))
view: <run>\frames\0292_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 19 — Late June 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 4/7
   Threat 45 / 100
   Turn 19 — Late June 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Prussia — Courting]  [Recall]  [icon: Hanover Eliminated! @(3492,64)]  [icon: Britain Joins Offensive! @(3534,64)]  [icon: Austria Joins Offensive! @(3576,64)]  [icon: Russia Declares War! @(3618,64)]  [icon: European Courts Concerned @(3649,64)]
── BottomLeftUI (layer 0) [scrolled 1986 of 1986 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   19
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   26,929
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP.
map: unchanged (53 labels)
```

```
#0293  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0293_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 19
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 20 — Early July 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1787 of 1788 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   29,419
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Diplomatic blowback! Prussia discovered our scheming. (-3 relation)
   Bavaria loyalty 82 (+2): the garrison's presence, relations with the lord
   Territorial rivalry between Britain and Russia grows.
   Davout's resentment of Murat has cooled with time.
   Lannes's resentment of Murat has cooled with time.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 19
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — an envoy from Holland has arrived with a petition.
   • Sire — Europe has watched us 11 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The cheapest court to keep out of it is Naples: Talleyrand brings her to −10 in 1 turn (1 DP).
   SITUATION
   France holds 28 regions. Treasury: 26,929g (+2,853 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 17 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 15 turns idle.
   - Murat — Gascony — 13,348 — 10 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Munich — 11,407 — 4 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Shrapnel — Stockholm — 3,563 [confirmed]
   Mack — Bohemia — large force [partial]
   Brunswick — Artois — substantial force [partial]
   TURN EVENTS
   Bavaria loyalty 82 (+2): the garrison's presence, relations with the lord
   Davout's resentment of Murat has cooled with time.
   Lannes's resentment of Murat has cooled with time.
   DIPLOMATIC EVENTS
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 97.
   Blowback from Talleyrand's mission: Prussia discovered our scheming: -3 to relations (relations now 94).
   An envoy from Holland has arrived with a petition.
   ENVOYS AWAITING RESPONSE
   Talleyrand: 1 envoy awaits your reply this turn. Open Envoys before ending the turn.
   - Holland — Client Petition
   Berthier: "I have placed the diplomatic packet atop the morning dispatch, Sire."
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Bernadotte nurses a grievance against Murat, Sire — and has stood idle 16 turns. Those are the same fact."
   ════════════════════════════════════
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP.
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 2583g | Charges of Empire: -299g | Rentes: -60g | Other: +1604g | Upkeep: -1338g | Net: +2490g
   Treasury: 29,419g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 84 (+2): the garrison's presence, relations with the lord
   Relations between Austria and Russia are deteriorating. Defensive Alliance may collapse in 2 turns.
   Bernadotte's resentment of Murat has cooled for now. What was settled between them at the staff table has not been.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2061,255)  Spain(1185,881)  Sweden(1860,83)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Britain(1391,217)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  15(1943,203)  5(1799,839)  Shrapnel(1829,36)  ?(2057,485)  Mack(2058,445)  Ney(1947,451)  Bernadotte(1976,425)  ?(1580,371)  Brunswick(1580,331)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  Lannes(1913,549)  Massena(1923,612)  ?(1829,135)  ?(2108,430)  ?(2057,545)  ?(1981,363)  10k(1882,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  12k(1697,412)  10k(1923,677)
```

```
#0294  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0294_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
── TopBar (layer 75) ──
   DP: 5/7
   Threat 45 / 100
   Turn 20 — Early July 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Hanover Eliminated! @(3351,64)]  [icon: Britain Joins Offensive! @(3393,64)]  [icon: Austria Joins Offensive! @(3435,64)]  [icon: Russia Declares War! @(3477,64)]  [icon: European Courts Concerned @(3519,64)]  [icon: France Joins Offensive! @(3561,64)]  [+30]
── BottomLeftUI (layer 0) [scrolled 1811 of 1811 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   29,419
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 11 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Bernadotte nurses a grievance against Murat, Sire — and has stood idle 16 turns. Those are the same fact."
   ════════════════════════════════════
   Responding to Holland's proposal: accepted
   Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP.
   ► end turn
   ═══════════════════════════════════════
   TURN 20 BEGINS
   ═══════════════════════════════════════
   Income: 2583g | Charges of Empire: -299g | Rentes: -60g | Other: +1604g | Upkeep: -1338g | Net: +2490g
   Treasury: 29,419g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 84 (+2): the garrison's presence, relations with the lord
   Relations between Austria and Russia are deteriorating. Defensive Alliance may collapse in 2 turns.
   Bernadotte's resentment of Murat has cooled for now. What was settled between them at the staff table has not been.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 20
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march.
   SITUATION
   France holds 28 regions. Treasury: 29,419g (+2,490 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 18 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 16 turns idle.
   - Murat — Gascony — 13,348 — 11 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Munich — 11,407 — 5 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Mack — Bohemia — large force [partial]
   Brunswick — Artois — substantial force [partial]
   Shrapnel — Stockholm — screening force [stale - T17]
   TURN EVENTS
   Bavaria loyalty 84 (+2): the garrison's presence, relations with the lord
   Bernadotte's resentment of Murat has cooled for now. What was settled between them at the staff table has not been.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts Congreve's Rockets — artillery levies cost 15% less (×0.85).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 100.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 12 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
map: unchanged (53 labels)
```

```
#0295  type can we summon the congress?  ->  ok
  (typed and Enter)
view: <run>\frames\0295_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 20 — Early July 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=[], region_panel=no
reply: ok The Congress of Paris — ✓ 1 administrative action (you have 2); ✗ 45 titled provinces (38 of 45); ✓ Paris held; ✓ the Emperor free; ✓ no satellite on the brink of rebellion; ✓ Europe's alarm below 80 (now 45 — holding: our bloc's weight in Europe +1 against 3 of decay (one, plus one for each court at peace with us, at most three); a treaty that dissolves a league halves it); ✓ no Congress dissolved within 10 turns; ✓ 2 diplomatic points (you have 5). Not yet, Sire: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and settle). The table is on the Diplomatic Ledger's Congress tab (press D, then 7). Nothing has been relayed.
── TopBar (layer 75): unchanged
── BottomLeftUI (layer 0) [scrolled 1986 of 1986 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   20
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   29,419
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ Diplomacy]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   ► can we summon the congress?
   The Congress of Paris — ✓ 1 administrative action (you have 2); ✗ 45 titled provinces (38 of 45); ✓ Paris held; ✓ the Emperor free; ✓ no satellite on the brink of rebellion; ✓ Europe's alarm below 80 (now 45 — holding: our bloc's weight in Europe +1 against 3 of decay (one, plus one for each court at peace with us, at most three); a treaty that dissolves a league halves it); ✓ no Congress dissolved within 10 turns; ✓ 2 diplomatic points (you have 5). Not yet, Sire: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and settle). The table is on the Diplomatic 
map: unchanged (53 labels)
```

```
#0296  click End Turn (E)  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0296_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 21 — Late July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 20
   Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TopBar (layer 75) [under a modal] ──
   DP: 5/7
   Threat 45 / 100
   Turn 21 — Late July 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [⚓ 45 sail]  [Talleyrand: Courting → Prussia]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1766 of 1767 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   21
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   31,889
   Inf:
   100,000
   Cav:
   30,000
   Art:
   20,000
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ Diplomacy](disabled: Diplomacy (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 84 (+2): the garrison's presence, relations with the lord
   Relations between Austria and Russia are deteriorating. Defensive Alliance may collapse in 2 turns.
   Bernadotte's resentment of Murat has cooled for now. What was settled between them at the staff table has not been.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 20
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march.
   SITUATION
   France holds 28 regions. Treasury: 29,419g (+2,490 by the accounts)
   The courts at war hold 0 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Rhineland — 28,875 — Awaiting orders.
   - Massena — Milan — 26,239 — 18 turns idle.
   - Davout — Swabia — 17,079 — Awaiting orders.
   - Deroy — Swabia — 16,140 — Awaiting orders. Trust:40
   - Ney — Franconia — 15,795 — 16 turns idle.
   - Murat — Gascony — 13,348 — 11 turns idle.
   - Bernadotte — Franconia — 11,647 — Awaiting orders. Trust:40 Morale:57%
   - Lannes — Munich — 11,407 — 5 turns idle.
   - Napoleon — Rhineland — 6,598 — Awaiting orders.
   INTELLIGENCE
   Mack — Bohemia — large force [partial]
   Brunswick — Artois — substantial force [partial]
   Shrapnel — Stockholm — screening force [stale - T17]
   TURN EVENTS
   Bavaria loyalty 84 (+2): the garrison's presence, relations with the lord
   Bernadotte's resentment of Murat has cooled for now. What was settled between them at the staff table has not been.
   DIPLOMATIC EVENTS
   THE LAWS: Britain enacts Congreve's Rockets — artillery levies cost 15% less (×0.85).
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Talleyrand's efforts in Prussia continue. Relations now at 100.
   THE CONGRESS OF PARIS
   THE CONGRESS OF PARIS — 38 of 45 titled · summon from the Cabinet (F1)
   WAR PURPOSE
   War Purpose: Defense vs Hanover — the homeland — 28 of 28 provinces held  |  Settlement: White Peace (+0)
   COALITION THREAT
   Threat: 45/100 [Murmurs]
   Europe has watched us 12 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Russia, Britain, Austria and 3 lesser courts would march. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Quiet is a clock, Sire. Every turn we keep the peace, Europe counts — and arms."
   ════════════════════════════════════
   ► can we summon the congress?
   The Congress of Paris — ✓ 1 administrative action (you have 2); ✗ 45 titled provinces (38 of 45); ✓ Paris held; ✓ the Emperor free; ✓ no satellite on the brink of rebellion; ✓ Europe's alarm below 80 (now 45 — holding: our bloc's weight in Europe +1 against 3 of decay (one, plus one for each court at peace with us, at most three); a treaty that dissolves a league halves it); ✓ no Congress dissolved within 10 turns; ✓ 2 diplomatic points (you have 5). Not yet, Sire: The Congress cannot be summoned on 38 titled provinces — 45 are needed (7 more to win and settle). The table is on the Diplomatic 
   ► end turn
   ═══════════════════════════════════════
   TURN 21 BEGINS
   ═══════════════════════════════════════
   Income: 2585g | Charges of Empire: -329g | Rentes: -60g | Other: +1612g | Upkeep: -1338g | Net: +2470g
   Treasury: 31,889g
   Actions refreshed: 4/4
   REMINDER: Ney has +20% shock bonus ready - use it in your next attack!
   REMINDER: Davout has +20% shock bonus ready - use it in your next attack!
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 86 (+2): the garrison's presence, relations with the lord
   Territorial rivalry between Britain and Russia grows.
map names: Russia(2580,195)  Ottoman Empire(2362,788)  Prussia(2061,255)  Spain(1185,881)  Sweden(1860,83)  Saxony(2108,396)  Austria(2120,597)  France(1556,537)  Britain(1391,217)  Bavaria(1923,507)  Kingdom of Italy(1766,677)  Denmark(1738,73)  Papal States(1876,778)  Portugal(1112,816)  Naples(1802,904)  Sardinia(1642,800)  Hesse(1904,394)  Holland(1738,378)  Switzerland(1759,566)
map pieces: 100(1323,385)  45(1298,616)  37(1347,785)  20(1995,111)  18(1965,61)  15(2303,666)  12(1553,267)  10(990,803)  15(1943,203)  5(1799,839)  Shrapnel(1829,36)  Ney(1947,451)  Bernadotte(1976,425)  ?(1580,371)  Brunswick(1580,331)  Davout(1850,466)  Deroy(1879,438)  Soult(1816,387)  Napoleon(1841,360)  Murat(1445,622)  Lannes(1913,549)  Massena(1923,612)  ?(1829,135)  ?(2108,430)  ?(2057,545)  ?(1981,363)  10k(1882,642)  10k(1910,360)  25k(1556,504)  12k(1504,454)  12k(1697,412)  10k(1923,677)
```

```
#0297  quit  ->  ok
  (the engine quits)
view: <run>\frames\0297_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 21 — Late July 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase'], region_panel=no
── EnemyPhaseDialog (layer 118): unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1766 of 1767 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   REMINDER: Soult has +20% shock bonus ready - use it in your next attack!
   REMINDER: Massena has +20% shock bonus ready - use it in your next attack!
   Bavaria loyalty 86 (+2): the garrison's presence, relations with the lord
   Territorial rivalry between Britain and Russia grows.
map: unchanged (51 labels)
```

