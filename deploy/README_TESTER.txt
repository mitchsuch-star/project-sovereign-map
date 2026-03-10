============================================================
  INK & IRON - Playtest Build
============================================================

A Napoleonic strategy game where you command marshals through
written orders. Your marshals have personalities and may not
always obey.

------------------------------------------------------------
  SETUP (one time)
------------------------------------------------------------

1. Open config.txt in any text editor (Notepad works)
2. Replace "your_key_here" with the API key Mitch gave you
3. Save the file

That's it.

------------------------------------------------------------
  HOW TO PLAY
------------------------------------------------------------

Double-click launch.bat

Two windows will open:
  - A small server window (minimized) - don't close this
  - The game window

When you're done playing, just close the game window.
The server shuts down automatically.

------------------------------------------------------------
  CONTROLS
------------------------------------------------------------

Type commands in the terminal area at the bottom of the
screen and press Enter to send them.

Example commands:
  "Marshal Ney, attack the enemy at Saxony"
  "Davout, move to Bavaria"
  "end turn"

Hotkeys:
  F1  - Diplomacy (propose treaties, negotiate)
  D   - Morning Dispatch (turn briefing)
  T   - Strategic Ledger (forces, economy, orders)
  G   - Generals (marshal management)
  L   - Campaign Log
  Esc - Pause Menu

------------------------------------------------------------
  WHAT TO TEST / FEEDBACK
------------------------------------------------------------

Just play and have fun. Anything you notice is useful:

  - Is it fun? What moments stood out?
  - Do the marshals feel like they have personality?
  - Is the diplomacy system interesting to engage with?
  - Anything confusing or unclear?
  - Any crashes or weird behavior?

Don't worry about being thorough or formal. Even a few
sentences of "I liked X, Y was confusing" is great.

------------------------------------------------------------
  REPORTING
------------------------------------------------------------

Just write up your notes and message/email Mitch.
Screenshots welcome if you spot something weird.

------------------------------------------------------------
  TROUBLESHOOTING
------------------------------------------------------------

"Server window flashes and disappears"
  - Make sure config.txt has a valid API key
  - Try running ink_iron_server\ink_iron_server.exe directly
    to see the error message

"Game can't connect to server"
  - Make sure the server window is running (check taskbar)
  - The server takes a few seconds to start up

"Commands don't work / AI doesn't respond"
  - Check your API key is correct in config.txt
  - The AI needs an internet connection to process commands
