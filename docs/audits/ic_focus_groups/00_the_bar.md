# The focus-group loop — its rules, written BEFORE any panel is shown the design

Date written: November 19, 2026. Subject: "His Own Command" (row IC), docs/INDEPENDENT_COMMAND_SPEC.md.

## The panels

Six panels a round. Each panel is four named experts with different backgrounds who are told to disagree
where they would disagree, and that a panel which only praises is useless.

1. Players — four kinds of strategy player.
2. Designers — systems, board wargames, balance, production.
3. Historians — the Grande Armée's staff, the marshals, mission command, a historical novelist.
4. Newcomers and UX — a games user researcher, a first-time player, an accessibility specialist, a plain-words editor.
5. Engineers and QA — AI programmer, QA lead, save/determinism engineer, exploit hunter. May read the code.
6. The enemy's side — an opponent-AI designer, a player who beats AIs for sport, an information/deception
   strategist, a red-team wargamer. May read the code.

Round two uses NEW people on the same six lenses. They are shown the improved design and the earlier
round's worst findings with the rulings given, and are asked to break those rulings.

## What every panel must return

- Seven scores from 1 to 10, each with one sentence of reason:
  A Clarity · B Agency (is it you playing?) · C Character (are the marshals different men?) ·
  D Solidity (can a rule be broken, contradicted or abused?) · E The enemy (a better and fair opponent?) ·
  F Typing (does the typed line have a real job?) · G Want (would you play it / fight to build it?)
- The best three things.
- Problems, ranked, each with a rank and a proposed fix:
  - RANK 1 — it cannot ship like this: two rules contradict; an exploit wins the game or makes the cap
    meaningless; hidden information leaks; a state with no way out.
  - RANK 2 — a serious weakness in play: a strategy that is always best, a boring loop, a confusion most
    players will hit.
  - RANK 3 — polish.
- At least ten concrete edge cases: the situation, and what the design says happens (or "the design does not say").
- How the enemy should use it, and how the player should be able to read and exploit that.
- Where the four disagreed.

## How I treat what comes back

- Every RANK 1 and RANK 2 finding gets one of: ACCEPTED (the design changes — say how), ALREADY ANSWERED
  (point to where), or REJECTED (say why). Nothing is dropped silently.
- A finding about what the code does is checked against the code before it is accepted.
- The design's version goes up by one after each round, and the record of findings and rulings is kept in
  the design document.

## When the loop stops

It stops after the first round in which ALL of these hold:

1. No panel raises a RANK 1 finding that I accept as real and still open.
2. No more than three accepted RANK 2 findings remain open, each with a recorded ruling.
3. The median of all scores is 8 or more, and no panel scores D (Solidity) or G (Want) below 7.

At most three rounds. If the bar is not met after three, the report says plainly what is left.

Scores are a weak signal — panels of this kind tend to mark kindly. The findings are the point; the scores
only guard against stopping while a panel is still unhappy.
