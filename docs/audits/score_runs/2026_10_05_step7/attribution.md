# Step 7's exit — every flip attributed by a lever-down arm

The exit read the final tree against the start reading on `bc93ffaf`, both
checked with the same instrument (the exit's own corrections SF7-X36, X40,
X41 and X44 applied to both). Each item that flipped was re-run on this
tree with one slice's levers DOWN and read with the instrument's own reader.
Tool: `tools/_step7_exit_attribution.py` (it takes the final reading's own
command lines). The arms were run on `e83be52a` with the exit's driver fix
(SF7-X36); SF7-X42 and X43 change a refusal's words and one parse, and move
none of these readings.

| item | start `bc93ffaf` | final | levers down | reading with the levers down | cause |
|---|---|---|---|---|---|
| combat legibility C2 | ✗ favorable 12/13, even 2/2 | ✓ favorable 12/12, even 2/3 | the field read (slice 3) | ✗ 12/13, even 2/2 — the start's | slice 3 (§6 row 16) |
| UI/UX C4 | ✗ 4 blocking popups (turn 10) | ✓ 3 (turn 9) | the field read | ✗ 4 (turn 10) — the start's | slice 3 |
| UI/UX C4 | | | the S5-4 overflow (slice 7) | ✓ 3 (turn 9) — unchanged | not slice 7 |
| AI aliveness C5 | ✓ no dither | ✗ Charles t8–t11, t33–t36 | the field read | ✓ no dither | slice 3 (§6 row 18, the user's) |
| economy C1 | ✓ the Staff at loop 7 | ✗ loop 10 | the field read | ✓ loop 7 | slice 3 |
| marshal drama F1 | ✓ 3 petition modals | ✗ 5 | the field read | ✓ 2 | slice 3 |
| all three ✓→✗ | | | slice 10's levers (S, P) | final's readings — unchanged | not slice 10 |
| diplomacy C3 | ✗ no volte-face | ✓ the volte-face fires | §6 row 20 (slice 6) | ✗ no volte-face | slice 6 (§6 row 20) |
| first contact C4 | ✗ the counsel names no purchase | ✓ "build supply depot in Paris — 300g" | slice 3b's build line | ✓ still names it | either alone |
| first contact C4 | | | the field read | ✓ still names it | either alone |
| first contact C4 | | | both | ✗ the start's answer | slices 3 + 3b, either sufficient |
| command C3 | ✗ 10/20 | ✓ 20/20 | — | — | the exit's own SF7-X42 … X44 |

**Why the field read moves these.** With the lead's coordination read on the
field (§6 row 16, the user's ruling), French battles mass more men and lose
fewer: on LAW the army stands ~10,000 larger at turn 2 and pays their upkeep
("you pay for the soldiers you have"), so the saving reaches the Staff's
9,000 three loops later; on the flagship arm the bigger victories crown more
men and five crisis-tier petitions keep their modal (B1) where three did;
on CMD-H Archduke Charles fortifies on arrival, breaks camp to strike and
fortifies the next province (row 18's shape). None is tuned (the user's rule);
row 22 puts the two new ones to the user.

Raw output of the tool on the exit (October 5, 2026):

```
FLAG petition modals: {'field_down': 2, 's10_down': 5}
LAW field_down: the Staff enacted at loop 7
CMD-H field_down: 7 acts, no dither
LAW s10_down: the Staff enacted at loop 10
CMD-H s10_down: 15 fortify/unfortify acts; fortify→unfortify→fortify within 3 turns: ['CMD-H ArchdukeCharles t8–t11', 'CMD-H ArchdukeCharles t33–t36']
combat C2 field_down: favorable out-bleeds 12/13 = 0.92; even 2/2; unfavorable 1/6
ui C4 field_down: most blocking popups one end turn raised: 4 (turn 10)
ui C4 overflow_down: most blocking popups one end turn raised: 3 (turn 9)
first contact C4 buildline_down: … build supply depot in Paris — 300g
first contact C4 field_down: … build supply depot in Paris — 300g
first contact C4 both_down: … For any matter of state, press F1 for the Cabinet.
diplomacy C3 allyswar_down: no volte_face on the volte arm
```
