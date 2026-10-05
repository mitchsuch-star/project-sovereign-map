# The economy audit's exit attribution (October 5, 2026)

The audit's reading (this directory) against the final reading (`../2026_10_05_sfr/`): every flipped item re-read on this tree with one group of the audit's levers DOWN, by `tools/_econ_audit_exit_attribution.py` (the reading's own command lines; the instrument's own readers; v1 readers unless named). **With every lever down the arms read as the final reading did** (living balance C4 and C5 ✓, AI aliveness C6 ✗ at 5/19 on CMD-A, AI C1 with 2 lapses, AI C5's two v1 hits, drama F1 5 modals, France 28/30/29, NAV1T-H completed) — the attribution's baseline holds.

## What each flip is

- **AI aliveness C6 ✗ → ✓ — SFR-DR1, the league declares in its own right.** With the league's two levers down, CMD-A reads 7 of 18 (✗); with the arming rung down, 12 of 18 (✓).
- **Economy C2 ✗ → ✓ — EA-13, the Net says why it moved.** With the note's lever down, the final reading's unnamed moves return (t3–t5: the charges, the tribute, the occupation); with the towers' lever down, ✓.
- **Living balance C4 ✓ → ✗ — the audit's levers in sum; no single lever restores it.** All down: Austria re-declares on France at t34 on CMD-M (✓). The arming rung down: CMD-H's general peace only at t39 (✗); the league's levers down: no peace on CMD-H at all (✗). On the shipped tree the peace on CMD-M breaks at t23, earlier, when Austria's own design war on Bavaria draws France in through its alliance — a cascade, which the item excludes.
- **Living balance C5 ✓ → ✗ — the reader's timing (EA-16), on a board that now produces it.** The turn-12 page said "Austria and Prussia would now join a league against us"; THE NEXT LEAGUE's rows first carried Prussia on turn 13, and the reader asked turn 13's page. The same miss reads with either lever group down.
- **Not flips, read for the record:** AI aliveness C1 stays ✗ for a different reason — the rival courts enact 19–20 laws with 0 lapses (above the 13–18 band; the arming rung down 17–19, the towers down 18 on CMD-H), where the final reading had 2 lapses (SFR-B14); AI C5 (v1) reads ✓ with either group down — the board, not one lever; drama F1's modal count is 5 with every lever down and 4 with the arming rung down; NAV1T-H's game over (the Emperor deposed at t27 — the arm already fell from 28 to 7 provinces by t30 on the final reading) persists with the arming rung down and completes with every lever down — the audit's levers in sum.

## The raw reads


- living balance C4 [all_down]: declarations beyond the fresh-peace floor: [('CMD-H', 'peaces', {'Austria': 34}), ('CMD-M', 'Austria', 10, 34)]
- living balance C5 [all_down]: after the peace: 1 sponsorships against France, 1 on the page; 4 great powers newly free to join, 4 on the page; 0 quoted keep-out levers on the saves, 0 flip the gate
- AI aliveness C6 [all_down]: turns with a visible AI attack over the turns at war: {'CMD-H': '15/24', 'CMD-A': '5/19', 'CMD-M': '11/39'}
- AI aliveness C1 [all_down]: laws enacted abroad (enacted, lapsed) per seed: {'CMD-H': (16, 0), 'CMD-A': (17, 0), 'CMD-M': (15, 2)}
- AI aliveness C5 [all_down]: 23 fortify/unfortify acts; fortify→unfortify→fortify within 3 turns: ['CMD-H ArchdukeCharles t8–t11', 'CMD-H ArchdukeCharles t33–t36']
- living balance F1 [all_down]: France at turn 40: {'CMD-H': 28, 'CMD-A': 30, 'CMD-M': 29}
- living balance C4 [arms_down]: declarations beyond the fresh-peace floor: [('CMD-H', 'peaces', {'Austria': 39})]
- living balance C5 [arms_down]: after the peace: 2 sponsorships against France, 0 on the page; 5 great powers newly free to join, 3 on the page; 0 quoted keep-out levers on the saves, 0 flip the gate; missed ['CMD-M t13 Prussia newly free', 'CMD-M t27 
- AI aliveness C6 [arms_down]: turns with a visible AI attack over the turns at war: {'CMD-H': '14/18', 'CMD-A': '12/18', 'CMD-M': '20/30'}
- AI aliveness C1 [arms_down]: laws enacted abroad (enacted, lapsed) per seed: {'CMD-H': (17, 0), 'CMD-A': (19, 0), 'CMD-M': (17, 0)}
- AI aliveness C5 [arms_down]: 30 acts, no dither
- living balance F1 [arms_down]: France at turn 40: {'CMD-H': 28, 'CMD-A': 29, 'CMD-M': 28}
- living balance C4 [league_down]: declarations beyond the fresh-peace floor: [('CMD-H', 'peaces', {})]
- living balance C5 [league_down]: after the peace: 0 sponsorships against France, 0 on the page; 6 great powers newly free to join, 5 on the page; 0 quoted keep-out levers on the saves, 0 flip the gate; missed ['CMD-M t13 Prussia newly free']
- AI aliveness C6 [league_down]: turns with a visible AI attack over the turns at war: {'CMD-H': '15/18', 'CMD-A': '7/18', 'CMD-M': '19/30'}
- AI aliveness C1 [league_down]: laws enacted abroad (enacted, lapsed) per seed: {'CMD-H': (19, 0), 'CMD-A': (19, 0), 'CMD-M': (20, 0)}
- AI aliveness C5 [league_down]: 22 acts, no dither
- living balance F1 [league_down]: France at turn 40: {'CMD-H': 28, 'CMD-A': 29, 'CMD-M': 28}
- economy C2 [note_down]: 48 moves of 10% or more; unnamed by the ledger's notes that turn or the next: ['t3 charges 51→156', 't4 charges 156→347', 't5 tribute 802→712', 't5 charges 347→410', 't5 occupation 70→40']
- economy C2 [towers_down]: 41 moves of 10% or more, each named by a ledger note
- AI aliveness C1 [towers_down, CMD-H]: laws enacted abroad (enacted, lapsed) per seed: {'CMD-H': (18, 0)}
- marshal drama F1 [all_down]: FLAG petition modals 5
- NAV1T-H [all_down]: status completed
- marshal drama F1 [arms_down]: FLAG petition modals 4
- NAV1T-H [arms_down]: status game-over
