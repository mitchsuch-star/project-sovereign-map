# UXR-4 at S15's head — the decided fixes, re-shot (October 25, 2026)

Rows: UXR3-24, UXR3-80, UXR3-29, UXR3-79, UXR3-81 (`docs/BUG_FIXES.md`; the
"decided fix, if the user's mark is ✗" sentence of each is the spec, built as
written). Rules and frames are for the user's yes/no at their monitor; a ✓ closes
the row, a ✗ goes back with this README beside it.

How the frames were taken: `tools/iq10_run_captures.py --physical`, the window
sized to 1920×1080 and 5120×1440 with the Interface Scale a player at that size
would have (`auto`: 1.0 and 1.4), on the payloads `tools/iq10_capture_payloads.py`
captured off the rows' own boards (client base `4ac79a0f` plus the S15-head edits).
`index.json` carries each frame's record (`seen_text`: the whole lines a player
sees), the frame's before/after paths and the staging; the engine's output held 0
`SCRIPT ERROR` lines. After frames are the surface's own crop (the S12b idiom,
`tools/uxr3_review.crop`), JPEG q85, named `UXR4_<SHOT>_<res>.jpg` in `frames/`.
Before frames are the committed S12b set, `docs/audits/uxr3_s12b/frames/UXR3_<SHOT>_<res>.jpg`.

