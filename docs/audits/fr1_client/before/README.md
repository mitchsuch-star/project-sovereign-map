# Row FR, Session FR-1 — the probe before the build (November 23, 2026)

The real client, driven at the first player's setup (Interface Scale 1.8 on 5120 × 1377), against a sandboxed
backend on port 8006 (`tools/dd_b_play.py`, road "diplomacy"). The action log is `actions.log` beside this file.

| Step | What was pressed | What the client did |
|---|---|---|
| 6–8 | Alt+T, Alt+3, Pin | the Strategic Ledger open at its third book (ECONOMY), pinned beside the map |
| 9 | click Murat | Murat selected; his card showed `1 Hold the ground · 2 actions` … `7 Cancel order` |
| 10 | click the ECONOMY tab | the caret left the command line (focus: the tab button) |
| **11** | **key 1** | **the ledger turned to its first book (FORCES); Murat's card did nothing** — WS-10 as filed |
| 12–14 | Unpin, Alt+G, Pin | the Generals screen pinned beside the map (no focus owner: the caret off the line) |
| 15 | click Murat | Murat selected; his card standing |
| **16** | **key 3** | **the Generals screen's detail jumped to Davout (its third marshal); Murat's card did not drill** — the docked Generals screen never stood aside |

**What step 16 proves (FR1-1):**
- Session UI-6's rule is not met in the real client: "docked at the Side Desk, the war room keeps the keys"
  (`marshal_management.gd` ~178–184).
- The flag is written on the screen's root node (`top_bar._set_docked`, `node.set_meta("side_desk_docked", on)`).
- Every reader asks the `PanelContainer` inside it: `marshal_management.gd` ×2, `dispatch_view.gd` ×4, `utils.gd`
  ×2.
- On unpin the flag is set to `false`, not removed, while the readers ask `has_meta`.
- The source-text pins (`TestWS10…::test_the_generals_screen_already_stands_aside`, `test_ui6_generals.py` ~175)
  read the reader's words, never the behaviour, so they stayed green.
