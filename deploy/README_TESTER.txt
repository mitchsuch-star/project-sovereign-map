================================================================
        INK & IRON — PLAYTEST BUILD
        A Napoleonic Strategy Game
================================================================

September 1805. You are Napoleon. Austria, Britain and Russia
stand against you; Prussia watches, armed and undecided.

You command your marshals through written orders. They have
personalities, ambitions and grudges — and they don't always
obey.

================================================================
  INSTALLATION & SETUP
================================================================

REQUIREMENTS:
  - Windows 10 or 11
  - Nothing else. No account, no key, no internet connection.
    The full game runs offline on its built-in parser.

SETUP:
  1. Unzip this folder anywhere (Desktop is fine)
  2. Double-click launch.bat

  Two windows open:
    - A server window (minimized in the taskbar) — DON'T close it
    - The game window

  When you're done, close the game window. The server shuts
  down automatically.

SMARTER PARSING (OPTIONAL):
  If you connect your own Anthropic account, unusually-phrased
  orders that the built-in parser can't confidently read are
  interpreted by Claude. The game is identical either way — it
  cannot invent actions or change outcomes, it only reads.

  Two ways to enable it:
    - In the game: Main Menu -> Settings -> THE PARSER (AI)
    - Or open config.txt in Notepad and paste a key there

  Typical cost: under $2 for an entire campaign, billed by
  Anthropic to you. Stored only on this PC. If it's ever
  unreachable, the game just continues on the built-in parser.

SAVES:
  Saved games live in %APPDATA%\InkAndIron\saves — they survive
  moving or re-unzipping the game folder. The game autosaves
  every turn; "Continue" on the main menu resumes the newest
  save.

FIRST TIME?
  Take "The School of War — a guided campaign" on the main
  menu. Berthier walks you through movement, battle, and the
  court in a short scripted lesson on the Danube.

================================================================
  CONTROLS
================================================================

TYPE ORDERS in the terminal at the bottom of the screen, in
plain language, then press Enter:

    "Ney, attack Mack"
    "Davout, move to Bavaria"
    "Soult, hold Lorraine"
    "Talleyrand, assess our situation"
    "end turn"

SPEAK COMMANDS (optional):
  Click the command line, press Win+H, and dictate. Windows
  voice typing writes into the terminal — review the text,
  then press Enter to send.
  (Windows 10: turn on "Online speech recognition" in Windows
  Settings if the panel refuses to listen.)

HOTKEYS:
  The command line keeps the keyboard for most of a turn, and a
  letter you type there is a letter, not a shortcut — so every
  hotkey below has an Alt form that works WHILE you are typing.
  The bare key works whenever the command line is not focused.

  F1        — Diplomacy wizard (treaties, settlements, formables)
  T / Alt+T — Strategic Ledger (forces, economy, Admiralty, orders)
  G / Alt+G — Generals (marshal cards, glory, rewards, commissions)
  D / Alt+D — Diplomatic Ledger (nations, treaties, Talleyrand)
  R / Alt+R — Morning Dispatch (re-read the turn briefing)
  L / Alt+L — Campaign Log (history of events)
  N / Alt+N — Le Moniteur (the gazette — the press writes your war)
  E / Alt+E — End Turn
  Tab       — Collapse/restore the terminal (Alt+Tab while typing)
  Esc       — Pause menu (save, load, settings). While typing, the
              first Esc leaves the command line and the second
              opens the menu.

THE MAP:
  Mouse wheel or +/- (Alt +/-) to zoom, drag to pan, Home
  (Alt+Home) to recenter, M (Alt+M) to cycle map coloring — the
  terminal prints which view you landed on. Click any province
  for a panel of actions there — recruit, build, negotiate, and
  orders for marshals present. Click a marshal's piece for their
  orders.

================================================================
  YOUR MARSHALS
================================================================

Seven marshals stand ready in the east; more can be raised
from the Commission bench on the Generals screen (G).

  NEY (aggressive) — "The Bravest of the Brave." Wants to
    charge. Objects to defensive orders. Devastating in the
    attack, careless of the cost.

  DAVOUT (cautious) — The Iron Marshal. The best defender
    France has. Objects to risky attacks; his fortified
    positions coil tighter every turn he holds them.

  SOULT (literal) — Does exactly what you say, exactly as you
    said it. Ask him to "deal with" something and he will ask
    you what you mean. Precise, never improvises.

  LANNES (aggressive) — Napoleon's friend, first over the
    bridge. Fast to arrive when a battle starts nearby.

  MURAT (aggressive) — The cavalry incarnate. Glory-hungry —
    watch his envy of other marshals' triumphs.

  BERNADOTTE (cautious) — Talented, proud, and slow to march
    to another man's rescue. Do not pair him with Davout.

  MASSENA (aggressive) — Holds Italy alone. Thrifty he is not.

  BERTHIER — Chief of staff. Reads your orders back, annotates
    battle reports, and runs the tutorial.

  TALLEYRAND — Foreign minister. Negotiates, advises, warns —
    and sometimes acts on his own opinion of your policy.

