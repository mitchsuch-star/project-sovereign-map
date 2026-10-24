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
#0001  click "Looks right"  ->  ERROR: no visible control's text holds ""Looks right""
view: <run>\frames\0001_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: -
open: screens=[], pinned=-, popups=['scale_card'], region_panel=no, other=['main_menu']
── TitleBlock (layer 0): unchanged
── StatusLine (layer 0): unchanged
── PaintingCaption (layer 0): unchanged
── VersionLine (layer 0): unchanged
── ScaleCard (layer 0): unchanged
── MenuColumn (layer 0): unchanged
```

```
#0002  click "The School of War — The Table"  ->  ERROR: no visible control's text holds ""The School of War — The Table""
view: <run>\frames\0002_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
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
#0003  click Looks right  ->  ok
  (clicked at (1960, 669))
view: <run>\frames\0003_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: -
open: screens=[], pinned=-, popups=[], region_panel=no, other=['main_menu']
── TitleBlock (layer 0): unchanged
── StatusLine (layer 0): unchanged
── PaintingCaption (layer 0) ──
   Horace Vernet — The Battle of Jena  ·  public domain
── VersionLine (layer 0): unchanged
── MenuColumn (layer 0): unchanged
```

```
#0004  click The School of War — The Table  ->  ok
  (clicked at (490, 566))
view: <run>\frames\0004_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR — THE TABLE
   1 of 7
   I. The Day After Austerlitz / Sire — Ulm and Austerlitz are on the record, Vienna is ours, and the Tsar's army is marching home by the Hungarian road. The war is now made at the table. Before you treat with Austria, hold your ally: open the Cabinet on Bavaria and send Talleyrand to REASSURE her — one diplomatic point a turn, of the five you hold; they return each morning. An ally is reassured, not …
   controls: [–]  [Skip]  <Open the Cabinet on Bavaria ▸>  <Skip this lesson ▸>
── TopBar (layer 75) ──
   DP: 5/5
   Threat 30 / 100
   Turn 1 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Moravia
   +85 ↑
   T:8
   controls: [War for Moravia]
── BottomLeftUI (layer 0) [scrolled 1279 of 1279 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,500 (+3,319 next turn)
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
   New campaign started. Your campaign autosave is untouched.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 1
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   SITUATION
   France holds 31 regions. Treasury: 2,500g (+3,319 by the accounts)
   The courts at war hold 14 regions. Estimated enemy strength: 17% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Tyrol — 42,000 — Awaiting orders.
   - Soult — Moravia — 30,000 — Awaiting orders.
   - Davout — Moravia — 26,000 — Awaiting orders.
   - Ney — Tyrol — 24,000 — Awaiting orders.
   - Murat — Vienna — 22,000 — Awaiting orders.
   - Lannes — Vienna — 18,000 — Awaiting orders.
   INTELLIGENCE
   Deroy — Munich — substantial force [partial]
   Archduke Charles — Carniola — substantial force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Austria (War for Moravia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): Total Victory (+85)
   War Purpose: Defense vs Russia (War for Moravia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 30/100 [Tension]
   At this pace the courts consult on turn 22 and declare on turn 25: Britain would march. The Balance of Europe (D) names the price to keep each court out.
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, attack Archduke Charles
   • Murat, march to Bohemia
   • recruit infantry in Vienna — 706g for 10,000 men under Lannes
   • build supply depot in Vienna — 300g
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
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
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2016,653)  France(1691,528)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)
map pieces: Archduke Charles(2016,601)  Murat(2097,501)  Lannes(2121,475)  Davout(2189,482)  Soult(2207,456)  Ney(1935,575)  Massena(1960,549)  ?(1901,540)  Deroy(1901,471)  ?(2068,435)  25k(2109,556)  ?(1894,591)  25k(1595,497)  ?(1910,645)
```

```
#0005  click Open the Cabinet on Bavaria  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0005_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 0 of 345 px] ──
   THE CABINET — Bavaria
   DP: 5
   TALLEYRAND'S ASSESSMENT — BAVARIA / Status: Alliance   Relation: +65 (Loyal) /  / "Our alliance with Bavaria stands firm. There is little to gain from change, and much to lose." / Recommendation: Talleyrand recommends: Propose Vassal /  / KEY FACTORS /   + Current relations (+30) /   + Base willingness (+10) /   + Diplomatic skill advantage (+6)
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Propose Vassal (3 DP)  —  Uncertain — a counter is likely]  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Downgrade (1 DP)]  [Back]  [Cancel]
── TutorialOverlay (layer 90) [under a modal]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1279 of 1279 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (33 labels)
```

```
#0006  scroll 1828 650 down 4  ->  ok
  (scrolled down 4 at (1828, 650))
view: <run>\frames\0006_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 0 of 345 px]: unchanged
── TutorialOverlay (layer 90) [under a modal]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1279 of 1279 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (33 labels)
```

```
#0007  scroll 1825 560 down 5  ->  ok
  (scrolled down 5 at (1825, 560))
view: <run>\frames\0007_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 85 of 341 px] ──
   THE CABINET — Bavaria
   DP: 5
   TALLEYRAND'S ASSESSMENT — BAVARIA / Status: Alliance   Relation: +65 (Loyal) /  / "Our alliance with Bavaria stands firm. There is little to gain from change, and much to lose." / Recommendation: Talleyrand recommends: Propose Vassal /  / KEY FACTORS /   + Current relations (+30) /   + Base willingness (+10) /   + Diplomatic skill advantage (+6)
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Downgrade (1 DP)]  [Reassure Ally (1 DP)  —  +4 relation/turn]  [Gather Intel (1 DP)  —  3 turns, then full intel for 5]  [Back]  [Cancel]
── TutorialOverlay (layer 90) [under a modal]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1279 of 1279 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (33 labels)
```

```
#0008  click Reassure Ally  ->  ok
  (clicked at (1825, 570))
view: <run>\frames\0008_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm', 'tutorial_overlay (not modal)'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC MISSION — Bavaria /  / "Sire, I shall begin efforts to reassure Bavaria. This will cost 1 DP per turn." /  / DP cost: 1/turn
   controls: [icon: Close (Esc) @(2151,292)]  [Begin mission]  [Not now]
── TutorialOverlay (layer 90) [under a modal]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1324 of 1324 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,500 (+3,319 next turn)
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
   ► reassure Bavaria
map: unchanged (33 labels)
```

```
#0009  click Begin mission  ->  ok
  (clicked at (1603, 727))
view: <run>\frames\0009_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR — THE TABLE
   2 of 7
   II. Every Court for Itself / A war with two courts is settled at ONE table, Sire. Open it below: the door stages Talleyrand's draft on the whole war for no diplomatic point and no action, and Bavaria's claim to the Tyrol arrives beside it — the peace itself answers her. Read the rows: Austria's reads WILL SIGN; Russia holds out, for her seat is unbeaten and a whole-war peace needs every court's co …
   controls: [–]  [Skip]  <Open the table ▸>  <Skip this lesson ▸>
