================================================================
        INK & IRON — PLAYTEST BUILD
        A Napoleonic Strategy Game
================================================================

You command Napoleon's marshals through written orders.
They have personalities — and they don't always obey.

================================================================
  INSTALLATION & SETUP
================================================================

REQUIREMENTS:
  - Windows 10 or 11
  - Internet connection (the AI needs it to process commands)
  - An Anthropic API key (Mitch will provide one, or get
    your own at https://console.anthropic.com/)

SETUP:
  1. Unzip this folder anywhere (Desktop is fine)
  2. Open config.txt in Notepad
  3. Replace "your_key_here" with the API key:
       ANTHROPIC_API_KEY=sk-ant-abc123...
  4. Save and close config.txt

HOW TO LAUNCH:
  Double-click launch.bat

  Two windows will open:
    - A server window (minimized in taskbar) — DON'T close it
    - The game window

  When you're done, close the game window. The server
  shuts down automatically.

================================================================
  CONTROLS
================================================================

TYPE COMMANDS in the terminal at the bottom of the screen.
Press Enter to send.

HOTKEYS:
  F1  — Diplomacy wizard (propose treaties, negotiate)
  D   — Morning Dispatch (turn briefing)
  T   — Strategic Ledger (forces, economy, orders)
  G   — Generals (marshal stats, trust, relationships)
  L   — Campaign Log (history of events)
  E   — End Turn
  Esc — Pause Menu

================================================================
  HOW TO PLAY
================================================================

THE BASICS:
  You are Napoleon. You command marshals by typing orders
  in natural language:

    "Ney, attack Wellington"
    "Davout, move to Bavaria"
    "Drouot, bombard the enemy at Belgium"
    "end turn"

  Each turn you have a limited number of Action Points (AP).
  Most actions cost 1-2 AP. When you're done, type "end turn"
  or press E.

  After your turn, enemy nations move. Then you get a Morning
  Dispatch (press D to re-read) briefing you on what happened.

YOUR MARSHALS:
  Each marshal has a personality that affects how they fight
  and whether they'll follow your orders.

  NEY (Cavalry, Aggressive)
    Wants to charge. Objects to defensive orders. Gains
    "recklessness" from winning — at level 4 he auto-charges
    without orders. Devastating on attack (+15%), fragile
    on defense. Cavalry shreds artillery units (+30%).

  DAVOUT (Infantry, Cautious)
    The best defender in the game (+20% defense in stance).
    Objects to risky attacks, especially when outnumbered.
    Can counter-punch after defending successfully.

  DROUOT (Artillery)
    Cannot move and attack in the same turn. Use bombardment
    to soften enemies before assault. +10% fort degradation.
    Passive overwatch: -3% to any enemy attacking a region
    where Drouot is stationed.

  GROUCHY (Infantry, Literal)
    Follows orders exactly. Never improvises. Gets +15%
    defense while holding position. Good for anchoring a
    front line. Won't object much.

  BERTHIER (Advisor)
    Chief of staff. Provides battle reports after combat
    with analysis of what happened and why.

AVAILABLE COMMANDS:
  attack / charge    — Attack an adjacent enemy
  defend / hold      — Dig in and prepare for assault
  move               — Advance to an adjacent region
  retreat            — Fall back from current position
  scout              — Gather intel on a distant region
  wait               — Do nothing this turn
  drill              — 2-turn prep for +20% attack bonus
  fortify            — Build earthworks (+2-3% def/turn, max ~15%)
  form square        — Anti-cavalry formation (details below)
  garrison           — Leave troops to defend a region
  recruit            — Raise new troops (costs gold)
  bombardment        — Artillery softens enemy (Drouot only)
  stance aggressive  — +15% attack, -10% defense
  stance defensive   — -10% attack, +15% defense
  stance neutral     — Reset to baseline
  end turn           — Finish your turn

STRATEGIC COMMANDS (multi-turn, autonomous):
  "Ney, march to Berlin"     — Move across multiple regions
  "Davout, pursue Blucher"   — Chase a fleeing enemy
  "Grouchy, hold Bavaria"    — Fortify and defend a region
  "Drouot, support Ney"      — Follow and assist an ally

  These persist across turns. Cancel with "cancel" (costs 1 AP).
  Any tactical command (attack, defend, etc.) overrides them.

================================================================
  WHEN MARSHALS DISOBEY
================================================================

If you order something against a marshal's nature, they object.
Ney hates defending. Davout hates reckless attacks.

Three levels:

  MILD — Marshal grumbles but obeys automatically.
    "I'd rather attack, but... fine."

  MAJOR — You must choose:
    [Trust]      Accept their judgment. +12 trust.
                 They suggest an alternative action.
    [Insist]     Override them. -10 trust if they obey,
                 -15 if they refuse outright.
    [Compromise] Split the difference. +3 trust.

  DEFIANCE — After you Insist, they may refuse entirely
    (5-35% chance based on trust). They do something else.

TRUST (0-100, starts at 70):
  High trust (80+) = fewer objections, reliable execution.
  Low trust (<20) = frequent defiance, unreliable marshals.

  Build trust by listening to objections (Trust option).
  Destroy trust by constantly overriding (Insist option).

  Tip: Your marshals often know what they're doing. Trusting
  them early builds a reserve of goodwill for when you really
  need to override them later.

================================================================
  COMBAT
================================================================

When you order an attack, combat resolves immediately.
Both sides take casualties based on troop strength and
modifiers. If morale drops below 25%, the loser retreats.
If morale hits 0%, the army is "broken" — teleports to
capital and needs 4 turns to recover.

KEY MODIFIERS:
  Terrain (defender bonus):
    Plains     +0%    Cavalry thrives here
    Hills      +15%   Moderate advantage
    Forest     +10%   Cavalry struggles
    Urban      +20%   City fighting
    Mountains  +25%   Strongest defense, cavalry useless
    River      +15%   Crossing penalty

  Stance:
    Aggressive   +15% attack, -10% defense
    Defensive    -10% attack, +15% defense

  Drill:         +20% attack (first battle only after 2-turn prep)
  Fortification: Up to +15% defense (builds over multiple turns)
  Square:        Cavalry -40% damage, artillery +50% damage

THE TACTICAL TRIANGLE:

  Three formations counter each other:

  CAVALRY beats ARTILLERY
    Cavalry gets +30% damage vs artillery units.
    Artillery can't move and attack same turn — vulnerable
    to fast cavalry strikes.

  ARTILLERY beats SQUARE
    Square formation gives +50% bonus to artillery damage.
    Infantry in square are sitting ducks for bombardment.

  SQUARE beats CAVALRY
    Square formation cuts cavalry attack damage by 40%.
    The classic anti-cavalry defense.

  Use this to your advantage:
    - Enemy has cavalry? Form square with your infantry.
    - Enemy in square? Bombard with Drouot.
    - Enemy is artillery? Charge with Ney.

  OVERWATCH:
    Friendly artillery in a region passively penalizes
    attackers by -3% per artillery unit. Just having Drouot
    nearby protects your forces.

================================================================
  DIPLOMACY
================================================================

Press F1 to open the Diplomacy Wizard.

HOW IT WORKS:
  1. Pick a nation (categorized by relationship)
  2. Pick an action (shows acceptance likelihood)
     Green  = "Almost Certain" to accept
     Yellow = "Uncertain" — might counter-offer
     Red    = "Hopeless" — will almost certainly reject

NATIONS YOU'LL DEAL WITH:
  SAXONY   — Friendly. 18k troops. Easy to ally or vassalize.
             Great first diplomatic target.
  AUSTRIA  — Hostile. 60k troops. Allied with Prussia.
             Hard to negotiate with early on.
  PRUSSIA  — At war with you. 72k troops. Tough fighters.
             Can be peaced out but it's costly.
  BRITAIN  — At war with you. Off-map naval power.
             Permanent strategic pressure. Hardest to peace.

DIPLOMATIC STATES (worst to best):
  WAR → ARMISTICE → PEACE → OPEN BORDERS →
  NON-AGGRESSION → DEFENSIVE ALLIANCE → ALLIANCE

  Each step up costs Diplomatic Points (DP) and requires
  the other nation to accept your proposal.

WHAT AFFECTS ACCEPTANCE:
  - War score (winning = they're more willing to talk)
  - Relations (friendly nations accept more easily)
  - Threat level (high threat makes everyone hostile)
  - Sweeteners (offer gold or concessions to improve odds)

TALLEYRAND (your foreign minister):
  Handles negotiations. Shows you likelihood estimates
  before you commit. Travel time: proposals take 1-2 turns
  to deliver, response comes next turn.

VASSALIZATION:
  Make a weaker nation your tributary. They pay you gold
  each turn. You can garrison their capital. But forced
  vassalization (military conquest) generates high threat
  and rebellion risk. Diplomatic vassalization is safer.

================================================================
  THREAT & COALITIONS
================================================================

THREAT (0-100): How much Europe fears your expansion.

  What raises threat:
    Declare war         +20
    Capture a capital   +15
    Win a battle        +3
    Win decisively      +5 (on top of the +3)
    Annex territory     +8 per region
    Military vassal     +25

  What lowers threat:
    Natural decay       -1 per turn
    Peace treaties      -1 per turn per nation at peace
    Time and restraint

WHAT HAPPENS WHEN THREAT IS HIGH:
  0-29:   Calm. Europe doesn't care.
  30-39:  Tension. Talleyrand warns of unease.
  40-59:  Murmurs. Morning Dispatch warns "courts restless."
  60-79:  BREWING. 3-turn countdown to coalition!
          You can still defuse it — make peace, improve
          relations, stop conquering.
  80+:    INSTANT COALITION. Too late. Everyone declares
          war at once.

SURVIVING A COALITION:
  - Win decisive battles to demoralize members
  - Negotiate peace with individual members (costly)
  - Peel off weaker nations through diplomacy
  - Coalition dissolves when fewer than 2 members remain
  - 5-turn cooldown before a new one can form

  Tip: Don't panic. Coalitions are scary but beatable.
  Focus on one member at a time. Saxony or Austria are
  usually the weakest links.

================================================================
  ECONOMY
================================================================

GOLD comes from:
  - Regions you control (50-300 per turn based on type)
  - Trade with nations at peace
  - Tribute from vassals

GOLD is spent on:
  - Recruiting troops (10 gold per 1,000 troops)
  - Buildings (supply depots, markets, training grounds)
  - Vassal investment (200 gold to boost loyalty)
  - Diplomatic sweeteners (offer gold in negotiations)

DIPLOMATIC POINTS (DP):
  - Regenerate 2 per turn
  - Spent on all diplomatic actions
  - Budget carefully — big proposals cost 2-3 DP

================================================================
  STARTING SITUATION
================================================================

You control 8 of 19 regions. Your enemies have the rest.

YOUR FORCES:
  Ney      — 36k at Belgium (cavalry)
  Davout   — 42k in eastern France (infantry)
  Grouchy  — 28k at Bavaria (infantry)
  Drouot   — 8k at Paris (artillery)

ENEMY FORCES:
  Britain  — 76k total (Wellington + Uxbridge)
  Prussia  — 72k total (Blucher + Gneisenau)
  Austria  — 60k total (spread across eastern territories)
  Saxony   — 18k (friendly, potential ally)

SUGGESTED OPENING MOVES:
  - Ally or vassalize Saxony (easy diplomatic win)
  - Fortify Belgium against British/Prussian pressure
  - Use Davout defensively in the east
  - Build up before attacking — drill pays off

================================================================
  STRATEGY TIPS
================================================================

  1. LISTEN TO YOUR MARSHALS. Trusting their objections
     builds goodwill you'll need later. They're usually
     right about their specialty.

  2. WATCH YOUR THREAT. Conquer too fast and all of Europe
     unites against you. Mix military and diplomacy.

  3. PLAY TO PERSONALITIES. Ney attacks. Davout defends.
     Don't fight their nature — use it.

  4. FORTIFY BEFORE HOLDING. A fortified marshal can hold
     against 2:1 odds. An unfortified one barely holds 1:1.

  5. DRILL BEFORE BIG BATTLES. 2 turns of drill = +20%
     attack. Worth it for crucial fights.

  6. SAXONY IS YOUR TUTORIAL. Easy to ally or vassalize.
     Use them to learn diplomacy before tackling bigger
     nations.

  7. MANAGE MORALE. Repeated losses break armies. Rotate
     damaged marshals to the rear to recover.

  8. THREAT DECAY IS YOUR FRIEND. Pause expansion, make
     peace, and threat drops -3/turn. Buy time.

  9. COALITIONS ARE WINNABLE. Focus on one member at a
     time. Diplomacy can peel off weaker nations.

  10. THE AI HAS PERSONALITY TOO. Enemy marshals have the
      same personality system. Wellington defends. Blucher
      attacks. Exploit their tendencies.

================================================================
  TROUBLESHOOTING
================================================================

"Server window flashes and disappears"
  - Check config.txt has a valid API key
  - Try running ink_iron_server.exe directly from
    a command prompt to see the error message

"Game can't connect to server"
  - Make sure the server window is running (check taskbar)
  - Wait a few extra seconds — server needs startup time

"Commands don't work / AI doesn't respond"
  - Check your API key is correct in config.txt
  - You need an internet connection for AI processing

"Game crashes or freezes"
  - Note what you were doing and tell Mitch
  - Try restarting (close game, press any key in launcher)

================================================================
  FEEDBACK — WHAT TO TELL MITCH
================================================================

Just play and have fun. Anything you notice is useful:

  - Is it fun? What moments stood out?
  - Do the marshals feel like they have personality?
  - Is the diplomacy system interesting to engage with?
  - Were the tactical triangle and formations intuitive?
  - Anything confusing or unclear?
  - Any crashes or weird behavior?

Don't worry about being thorough. Even a few sentences
like "I liked X, Y was confusing" is valuable.

Write up your notes and message/email Mitch.
Screenshots welcome if you spot something weird.

================================================================
  CREDITS
================================================================

Designed and developed by Mitch.
AI-assisted development with Claude.
Built with Godot 4 and Python/FastAPI.

================================================================
