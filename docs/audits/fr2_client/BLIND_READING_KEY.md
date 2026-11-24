# Row FR, Session FR-2 — the blind reading of the battle report's new rows (the key, written first)

Written November 23, 2026, BEFORE any reader saw the rows. Three fresh readers (Explore agents, Sonnet), each shown
only the player's text below — no code, no design doc. The bar: **every reader right on every row** (the meaning in
essence, in their own words), and none guessing. A reader who is right but unsure is reported as such.

## What the readers are shown

> After a battle, Berthier's report lists what helped or hurt each side, like this:
>
> `Why: you had more men — 60,000 against 40,000; your jealous lone attack +15%; your cavalry momentum +5%.`
> `Attack: Murat (Jealous lone attack +15%, Cavalry momentum +5%, Bold nature +15%)`
> `Defence: Mack (Defensive stance +15%, Fortified position +50%, Square formation +5%, Defence limit (+75% at most) −8%)`
>
> and, after another battle:
>
> `Attack: Soult (Confidence in his orders +15%, The Emperor commands in person +10%)`
> `Attack: Lannes (Settled grievance +10%, Aggressive stance +15%)`

## The questions

For each of these five, in your own words: what does it mean, and why does it make his side fight better or worse?

1. "Jealous lone attack +15%"
2. "Cavalry momentum +5%"
3. "Defence limit (+75% at most) −8%"
4. "Confidence in his orders +15%"
5. "Settled grievance +10%"

## The key (what the game applies)

1. **Jealous lone attack +15%** — the marshal is jealous of a rival and attacks ALONE (no other corps of his side in
   the fight), wanting the glory for himself; he fights 15 % harder. (Right if the reader says jealousy/rivalry AND
   alone/without help, or wanting the credit himself.)
2. **Cavalry momentum +5%** — cavalry that has already charged this turn gathers speed: its second charge of the turn
   hits 5 % harder (10 % from the third). (Right if the reader says cavalry gaining momentum from charging again /
   repeated attacks.)
3. **Defence limit (+75% at most) −8%** — the defender's bonuses added up to more than the most any defence may
   have (+75 %), so 8 % of them does not count. (Right if the reader says a cap or ceiling on defence bonuses, and
   the −8 % is the part over it that is cut.)
4. **Confidence in his orders +15%** — he goes in sure of his orders (clear, well-judged ones), and fights 15 %
   harder for it. (Right if the reader says clear or good orders / confidence in his instructions.)
5. **Settled grievance +10%** — a grievance he held (a resentment) has just been answered or settled, and he fights
   10 % harder (for a short while). (Right if the reader says an old complaint/resentment resolved, lifting his
   spirit or drive.)

## Result

Three rounds, three fresh readers each round (nine in all), each shown only the text above.

- **Round 1** (the labels as first built: "Cavalry momentum", "Defence limit (+75% at most)", "Settled grievance"):
  **missed.**
  - Row 2: all three read it as any charge's bonus. The label never said it comes from charging again in a turn.
  - Row 3: two of three were confused. They add the rows (+15 +50 +5 = +70, under +75), while the game multiplies
    them. The example's own −8 % did not match the game's multiplication either: it was the key-writer's slip,
    corrected for round 2.
  - Row 5: right in meaning, but guessed (settled by apology, or by revenge?).
  - Rows 1 and 4: right, fairly sure, all three.
- **Round 2** (the three labels rewritten: "Cavalry momentum (charged again today)", "Defence limit (together +81%,
  cut to +75%)", "Pride after proving himself" — the jealousy surge is a grievance answered by his own deed):
  **15 of 15 right in meaning.** All three still guessed why 81 cut to 75 shows as −3 % (the bonuses multiply).
- **Round 3** (row 3's label says so: "Defence limit (the bonuses multiply to +81%; the limit is +75%)"):
  **15 of 15 right in meaning, again.**
  - Row 3: one reader sure (1.15 × 1.50 × 1.05 = 1.81; 1.75 / 1.81 ≈ −3 %), one fairly sure, one still guessing at
    the arithmetic.
  - Row 1: one reader guessing at the exact trigger ("the only attacker, or no rival helping?"), its meaning right.
  - Every other answer: fairly sure or sure.

**The bar:** met on meaning in rounds 2 and 3. Its "none guessing" clause was missed narrowly in round 3, on two
details rather than on what any row means:
- why a cut from +81 % to +75 % reads −3 % (multiplied bonuses);
- the lone attack's exact trigger.

Homed: Help & Keys says that a battle's bonuses multiply and that a defence is limited to +75 %. That is row TU's
(`docs/TUTORIAL_UPDATE_SPEC.md` §3), with its strict pin in `tests/test_tu_the_tutorial_brought_up_to_date.py`.