── TopBar (layer 75) ──
   DP: 5/5
   Threat 30 / 100
   Turn 1 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Reassuring Ally → B...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [Talleyrand at Bavaria — Reassuring Ally]  [Recall]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Moravia
   +85 ↑
   T:8
   controls: [War for Moravia]
── BottomLeftUI (layer 0) [scrolled 1389 of 1389 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,500 (+3,319 next turn)
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
   Talleyrand begins efforts to reassure Bavaria. (1 DP/turn)
map: unchanged (33 labels)
```

```
#0010  click Open the table  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0010_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Early December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm', 'tutorial_overlay (not modal)'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 486 px] ──
   This draft will not carry as it stands. / the War for Moravia — the table with Austria + Russia - Whole-war settlement / Covered enemies: Austria, Russia / Will NOT carry as drafted — every court must reach 50. Holding out: Russia -49/50. / Treasury 2,500 gold: committed 0 / reserve 500 / remaining 2,000 / Sire, this settlement of the War for Moravia — the table with Austria + Russia seats 2 court …
   The table /   * Austria ▸ - Will sign (56/50) Demanded: Carniola + 200g /       Metternich signals that Austria will sign the settlement of the War for Moravia — the table with Austria + Russia. /       Demanded · Cede Carniola  Remove /       Demanded · 200 gold  [-][+]  Remove /       + Add demand /   * Russia ▸ - Holding out (-49/50) White peace /       Blocker: Settlement legitimacy /       Cz …
   Austria:
   Russia:
   This is the table, Sire. Every court seated here signs for itself — each must reach 50 or the draft will not carry. Demand more of a court, ease it, or drop it to fight on; a court that is ready may be taken alone. / Sire, the settlement of the War for Moravia — the table with Austria + Russia cannot be ratified now: no single dominant pressure. Revise terms or stand down before pressing further.  …
   controls: <Austria ▸>  <Remove>  <Remove>  <+ Add demand>  <Russia ▸>  <+ Add demand>  [Demand more of Austria]  [Ease Austria]  [Separate peace with Austria — alone: 68 (Favorable)]  [Demand more of Russia]  [Ease Russia]  [Drop Russia]  <Grant>  <Decline>  [Harsher terms]  [More generous]  [Submit for Review]  [Back Out]
── TutorialOverlay (layer 90) [under a modal] ──
   THE SCHOOL OF WAR — THE TABLE
   3 of 7
   III. Austria Alone / Then leave Russia at war and take Austria alone, Sire. On her row stands the chip SEPARATE PEACE WITH AUSTRIA, with the figure her envoy reads for it. Click it: the chooser says what a separate peace does to our allies — PROCEED, and Talleyrand lays the bilateral draft before you, her slice of the table in his own hand. Send it as suggested — three diplomatic points — then end …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 30 / 100
   Turn 1 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Reassuring Ally → B...]  [Envoys (1)]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
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
   2,500 (+3,319 next turn)
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
   Opening settlement review for Austria
map: unchanged (33 labels)
```

```
#0011  click Separate peace with Austria  ->  ok
  (clicked at (1866, 639))
view: <run>\frames\0011_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm', 'tutorial_overlay (not modal)'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   A separate peace, Sire, takes this one court out of the war while the rest fight on. The allies fighting beside you in it are carried in; an ally still at war with her is left fighting, and resents it. / Leave the joint settlement? / the War for Moravia — the table with Austria + Russia /  / Separate peace with Austria — every other court keeps its war. / Set aside the joint settlement; the other  …
   controls: [Proceed — separate peace with Austria]  [Stay with the joint settlement]
── TutorialOverlay (layer 90) [under a modal]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1434 of 1434 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,500 (+3,319 next turn)
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
   Directing Talleyrand: seek bilateral peace
map: unchanged (33 labels)
```

```
#0012  click Proceed  ->  ok
  (clicked at (1623, 727))
view: <run>\frames\0012_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Early December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm', 'tutorial_overlay (not modal)'], region_panel=no
── ProposalConfirmPopup (layer 110) [scrolled 0 of 530 px] ──
   PEACE PREVIEW - Austria /  / Proposed Terms / France demands: /   • Austria pays 200 gold to France /   • Austria cedes Carniola to France / Mutual: /   • Peace Treaty (end state of war) — France and Austria /   • Status quo: Moravia, Tyrol and Vienna stay ours by the treaty — titled. /  / Assessment: HARSH / Revanche lapses: Austria's cession of Carniola reconciles her Revanche while the treaty h …
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TutorialOverlay (layer 90) [under a modal]: unchanged
── TopBar (layer 75) [under a modal] ──
   DP: 5/5
   Threat 30 / 100
   Turn 1 — Early December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Reassuring Ally → B...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 1456 of 1456 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,500 (+3,319 next turn)
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
   Directing Talleyrand: confirm pair substitute
map: unchanged (33 labels)
```

```
#0013  click Send as suggested  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0013_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Early December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR — THE TABLE
   4 of 7
   IV. The Peace of Pressburg / Austria signed alone, Sire — as she did at Pressburg on the 26th of December. The Tsar would not sign and marched his army home; Britain, not on this board, fought on. The war card now reads Russia alone, and Bavaria and Italy, carried in by our peace, are at peace with Vienna too. A separate peace is the Emperor's oldest instrument: break the league one court at a tim …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75) ──
   DP: 2/5
   Threat 30 / 100
   Turn 1 — Early December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Reassuring Ally → B...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: Bavaria petitions over settlement scope @(3322,62)]  [Talleyrand at Bavaria — Reassuring Ally]  [icon: Diplomatic Action Dispatched @(3613,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War for Moravia
   +85 ↑
   T:8
   controls: [War for Moravia]
── BottomLeftUI (layer 0) [scrolled 1523 of 1523 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   2,500 (+3,319 next turn)
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
   Talleyrand departs for the Austrian court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent)
map: unchanged (33 labels)
```

```
#0014  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0014_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Late December 1805   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase', 'tutorial_overlay (not modal)'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 1
   Russia, Austria and Bavaria stirred, but their formations remain beyond our sight.
   controls: [Continue]
── TutorialOverlay (layer 90) [under a modal] ──
   THE SCHOOL OF WAR — THE TABLE
   5 of 7
   V. The Kingdom of Bavaria / Now the ally who fought beside us, Sire. Open the Cabinet on Bavaria and PROPOSE VASSALAGE: a vassal keeps her crown and her army, pays what the treaty names, and follows our wars; her LOYALTY and her AUTONOMY are the two dials of the bond — the Diplomatic Ledger's Vassals rows keep them — and only a court of half our power or less may be bound. Europe reads every treat …
   controls: [–]  [Skip]  <Propose vassalage ▸>  <Skip this lesson ▸>
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 41 / 100
   Turn 2 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Reassuring Ally → B...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2097 of 2097 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,868 (+3,136 next turn)
   Inf:
   82,400
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
   Income: 4037g | Occupation: -112g | Charges of Empire: -32g | Other: +1187g | Upkeep: -1712g | Net: +3368g
   Treasury: 5,868g
   Actions refreshed: 4/4
   PEACE SETTLEMENT: Treaty of Vienna
   Outcome: French victory after 9 turns. Final war score: +85
   Gained: Carniola
   Casualties: France 3,500 / Austria 43,000
   Terms: Austria pays 200 gold to France; Austria cedes Carniola to France; Status quo: Moravia, Tyrol and Vienna stay ours by the treaty — titled.
   Aftermath: Bavaria's war with Austria ends in this instrument; she takes nothing by it.; Our clients follow us into the peace: Kingdom of Italy (the client's war is the lord's war)
   Supply shortage at Tyrol: Ney loses 671 troops
   Supply shortage at Tyrol: Massena loses 1,175 troops
   Holland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   The Kingdom of Italy sends 7,500 men under Italian Contingent to the colours at Milan — they await the orders of France. The nearest host is Massena at Tyrol. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Austria with excellent news: they have accepted our proposal! The decisive factor was our military dominance.
   Treaty signed: At War → Peace with Austria.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2130,605)  France(1734,574)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)