GLORY & JEALOUSY:
  Marshals earn glory in battle and envy those above them on
  the ladder (see THE LAURELS OF THE ARMY on the Generals
  screen). Success raises their expectations — an unrewarded
  hero sours. Endow estates and pensions from their card
  (the Reward chip) before grievance turns to insubordination.

WHEN MARSHALS DISOBEY:
  Order something against a marshal's nature and they object.
  You choose: Trust their judgment (+trust, they suggest an
  alternative), Insist (-trust, and they may defy you
  outright), or Compromise. Trust is a reserve — spend it
  only when it matters.

================================================================
  THE WAR
================================================================

Each turn is roughly two weeks; the campaign opens in Late
September 1805. Battles resolve when armies meet: strength,
personality, terrain, fortification, formations and nearby
friends all weigh in. Berthier reports what happened and why,
and the war table stages the field — click "View the field"
after a battle.

A few things worth knowing:
  - Fortify before holding. Drill before attacking.
  - Infantry squares stop cavalry; artillery shreds squares;
    cavalry rides down artillery.
  - Armies need supply. Massing three corps on one poor
    province starves them — watch the dispatch's warnings.
  - Broken armies flee and need time to rally. Pursue them
    or let them go — both are choices.

THE NAVY:
  Britannia rules the waves — her blockade bleeds your ports
  and her Royal Navy shuts the Channel to any army you try to
  walk across it. See THE ADMIRALTY tab in the Strategic
  Ledger (T) for your fleets, the blockade board, and the
  crossings. Lay down ships at your dockyards, and if you
  would land in England, first win yourself a window: mass
  the fleets, stage the camp, and dare the Grand Diversion.

================================================================
  THE COURT
================================================================

Press F1 for the diplomacy wizard: treaties, subsidies,
ultimatums, vassals, and peace settlements with one court or
a whole coalition. Every option shows its real availability
and likelihood — nothing is a mystery roll.

  - Nations have DESIGNS of their own (see the Diplomatic
    Ledger). Austria wants Italy back; Prussia eyes Hanover;
    Britain pays anyone who will fight you. Satisfy, buy off,
    or defy them — they bargain with each other too.
  - Win too much and Europe unites: watch your threat, make
    peace when it profits you, and mind the coalition.
  - Beaten enemies sue for terms; you can dictate, carve
    client states (a Duchy of Warsaw, a free Ireland...), or
    show mercy and bank the goodwill.
  - Vassals pay tribute and answer the call to arms — if
    their loyalty holds. Neglect them and they drift.

================================================================
  TROUBLESHOOTING
================================================================

"The launcher says the server did not come up"
  - Check the "Ink and Iron Server" window in the taskbar for
    the actual error message
  - Run ink_iron_server.exe directly from a command prompt to
    see it in full
  - Something else may be using port 8005

"Game window opens but can't connect"
  - The main menu names the launch command when the server is
    down; use launch.bat rather than starting the exe alone

"Commands aren't understood"
  - The built-in parser reads plain orders best: start with
    the marshal's name, then the deed. "Ney, attack Mack."
  - Smarter Parsing (Settings) helps with unusual phrasings —
    it is optional and costs pennies, billed by Anthropic

"Game crashes or freezes"
  - Note what you were doing and tell Mitch. The autosave in
    %APPDATA%\InkAndIron\saves means you rarely lose more
    than a turn.

================================================================
  FEEDBACK — WHAT TO TELL MITCH
================================================================

Just play and have fun. Anything you notice is useful:

  - Is it fun? What moments stood out?
  - Did the marshals feel like people? Did anyone's jealousy,
    objection, or reward demand surprise you?
  - Was a battle result ever confusing after reading the
    report?
  - Did diplomacy feel alive — did Europe seem to want things?
  - Anything confusing, ugly, or broken?

Don't worry about being thorough. Even a few sentences like
"I liked X, Y was confusing" is valuable. Screenshots welcome.

================================================================
  CREDITS
================================================================

Designed and developed by Mitch.
AI-assisted development with Claude.
Built with Godot 4 and Python/FastAPI.
Fonts, icons, portraits and textures under their respective
licenses — see THIRD_PARTY_LICENSES.md in this folder, and the
per-family notices in licenses\.

================================================================