| Shot | Row | Before | After | What the first screenful shows now |
|---|---|---|---|---|
| `generals_t20` | UXR3-24 | `UXR3_GENERALS_T20_{1920x1080,5120x1440}` | `UXR4_GENERALS_T20_*` | OUR DOCTRINE is one title line ("▸ the doctrine"); THE LAURELS is one line; Ney's sheet starts under the Commission chip — portrait, Strength, Tactical and Shock bars in view (before: only his portrait at the bottom edge). His Trust / glory / grievance lines are still below the fold. |
| `generals_np_field` | UXR3-24 | `UXR3_GENERALS_NP_FIELD_*` | `UXR4_GENERALS_NP_FIELD_*` | Doctrine one line, THE EMPEROR next; under his state line a gold "★ The Presence  +10% here at Bohemia" states the figure as applied, before his Strength line. |
| `generals_np_field_dim`, `generals_np_field_out` (check frames) | UXR3-24 | — | `UXR4_GENERALS_NP_FIELD_DIM_*`, `..._OUT_*` | The same board with the backend's own NPC-D1 sentence appended to the Presence (a payload edit, said in `index.json`): "+4% here at Bohemia" with the star dimmed toward the grey ink; "+0% here at Bohemia" with the star at the ink ("his star is out"). |
| `generals_boot` | UXR3-80 | `UXR3_GENERALS_BOOT_*` | `UXR4_GENERALS_BOOT_*` | Doctrine one line; THE EMPEROR's card now leads — portrait, state line, "★ The Presence  +10% here at Lorraine", Strength, then his biography. **The first marshal's sheet (Ney) and the skill bars are still below the fold at both sizes**: the Emperor's own prose fills the rest of the screenful (see the open note below). |
| `generals_doctrine` | UXR3-24 | `UXR3_GENERALS_DOCTRINE_1920x1080` (no 5120 before) | `UXR4_GENERALS_DOCTRINE_*` | The board whose subject is the doctrine: the harness presses the toggle (`steps` on the shot), "▾ hide the doctrine" and the says / Strength / Flaw lines stand open above THE EMPEROR. |
| `generals_prisoner`, `generals_np_captive` (UXR3-24's other listed boards) | UXR3-24 | `UXR3_GENERALS_PRISONER_1920x1080`, `UXR3_GENERALS_NP_CAPTIVE_1920x1080` | `UXR4_GENERALS_PRISONER_*`, `UXR4_GENERALS_NP_CAPTIVE_*` | The captured marshal leads under "A PRISONER — Ney: PRISONER of the Kingdom of Italy since T1."; the captive Emperor's card leads under the one doctrine line with "A captive — PRISONER of Austria since T11". |
| `diplo_laws_rival_nations` | UXR3-29 | `UXR3_DIPLO_LAWS_RIVAL_NATIONS_*` | `UXR4_DIPLO_LAWS_RIVAL_NATIONS_*` | Britain's card is the first thing under the page head; its Laws line ("the Orders in Council and the Militia Transfer (300 gold a turn)") is the line under its name, its Doctrine line the next; Russia's card follows. "How Europe Reads France" and "The Emperor's Own Exposure" are out of the frame — they close the book. |
| `diplo_doctrine_nations` | UXR3-29 | `UXR3_DIPLO_DOCTRINE_NATIONS_*` | `UXR4_DIPLO_DOCTRINE_NATIONS_*` | Britain's and Russia's Doctrine lines lead their cards, one line under each name. **Austria's "cured since turn 1" line — this shot's point — is not in the first screenful** (a third card, the book's own court order; the fix as decided moves the two France blocks, not the courts). |
| `diplo_petition_granted_vassals` | UXR3-81 | `UXR3_DIPLO_PETITION_GRANTED_VASSALS_*` | `UXR4_DIPLO_PETITION_GRANTED_VASSALS_*` | Switzerland — the court whose petition was granted — is the first card, "Bond: +1/turn — a bond worth one honoured petition (bond 20)" in green directly under its header, above its Loyalty bar; Holland (no bond yet) follows. |
| `region_doctrine_posen` | UXR3-79 | `UXR3_REGION_DOCTRINE_POSEN_*` | `UXR4_REGION_DOCTRINE_POSEN_*` | "Poor country — a French army here draws 80% (living off the land)" is the line under "Prussia · City · Plains", above the help text and the Income / Stability / Supply row. |
| `region_doctrine_tyrol` | UXR3-79 | `UXR3_REGION_DOCTRINE_TYROL_*` | `UXR4_REGION_DOCTRINE_TYROL_*` | "Stripped by war (35%) — poor country for a French army until it recovers below 25%" is the line under "Austria · City · Mountains", above the ACTIONS block (Negotiate with Austria), the help text and the War damage figure. |
| `ledger_mission_transit_forces` | UXR3-41 | `UXR3_LEDGER_MISSION_TRANSIT_FORCES_*` | `UXR4_LEDGER_MISSION_TRANSIT_FORCES_*` | The board is STAGED now (the letter goes to Prussia, whom the gate admits; the capture asserts `paused: true` — `uxr3_41_restage_facts.json`): under THE CABINET, "Talleyrand → Denmark \| COURTING +8 a turn, drift +0, net +8" then "Relations 10 (Neutral) · paused: he is carrying your proposal — costs nothing, earns nothing until he returns · 2 DP a turn", in the warning colour, with NO [Recall]. Before, the block read an active mission with a live [Recall]. |
| `ledger_mission_starved_forces` | UXR3-41 | `UXR3_LEDGER_MISSION_STARVED_FORCES_*` | `UXR4_LEDGER_MISSION_STARVED_FORCES_*` | Staged now (the DP shortfall written after the turn's refill, before the mission's tick): "Relations 10 (Neutral) · paused: 2 DP needed — collapses in 2 turns without it · 2 DP a turn [Recall]" and "So far: stalled 1 turn for want of DP". Before, "COURTING … 4 funded turns". |

## Open notes for the user's eye (no open row: the fixes are built as decided)

1. **`generals_boot`** — the fold lets the Emperor's card lead, as decided, but his
   own two prose paragraphs (the biography and the "Sovereign: You, in the field…"
   personality line) still fill the rest of the first screenful, so the skill bars
   and the first marshal's sheet are one scroll down at 1920×1080 and 5120×1440.
   If the mark is ✗ again, the lever is the sovereign card's order (his skill bars
   above the two paragraphs), not another fold.
2. **`diplo_doctrine_nations`** — each court's Doctrine line leads its card, but the
   first screenful holds two cards (Britain, Russia); Austria's is the third.
3. The Presence's "applied figure" is read off the backend's own sentence
   (`marshal_overview._build_ability`: the authored "+10%" and, when the aura has
   decayed, "Today it stands at +N%"), never recomputed in the client; the star's
   colour is a straight blend from the gold to the grey ink by applied ÷ authored.