map pieces: ?(2016,627)  Archduke Charles(2034,575)  Murat(2097,501)  Lannes(2121,475)  Davout(2189,482)  Soult(2207,456)  Ney(1935,575)  Massena(1960,549)  ?(1901,540)  Deroy(1901,471)  Italian Contingent(1910,601)  ?(2068,435)  25k(2135,556)  ?(1894,572)  25k(1595,497)  10k(1910,645)
```

```
#0015  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0015_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90): unchanged
── TopBar (layer 75) ──
   DP: 7/7
   Threat 41 / 100
   Turn 2 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Reassuring Ally → B...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: European Courts Concerned @(3246,64)]  [icon: Bavaria petitions over settlement scope @(3288,64)]  [Talleyrand at Bavaria — Reassuring Ally]  [Recall]  [icon: Treaty with Austria @(3639,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with Russia
   0 →
   T:9
   controls: [War with Russia]
── BottomLeftUI (layer 0) [scrolled 2208 of 2208 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,868 (+3,136 next turn)
   Inf:
   82,400
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   ► reassure Bavaria
   Directing Talleyrand: start mission
   Talleyrand begins efforts to reassure Bavaria. (1 DP/turn)
   Opening settlement review for Austria
   Directing Talleyrand: seek bilateral peace
   Directing Talleyrand: confirm pair substitute
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Austrian court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent)
   ► end turn
   ═══════════════════════════════════════
   TURN 2 BEGINS
   ═══════════════════════════════════════
   Income: 4037g | Occupation: -112g | Charges of Empire: -32g | Other: +1187g | Upkeep: -1712g | Net: +3368g
   Treasury: 5,868g
   Actions refreshed: 4/4
   PEACE SETTLEMENT: Treaty of Vienna
   Outcome: French victory after 9 turns. Final war score: +85
   Gained: Carniola
   Casualties: France 3,500 / Austria 43,000
   Terms: Austria pays 200 gold to France; Austria cedes Carniola to France; Status quo: Moravia, Tyrol and Vienna stay ours by the treaty — titled.
   Aftermath: Bavaria's war with Austria ends in this instrument; she takes nothing by it.; Our clients follow us into the peace: Kingdom of Italy (the client's war is the lord's war)
   Supply shortage at Tyrol: Ney loses 671 troops
   Supply shortage at Tyrol: Massena loses 1,175 troops
   Holland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   The Kingdom of Italy sends 7,500 men under Italian Contingent to the colours at Milan — they await the orders of France. The nearest host is Massena at Tyrol. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Austria with excellent news: they have accepted our proposal! The decisive factor was our military dominance.
   Treaty signed: At War → Peace with Austria.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 2
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — the war with Austria is over. The peace grants safe passage home.
   SITUATION
   France holds 32 regions. Treasury: 5,868g (+3,368 by the accounts)
   The courts at war hold 10 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Tyrol — 40,825 — Awaiting orders.
   - Soult — Moravia — 30,000 — Awaiting orders.
   - Davout — Moravia — 26,000 — Awaiting orders.
   - Ney — Tyrol — 23,329 — Awaiting orders.
   - Murat — Vienna — 22,000 — Awaiting orders.
   - Lannes — Vienna — 18,000 — Awaiting orders.
   - Italian Contingent — Milan — 7,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Munich — substantial force [partial]
   Archduke Charles — Carniola — substantial force [partial]
   TURN EVENTS
   Supply cost you 1,846 men, at Tyrol.
   2 satellites drifted — Holland and Switzerland.
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Austria.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Kingdom of Italy sends 7,500 men under Italian Contingent to the colours at Milan — they await the orders of France. The nearest host is Massena at Tyrol. The Kingdom of Italy pays them; their dead will be its grief.
   Moravia, Tyrol and Vienna — retained by the peace with Austria, titled by treaty.
   Sire — France and Austria have signed the Peace Treaty.
   Peace ratified between France and Austria.
   Talleyrand returns from Austria with a response.
   REVANCHE: Austria will not forgive France the loss of Carniola and 3 more provinces. A new design hardens in their court.
   DIPLOMATIC STATUS
   Sire, I believe Hanover may be ready to discuss improved relations. The diplomatic winds favor us.
   Sire, I believe Hesse may be ready to discuss improved relations. The diplomatic winds favor us.
   WAR PURPOSE
   War Purpose: Defense vs Russia (War with Russia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 41/100 [Murmurs]
   Europe has watched us 2 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: Britain would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
map: unchanged (35 labels)
```

```
#0016  click Propose vassalage  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0016_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 134 px, 0 of 504 px] ──
   THE CABINET — Bavaria
   DP: 7
   TALLEYRAND'S ASSESSMENT — BAVARIA / Status: Alliance   Relation: +64 (Loyal) /  / "Our alliance with Bavaria stands firm. There is little to gain from change, and much to lose." / Recommendation: Talleyrand recommends: Propose Vassal /  / KEY FACTORS /   + Current relations (+30) /   + Base willingness (+10) /   + Diplomatic skill advantage (+6)
   An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it.
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Cancel: Reassure Ally  —  Loyal (-1 over 0 turns)]  [Propose Vassal (3 DP)  —  Uncertain — a counter is likely]  [Declare War (1 DP)]  [Break Treaty (1 DP)](disabled: An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens i)  [Back]  [Cancel]
── TutorialOverlay (layer 90) [under a modal]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2208 of 2208 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 41/100 [Murmurs]
   Europe has watched us 2 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: Britain would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
map: unchanged (35 labels)
```

```
#0017  click Propose Vassal  ->  ok
  (clicked at (1825, 500))
view: <run>\frames\0017_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm', 'tutorial_overlay (not modal)'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Bavaria /  / France demands: /   • Bavaria pays 95 gold per turn to France for as long as the treaty stands /  / Harshness: Low / Acceptance estimate: ~46% (COUNTER expected) / Key obstacle: insufficient concessions / DP cost: 3 /  / "Sire, regarding the Vassalage proposal to Bavaria, I have prepared terms that reflect the current diplomatic climate."
   controls: [icon: Close (Esc) @(2151,292)]  [Send as suggested]  [Harsher terms]  [More generous]  [Adjust terms]  [Not Now]
── TutorialOverlay (layer 90) [under a modal]: unchanged
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 41 / 100
   Turn 2 — Late December 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Reassuring Ally → B...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
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
   5,868 (+3,136 next turn)
   Inf:
   82,400
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► propose vassalization to Bavaria
map: unchanged (35 labels)
```

```
#0018  click More generous  ->  ok
  (clicked at (2056, 674))
view: <run>\frames\0018_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Late December 1805   command line: '' (disabled)
open: screens=[], pinned=-, popups=['proposal_confirm', 'tutorial_overlay (not modal)'], region_panel=no
── ProposalConfirmPopup (layer 110) ──
   DIPLOMATIC PROPOSAL — Bavaria /  / France concedes: /   • France pays 500 gold to Bavaria /  / Harshness: Low / Acceptance estimate: ~56% (ACCEPT) / DP cost: 3 /  / "A magnanimous approach, Sire. More generous terms for Bavaria."
   controls: [icon: Close (Esc) @(2151,292)]  [Send these terms]  [Even more generous]  [Less generous]  [Not Now]
── TutorialOverlay (layer 90) [under a modal]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 2273 of 2273 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,868 (+3,136 next turn)
   Inf:
   82,400
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   Directing Talleyrand: modify generous
map: unchanged (35 labels)
```

```
#0019  click Send these terms  ->  ok
  (clicked at (1602, 674))
view: <run>\frames\0019_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 2 — Late December 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR — THE TABLE
   6 of 7
   VI. The First Stone / Bavaria is yours to protect, Sire. Her loyalty stands in the Diplomatic Ledger's Vassals rows (D) and drifts a little each turn unless it is tended — invest in her, grant her autonomy, garrison her capital, or cede her a province; what the treaty names she pays each morning, and her corps marches when we call. The first stone of the Confederation is laid. / Berthier resumes w …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75) ──
   DP: 4/7
   Threat 41 / 100
   Turn 2 — Late December 1805
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Reassuring Ally → B...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: European Courts Concerned @(3256,62)]  [icon: Bavaria petitions over settlement scope @(3298,62)]  [icon: Treaty with Austria @(3340,62)]  [icon: Peace Treaty Accepted @(3382,62)]  [Talleyrand at Bavaria — Reassuring Ally]  [icon: Diplomatic Action Dispatched @(3655,62)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with Russia
   0 →
   T:9
   controls: [War with Russia]
── BottomLeftUI (layer 0) [scrolled 1719 of 1720 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   2
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   5,868 (+3,136 next turn)
   Inf:
   82,400
   Cav:
   16,750
   Art:
   10,600
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   ═══════════════════════════════════════
   Income: 4037g | Occupation: -112g | Charges of Empire: -32g | Other: +1187g | Upkeep: -1712g | Net: +3368g
   Treasury: 5,868g
   Actions refreshed: 4/4
   PEACE SETTLEMENT: Treaty of Vienna
   Outcome: French victory after 9 turns. Final war score: +85
   Gained: Carniola
   Casualties: France 3,500 / Austria 43,000
   Terms: Austria pays 200 gold to France; Austria cedes Carniola to France; Status quo: Moravia, Tyrol and Vienna stay ours by the treaty — titled.
   Aftermath: Bavaria's war with Austria ends in this instrument; she takes nothing by it.; Our clients follow us into the peace: Kingdom of Italy (the client's war is the lord's war)
   Supply shortage at Tyrol: Ney loses 671 troops
   Supply shortage at Tyrol: Massena loses 1,175 troops
   Holland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   The Kingdom of Italy sends 7,500 men under Italian Contingent to the colours at Milan — they await the orders of France. The nearest host is Massena at Tyrol. The Kingdom of Italy pays them; their dead will be its grief.
   Talleyrand returns from Austria with excellent news: they have accepted our proposal! The decisive factor was our military dominance.
   Treaty signed: At War → Peace with Austria.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 2
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — the war with Austria is over. The peace grants safe passage home.
   SITUATION
   France holds 32 regions. Treasury: 5,868g (+3,368 by the accounts)
   The courts at war hold 10 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Tyrol — 40,825 — Awaiting orders.
   - Soult — Moravia — 30,000 — Awaiting orders.
   - Davout — Moravia — 26,000 — Awaiting orders.
   - Ney — Tyrol — 23,329 — Awaiting orders.
   - Murat — Vienna — 22,000 — Awaiting orders.
   - Lannes — Vienna — 18,000 — Awaiting orders.
   - Italian Contingent — Milan — 7,500 — Awaiting orders.
   INTELLIGENCE
   Deroy — Munich — substantial force [partial]
   Archduke Charles — Carniola — substantial force [partial]
   TURN EVENTS
   Supply cost you 1,846 men, at Tyrol.
   2 satellites drifted — Holland and Switzerland.
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Austria.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   The Kingdom of Italy sends 7,500 men under Italian Contingent to the colours at Milan — they await the orders of France. The nearest host is Massena at Tyrol. The Kingdom of Italy pays them; their dead will be its grief.
   Moravia, Tyrol and Vienna — retained by the peace with Austria, titled by treaty.
   Sire — France and Austria have signed the Peace Treaty.
   Peace ratified between France and Austria.
   Talleyrand returns from Austria with a response.
   REVANCHE: Austria will not forgive France the loss of Carniola and 3 more provinces. A new design hardens in their court.
   DIPLOMATIC STATUS
   Sire, I believe Hanover may be ready to discuss improved relations. The diplomatic winds favor us.
   Sire, I believe Hesse may be ready to discuss improved relations. The diplomatic winds favor us.
   WAR PURPOSE
   War Purpose: Defense vs Russia (War with Russia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 41/100 [Murmurs]
   Europe has watched us 2 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: Britain would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "The treaty gives them the road, Sire, not the rations. They should be walking it."
   ════════════════════════════════════
   ► propose vassalization to Bavaria
   Directing Talleyrand: modify generous
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Bavarian court with your Vassalage proposal. Expect a response by next turn. (3 DP spent)
map: unchanged (35 labels)
```

```
#0020  click End Turn  ->  ok
  (clicked at (937, 978))
view: <run>\frames\0020_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Early January 1806   command line: '' (focused) (disabled)
open: screens=[], pinned=-, popups=['enemy_phase', 'tutorial_overlay (not modal)'], region_panel=no
── EnemyPhaseDialog (layer 118) ──
   ENEMY PHASE - Turn 2
   BAVARIA / ──────────────────────────── / - Deroy holds position /  / ──────────────────────────── / Russia and Austria stirred as well, but their formations remain beyond our sight.
   controls: [Continue]
── TutorialOverlay (layer 90) [under a modal] ──
   THE SCHOOL OF WAR — THE TABLE
   7 of 7
   VII. The Lesson Ends / Three acts in three turns, Sire: a mission, a separate peace, a vassal. Every screen you opened here keeps its first note for the great campaign — the Cabinet, the table, the chooser — and the roads of the Empire wait there under the Cabinet. The real war of 1805 is at the main menu under BEGIN. /   Conclude the lesson
   controls: [–]  [Skip]  <Conclude the lesson>
── TopBar (layer 75) [under a modal] ──
   DP: 7/7
   Threat 46 / 100
   Turn 3 — Early January 1806
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Reassuring Ally → B...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── BottomLeftUI (layer 0) [under a modal] [scrolled 2163 of 2163 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,545 (+3,034 next turn)
   Inf:
   84,700
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled)  [⚖ The Cabinet](disabled: The Cabinet (F1) — treat with ANY nation: allies, neutrals, or enemies)  [End Turn (E)](disabled: End your turn and let enemies move)
── MapControls (layer 0) [under a modal]: unchanged
── command window, new lines ──
   ► end turn
   ═══════════════════════════════════════
   TURN 3 BEGINS
   ═══════════════════════════════════════
   Income: 4140g | Occupation: -90g | Charges of Empire: -129g | Other: +1068g | Upkeep: -2312g | Net: +2677g
   Treasury: 8,545g
   Actions refreshed: 4/4
   Construction complete: Market in Carniola!
   Bavaria completes a market at Munich.
   Supply shortage at Tyrol: Ney loses 631 troops
   Supply shortage at Tyrol: Massena loses 1,105 troops
   Holland loyalty 96 (-2): satellite drift
   Kingdom of Italy loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 96 (-2): satellite drift
   Italian Contingent's contingent comes home — 7,500 of 7,500 men.
   Talleyrand returns from Bavaria with excellent news: they have accepted our proposal! The decisive factor was goodwill between our nations.
   Treaty signed: Alliance → Vassal with Bavaria.
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2130,605)  France(1734,574)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)
map pieces: ?(2025,481)  Archduke Charles(2024,443)  Murat(2097,501)  Lannes(2121,475)  Davout(2189,482)  Soult(2207,456)  Ney(1935,575)  Massena(1960,549)  Deroy(1891,535)  25k(2109,556)  10k(1893,591)  25k(1595,497)  ?(1910,645)
```

```
#0021  click Continue  ->  ok
  (clicked at (1829, 719))
view: <run>\frames\0021_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90): unchanged
── TopBar (layer 75) ──
   DP: 7/7
   Threat 46 / 100
   Turn 3 — Early January 1806
   Imperial Box
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Reassuring Ally → B...]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]  [icon: European Courts Concerned @(3202,64)]  [icon: Bavaria petitions over settlement scope @(3244,64)]  [Talleyrand at Bavaria — Reassuring Ally]  [Recall]  [icon: Treaty with Bavaria @(3597,64)]  [icon: Vassalage Accepted @(3638,64)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with Russia
   0 →
   T:10
   controls: [War with Russia]
── BottomLeftUI (layer 0) [scrolled 1743 of 1743 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   3
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   8,545 (+3,034 next turn)
   Inf:
   84,700
   Cav:
   18,500
   Art:
   11,200
   (Type command...)
   controls: [+]  [−]  [—]  [Execute](disabled: Type an order first)  [⚖ The Cabinet]  [End Turn (E)]
── MapControls (layer 0): unchanged
── command window, new lines ──
   [...earlier messages trimmed...]
   Directing Talleyrand: execute proposal
   Talleyrand departs for the Bavarian court with your Vassalage proposal. Expect a response by next turn. (3 DP spent)
   ► end turn
   ═══════════════════════════════════════
   TURN 3 BEGINS
   ═══════════════════════════════════════
   Income: 4140g | Occupation: -90g | Charges of Empire: -129g | Other: +1068g | Upkeep: -2312g | Net: +2677g
   Treasury: 8,545g
   Actions refreshed: 4/4
   Construction complete: Market in Carniola!
   Bavaria completes a market at Munich.
   Supply shortage at Tyrol: Ney loses 631 troops
   Supply shortage at Tyrol: Massena loses 1,105 troops
   Holland loyalty 96 (-2): satellite drift
   Kingdom of Italy loyalty 98 (-2): satellite drift — Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
   Switzerland loyalty 96 (-2): satellite drift
   Italian Contingent's contingent comes home — 7,500 of 7,500 men.
   Talleyrand returns from Bavaria with excellent news: they have accepted our proposal! The decisive factor was goodwill between our nations.
   Treaty signed: Alliance → Vassal with Bavaria.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 3
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — Ney and Massena stand 62,418 men at Tyrol, which feeds 30,000. 32,418 too many. 3,582 men lost in 2 turns. A supply depot at Tyrol would ease it; Milan can feed 75,000 more and Franconia can feed 60,000 more — a corps marched there ends it.
   • Sire — the war with Austria is over. The peace grants safe passage home.
   SITUATION
   France holds 32 regions. Treasury: 8,545g (+3,177 by the accounts)
   The courts at war hold 10 regions. Estimated enemy strength: 0% of French forces (no enemy corps in view — the figure counts nothing).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Massena — Tyrol — 39,720 — Awaiting orders.
   ⚠ Starving — supply has failed at Tyrol two turns running.
   - Soult — Moravia — 30,000 — Awaiting orders.
   - Davout — Moravia — 26,000 — Awaiting orders.
   - Ney — Tyrol — 22,698 — Awaiting orders.
   ⚠ Starving — supply has failed at Tyrol two turns running.
   - Murat — Vienna — 22,000 — Awaiting orders.
   - Deroy — Munich — 22,000 — Awaiting orders. Trust:40
   - Lannes — Vienna — 18,000 — Awaiting orders.
   INTELLIGENCE
   Archduke Charles — Bohemia — substantial force [partial]
   TURN EVENTS
   Construction complete: Market in Carniola!
   Supply cost you 1,736 men, at Tyrol.
   3 satellites drifted — Holland, Kingdom of Italy and Switzerland.
   DIPLOMATIC EVENTS
   Talleyrand has departed for the court of Bavaria.
   Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
   Italian Contingent's contingent comes home — 7,500 of 7,500 men.
   Bavaria has been established under the protection of France.
   Sire — France and Bavaria have signed the Vassalage.
   Talleyrand returns from Bavaria with a response.
   PEACE SETTLEMENTS
   The Treaty of Vienna
   France and Austria have concluded peace after 9 turns of war. France gained Carniola. Final war score: +85.
   DIPLOMATIC STATUS
   Sire, I believe Naples may be ready to discuss improved relations. The diplomatic winds favor us.
   Sire, I believe Ottoman may be ready to discuss improved relations. The diplomatic winds favor us.
   WAR PURPOSE
   War Purpose: Defense vs Russia (War with Russia) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   COALITION THREAT
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: Britain would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (32 labels)
```

```
#0022  click Conclude the lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0022_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Early January 1806   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1743 of 1743 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: Britain would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (32 labels)
```

```
#0023  key Escape  ->  ok
  (pressed Escape)
view: <run>\frames\0023_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1743 of 1743 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: Britain would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (32 labels)
```

```
#0024  click_at 3635 18  ->  ok
  (clicked at (3635, 18) on MenuBtn  (Button, layer 75))
view: <run>\frames\0024_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 3 — Early January 1806   command line: ''
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1743 of 1743 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   Threat: 46/100 [Murmurs]
   Europe has watched us 3 quiet turns. At this pace the courts consult on turn 22 and declare on turn 25: Britain would march. Bound for now by a fresh peace: Austria. The Balance of Europe (D) names the price to keep each court out.
   Berthier: "Men lost to the roads are lost for nothing, Sire. Either the province feeds them or we spread them."
   ════════════════════════════════════
map: unchanged (32 labels)
```

```
#0025  click Main Menu  ->  ok
  (clicked at (1829, 637))
view: <run>\frames\0025_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: -
open: screens=[], pinned=-, popups=[], region_panel=no, other=['main_menu']
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
── MenuColumn (layer 0) ──
   controls: [Return to the War Room]  [Begin the 1805 Campaign]  [The School of War — a guided campaign]  [The School of War — The Table (a guided peace)]  [Continue](disabled: No saved campaign yet)  [Load a Campaign…](disabled: No saved campaign yet)  [Settings]  [Quit to Desktop]
```

```
#0026  click The School of War — a guided campaign  ->  ok
  (clicked at (490, 566))
view: <run>\frames\0026_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: -
open: screens=[], pinned=-, popups=[], region_panel=no, other=['main_menu']
── TitleBlock (layer 0): unchanged
── MenuColumn (layer 0) ──
   Enter the School of War? Your running campaign leaves the table.
   controls: [Return to the War Room]  [Begin the 1805 Campaign]  [Confirm — to school]  [Keep my campaign]  [The School of War — a guided campaign]  [The School of War — The Table (a guided peace)]  [Continue](disabled: No saved campaign yet)  [Load a Campaign…](disabled: No saved campaign yet)  [Settings]  [Quit to Desktop]
── StatusLine (layer 0): unchanged
── PaintingCaption (layer 0): unchanged
── VersionLine (layer 0): unchanged
```

```
#0027  click Confirm — to school  ->  ok
  (clicked at (368, 592))
view: <run>\frames\0027_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   1 of 20
   I. The Situation / Sire — Austria has pushed two corps over the Iller while her main army musters at Vienna. Before orders, knowledge. Every command is TYPED into the line below: Tab completes a half-typed order, and clicking any province on the map offers its orders as chips. Lost for words? Type what can I do, status or help; Esc is the pause menu. Ask the treasury for its books first — it costs …
   controls: [–]  [Skip]  <✎ economy>  <Skip this lesson ▸>
── TopBar (layer 75) ──
   DP: 5/5
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with Austria
   0 →
   T:0
   controls: [War with Austria]
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   900 (+3,755 next turn)
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
   New campaign started. Your campaign autosave is untouched.
   ════════════════════════════════════
   MORNING DISPATCH — Turn 1
   Chief of Staff Berthier reporting
   ════════════════════════════════════
   Sire — the establishment stands 26,000 men under the ordinance, and the depots hold 80,000. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them.
   SITUATION
   France holds 28 regions. Treasury: 900g (+3,755 by the accounts)
   The courts at war hold 7 regions. Estimated enemy strength: 10% of French forces (an estimate — 1 of 1 known corps read from stale reports; unscouted armies are not counted).
   Your authority: 100 (Strong)
   MARSHAL STATUS
   - Soult — Paris — 40,000 — Awaiting orders.
   - Davout — Lorraine — 26,000 — Awaiting orders.
   - Ney — Rhineland — 24,000 — Awaiting orders.
   + Senarmont — Franche-Comte — 14,000 — Artillery at Franche-Comte.
   INTELLIGENCE
   Kienmayer — Swabia — small force [partial]
   WAR PURPOSE
   War Purpose: Defense vs Austria (War with Austria) — the homeland — 28 of 28 provinces held  |  Settlement (this pair): White Peace (+0)
   TODAY
   Orders the board will take at once — choose among them; they share one treasury and one army:
   • Ney, attack Kienmayer
   • Davout, march to Rhineland
   • recruit infantry in Paris — 450g for 10,000 men under Soult
   • build supply depot in Rhineland — 300g
   Type 'what can I do' for the orders this board will take, 'status' for the state of the board, or 'help' for the full command reference.
   For any matter of state, press F1 for the Cabinet.
   Berthier: "The depots are full and the ordinance allows it, Sire. Conscripts do not improve with keeping."
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
map pieces: ?(1859,469)  Kienmayer(1859,430)  Ney(1826,397)  Davout(1753,436)  Senarmont(1813,497)  Soult(1596,442)  12k(1813,580)  ?(1901,591)  ?(1893,372)  25k(1595,494)  ?(1769,580)
```

```
#0028  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0028_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   2 of 20
   II. The Army Marches / You hold 4 command actions and 2 administrative actions each turn — the counters stand above. A march costs one command action. Send Senarmont's guns forward through allied Bavaria — an ALLIANCE opens the road. Two orders may share a line: 'march to Munich then attack' engages whoever holds the ground on arrival, and any other second order is handed back to your line for you …
   controls: [–]  [Skip]  <✎ Senarmont, move to Munich>  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0029  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0029_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   3 of 20
   III. The Day Closes / Spend what actions you please, Sire — then close the day. The enemy moves when you have finished, and my morning dispatch reports what changed overnight. Whatever needs your answer afterwards — a letter, a grievance, a reward owed — waits on the notice rail at the top of the screen. /   ✎ end turn   / Click the quill to place the order on your command line — you give the word …
   controls: [–]  [Skip]  <✎ end turn>  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0030  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0030_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   4 of 20
   IV. The Marshal's Temper / Your marshals are men, not pieces — and a man may PUSH BACK against an order that offends his character: the aggressive marshal hates to sit still, the cautious one hates long odds, the literal one does exactly as told and never argues. Order Ney — who smells the enemy across the border — onto the DEFENSIVE, and hear what the bravest of the brave thinks of that. / Berthi …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0031  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0031_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   5 of 20
   V. Trust, Insist, Compromise / He objects — as he should. Answer on the card before you: Trust to let him have his way, Proceed as Ordered to be obeyed at a price in trust, or Compromise to meet him halfway. TRUST is the currency of command — his card (G) shows the figure. Yield to him and it rises; overrule him and it falls. A marshal whose trust runs low may DEFY you — refuse an order, or act on …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0032  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0032_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   6 of 20
   VI. The Guns Speak / Senarmont's batteries at Munich range the Tyrol passes, where Jellacic digs in. Artillery fires one province distant — but never on the day it marched; the guns must be laid. Bombard him while he still holds the pass; Austria rotates her corps within days. Should he slip away first, any enemy corps one province out serves the lesson — or end the turn and the school will move o …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0033  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0033_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   7 of 20
   VII. The Cabinet / War is also made at the table. Press F1 — the Cabinet — or click below: choose Austria and send Talleyrand to GATHER INTELLIGENCE. For five turns her armies stand revealed to you, at one diplomatic point a turn (you hold 5; they return each turn). Confirm on the card that follows. From the same door you propose peace, alliances and open borders, hire a court's neutrality, or rea …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0034  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0034_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   8 of 20
   VIII. First Blood / Now the sword. Kienmayer's screen still stands across the Rhine on allied Bavarian soil — Ney carries three times their number. Attack, and read the battle report that follows: terrain, casualties, and the temper of the men. Then occupy Swabia (Ney, move to Swabia); if the move is refused, his corps still stands — beaten men must be broken, so strike again before you walk in. / …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0035  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0035_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   9 of 20
   IX. The Marshalate / Read the MUSTER before every battle: it names who WILL JOIN, who WILL NOT, and why — ask what if Ney attacks Mack and Berthier reads it for nothing, before you commit. Your marshals are men with histories — press G: each card shows his TRUST in you, his GLORY, his skills, and whom he loves and hates. Ney and Soult are at odds; two marshals at odds bring half their weight to a  …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0036  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0036_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   10 of 20
   X. Standing Orders / For distant objectives, give a STANDING order — it costs 2 command actions and executes itself each morning until done. March Davout for Franconia, two provinces east; watch the later legs move without you at dawn (he routes around enemies on his own). Every standing order stands on the map as an ARROW along the road still to march, its clock on the badge — click the arrow to  …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0037  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0037_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   11 of 20
   XI. Conquest / Bohemia is Austrian soil, one march past Franconia. When Davout reaches the border, march in and it is yours (Davout, move to Bohemia); if an Austrian corps holds it, the refusal names him — attack that name, and the battle that breaks the last of them hands you the province. Should Austria mass there in strength, any Austrian province serves the lesson — the battered Tyrol will do  …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0038  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0038_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   12 of 20
   XII. The Conqueror's Choice / The province is yours, Sire — now choose its fate on the card before you: PLUNDER for gold now and a hostile countryside after, or SECURE for order and income that lasts. On an allied front, I counsel SECURE. Conquered soil costs upkeep to hold until it settles — the treasury's Occupation line — and every conquest raises Europe's alarm against you. / Berthier resumes  …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0039  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0039_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   13 of 20
   XIII. The Depots / War eats men and gold. Your 2 ADMINISTRATIVE actions recruit and build: raise infantry for Soult at Paris — the price is war-inflated, the capital discounts it, and clicking Paris on the map offers the same levy as a priced chip — then spend the second on build watchtower in Lorraine to watch the frontier. / Berthier resumes with the morning dispatch — end the turn when ready. / …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0040  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0040_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   14 of 20
   XIV. The Fog / You see only what your armies and towers see. Austria's main body is stirring — scout toward Bohemia and find it before it finds you. From here the school only advises, Sire; the war is yours. / Berthier resumes with the morning dispatch — end the turn when ready. / You skipped the last page — the school moves on. /   Skip this lesson ▸
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0041  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0041_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   15 of 20
   XV. The Counter-Blow / Charles and Schwarzenberg have been on you since the second morning — fifty thousand of them, and they will keep coming. Mountains favor the defender; so do earthworks (Ney, fortify) and a garrison detachment. Stand where the ground is strong and let them bleed on it — but not too many men on poor ground: a province feeds only so many, and a corps that outstays its supply st …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0042  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0042_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   16 of 20
   XVI. The Wooden Wall / There is no fleet in this lesson — the Danube is a river war — but the great campaign is fought against a sea power. Britain's Royal Navy holds the Channel: NO army crosses water she commands, and the map draws such a crossing SHUT in crimson (an open one is a dashed route). The ledger's seventh book, THE ADMIRALTY (T, then 7), shows your fleets and their readiness, the yard …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0043  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0043_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   17 of 20
   XVII. The Congress of Paris / The great campaign does not end when the last army breaks, Sire — it ends when EUROPE SIGNS. Hold forty-five provinces by TITLE — your own soil, what a treaty cedes or leaves in your hands (a signed peace titles what you keep of the loser's), a client's loyal homeland, or a conquest held twelve quiet turns — and you may summon the CONGRESS OF PARIS from the Cabinet (F …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0044  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0044_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   18 of 20
   XVIII. The Laws of State / The treasury buys more than muskets, Sire: it buys LAWS — acts of state, paid once and then every turn. The ledger's eighth book, THE LAWS (T, then 8), lists ours: what each does in numbers, its price, its upkeep, and whether we may enact it now. The Grand Quartier Général is the one road to a FIFTH order of the day — 9,000 gold, then 300 a turn. Say enact the Staff: the …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0045  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0045_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   19 of 20
   XIX. The Instruments / Everything I have taught has a screen: T the Strategic Ledger (eight books — forces, land, treasury, intelligence, manpower, orders, the Admiralty, the laws), G your Generals, D the courts of Europe, R my morning dispatch again, L the campaign log, N Le Moniteur. Hold Alt with the letter while you type. The treasury now carries occupation costs and the charges of empire — re …
   controls: [–]  [Skip]  <Skip this lesson ▸>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0046  click Skip this lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0046_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'tutorial_overlay (not modal)'], region_panel=no
── TutorialOverlay (layer 90) ──
   THE SCHOOL OF WAR
   20 of 20
   XX. The Lesson Ends / That is the whole of the craft, Sire: orders, temper, battle, conquest, coin — and the courts beyond. The real war of 1805 waits at the main menu under BEGIN. Hold this little front as long as it amuses you. / Berthier resumes with the morning dispatch — end the turn when ready. / You skipped the last page — the school moves on. /   Conclude the lesson
   controls: [–]  [Skip]  <Conclude the lesson>
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0047  click Conclude the lesson  ->  ok
  (pressed the link by its own road (meta_clicked))
view: <run>\frames\0047_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75): unchanged
── WarStatusPanel (layer 25): unchanged
── BottomLeftUI (layer 0) [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0): unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0048  click_at 3635 18  ->  ok
  (clicked at (3635, 18) on MenuBtn  (Button, layer 75))
view: <run>\frames\0048_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)', 'pause_menu'], region_panel=no
── PauseMenu (layer 120) ──
   CAMPAIGN MENU
   Ink & Iron — 0.1.0 early build
   controls: [Resume (Esc)]  [Save Game]  [Load Game]  [New Campaign]  [Settings]  [Main Menu]  [Quit to Desktop]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 1147 of 1147 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
map: unchanged (31 labels)
```

```
#0049  click Main Menu  ->  ok
  (clicked at (1829, 637))
view: <run>\frames\0049_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: -
open: screens=[], pinned=-, popups=[], region_panel=no, other=['main_menu']
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
── MenuColumn (layer 0) ──
   controls: [Return to the War Room]  [Begin the 1805 Campaign]  [The School of War — a guided campaign]  [The School of War — The Table (a guided peace)]  [Continue](disabled: No saved campaign yet)  [Load a Campaign…](disabled: No saved campaign yet)  [Settings]  [Quit to Desktop]
```

```
#0050  click Begin the 1805 Campaign  ->  ok
  (clicked at (490, 504))
view: <run>\frames\0050_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: -
open: screens=[], pinned=-, popups=[], region_panel=no, other=['main_menu']
── TitleBlock (layer 0): unchanged
── MenuColumn (layer 0) ──
   Begin anew? The autosave of your running campaign is replaced.
   controls: [Return to the War Room]  [Begin the 1805 Campaign]  [Confirm — begin anew]  [Keep my campaign]  [The School of War — a guided campaign]  [The School of War — The Table (a guided peace)]  [Continue](disabled: No saved campaign yet)  [Load a Campaign…](disabled: No saved campaign yet)  [Settings]  [Quit to Desktop]
── StatusLine (layer 0): unchanged
── PaintingCaption (layer 0): unchanged
── VersionLine (layer 0): unchanged
```

```
#0051  click Confirm — begin anew  ->  ok
  (clicked at (378, 592))
view: <run>\frames\0051_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['war_status_panel (not modal)'], region_panel=no
── TopBar (layer 75) ──
   DP: 5/5
   Turn 1 — Late September 1805
   controls: [Event Log (L)]  [Ledger (T)]  [Generals (G)]  [Diplomacy (D)]  [Dispatch (R)]  [Moniteur (N)]  [Talleyrand: Idle]  [Envoys]  [icon: Menu — Save, Load, Settings (Esc) @(3635,18)]
── WarStatusPanel (layer 25) ──
   ACTIVE WARS
   War with Austria
   0 →
   T:0
   controls: [War with Austria]
── BottomLeftUI (layer 0) [scrolled 552 of 552 px] ──
   ⚔ IMPERIAL COMMAND ⚔
   Scale
   Turn:
   1
   Actions:
   4/4
   Admin:
   2/2
   Gold:
   900
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
   • "scout Swabia" or "move to Flanders"
   • "what can I do" (Berthier names the orders the board takes today) or "end turn"
   • Ask Berthier: "who am I fighting", "is Paris safe", "what happened last turn" — an answer costs no action
   • Diplomacy: click [Diplomacy] (or press F1) to treat with ANY nation — allies, neutrals, or enemies, not only those you fight
   • Generals: press G to review your marshals — their loyalty, rewards (duchies & rentes), and grievances
   • Map: Alt+M cycles view (blended / political / terrain), Alt +/- zoom, Alt+Home recenters; Alt+` hides the terminal — the bare keys work whenever you are not typing
   • Map orders: with nothing typed, click one of your marshals (or drag his piece) — his roads light up — then a province, an enemy or another marshal: a card shows the exact order before it goes
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Starting a new campaign. Current autosave will be replaced.
   New campaign failed: New game failed: Invalid scenario: moments.deck[1].voice: Must name a speaker of ['cabinet', 'talleyrand', 'envoy']
map names: Russia(2471,232)  Ottoman Empire(2285,740)  Prussia(2103,310)  Spain(1277,819)  Sweden(1895,93)  Saxony(2068,404)  Austria(2078,576)  France(1596,525)  Bavaria(1909,499)  Kingdom of Italy(1774,645)  Denmark(1751,128)  Papal States(1869,731)  Portugal(1216,764)  Britain(1459,315)  Hanover(1741,350)  Naples(1806,839)  Sardinia(1669,750)  Hesse(1893,403)  Holland(1751,389)  Switzerland(1769,549)
map pieces: ?(1859,469)  Kienmayer(1859,430)  Ney(1826,397)  Davout(1753,436)  Senarmont(1813,497)  Soult(1596,442)  12k(1813,580)  ?(1901,591)  ?(1893,372)  25k(1595,494)  ?(1769,580)
```

```
#0052  key F1  ->  ok
  (pressed F1)
view: <run>\frames\0052_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 584 px] ──
   THE CABINET
   DP: 5
   "Your Excellency, which nation requires our diplomatic attention?"
   At War (1)
   Treaties (1)
   Vassals (3)
   ▼ more below
   controls: [icon: Close (Esc) @(2075,284)]  [Formable Nations — states that could yet exist]  [Austria  —  At War  |  -70 (Hostile)]  [Bavaria  —  Alliance  |  +60 (Loyal)]  [Holland  —  Vassal  |  0 (Neutral)]  [Kingdom of Italy  —  Vassal  |  0 (Neutral)]  [Switzerland  —  Vassal  |  0 (Neutral)]  [Cancel]
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 552 of 552 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Starting a new campaign. Current autosave will be replaced.
   New campaign failed: New game failed: Invalid scenario: moments.deck[1].voice: Must name a speaker of ['cabinet', 'talleyrand', 'envoy']
map: unchanged (31 labels)
```

```
#0053  quit  ->  ok
  (the engine quits)
view: <run>\frames\0053_view.jpg   (a view-JPEG pixel x 1.4285 = logical px; if your viewer shows it 2000 px wide, x 1.8285; screen [3657.0, 1028.0] logical)
turn: Turn 1 — Late September 1805   command line: '' (focused)
open: screens=[], pinned=-, popups=['diplomacy_wizard', 'war_status_panel (not modal)'], region_panel=no
── DiplomacyWizard (layer 110) [scrolled 0 of 584 px]: unchanged
── TopBar (layer 75) [under a modal]: unchanged
── WarStatusPanel (layer 25) [under a modal]: unchanged
── BottomLeftUI (layer 0) [under a modal] [scrolled 552 of 552 px]: unchanged
── MapControls (layer 0) [under a modal]: unchanged
── command window, last lines ──
   • The war table: every standing order is an arrow on the map — click it to cancel or change it; . (Alt+. while typing) finds the next marshal with nothing to do; Ctrl-click several marshals, then a province, to march them together on one card
   ─────────────────────────────────────
   Starting a new campaign. Current autosave will be replaced.
   New campaign failed: New game failed: Invalid scenario: moments.deck[1].voice: Must name a speaker of ['cabinet', 'talleyrand', 'envoy']
map: unchanged (31 labels)
```

