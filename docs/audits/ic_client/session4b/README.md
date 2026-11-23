# Row IC, Session 4b — the voice's blind reading again (IC4-R1), November 23, 2026

**Your ruling (November 23):** "Sharpen and re-test" — keep "nobody guesses"; sharpen Ney / Lannes and
Masséna / Davout so each pair is told apart by its mark; three fresh readers a round; a miss after three
rounds is reported with the lines that drew the guesses.

**The bar (written first, the plan):** every reader right on every question, and nobody guessing.

**The protocol.** The draw is now kept in the repository (`tools/_ic4b_voice_key.py`; Session 4's was never
kept). Each round: a new draw, its key written to this folder BEFORE any reader sees a line; three fresh
Sonnet readers, each shown only the six one-line portraits and the lines (no file, no tool); scored by
`tools/_ic4b_voice_score.py`. **Test 1** (the plan's question): twelve pairs of two named marshals, one line
each — which said which, and what told you; the two pairings that confused Session 4's readers (Ney with
Lannes, Masséna with Davout) drawn twice each. **Test 2** (harder, besides): five sets of six lines of one
kind, one line from each man, to be matched. Every draw includes the "act on your own" lines and the
hold-proposal lines (added after Session 4's last round, never read). A line is never drawn twice in one
draw.

Before round 1, a helper sharpened the four men's sets (Ney 33 lines, Lannes 11, Masséna 23, Davout 28,
each line given its man's mark); I rewrote three of its lines by hand where the mark made the sentence
awkward.

| Round | Key | Test 1 (pairs) | Test 2 (six-way) | Marked "partly guessed" | After it |
|---|---|---|---|---|---|
| 1 | `_blind_key_round1.json` (draw 1 set aside unread by any reader: a line was drawn twice — `_blind_key_round1_draw1_discarded_unread.json`; the draw now never repeats a line) | 36 of 36 | 90 of 90 | pairs 2, 9, 10 by all three readers (pair 1 by one); six-way 6–9 letters a reader, the same lines each time | the fourteen lines that drew the guesses sharpened (below) |
| 2 | `_blind_key_round2.json` (two draws set aside unread by any reader: one came out with eleven pairs, one drew a line in both tests — the draw now retries for twelve pairs and never draws a line twice anywhere) | 36 of 36 | 85 of 90 (one reader rotated the three "remembers" lines of Ney, Davout and Masséna, and swapped Lannes's and Bernadotte's "overruled") | 1–3 pairs a reader (pairs 6, 9, 10; pair 1 by one); six-way 7–12 letters a reader | the sixteen lines the readers erred on or marked unsure sharpened |
| 3 — the last | `_blind_key_round3.json` | 36 of 36 | 88 of 90 (one reader swapped Ney's and Lannes's "after a win") | pairs 1, 2, 9 and 11 by all three readers — each between two BOLD men; six-way 7–11 letters a reader | none: the ruling's three rounds are spent — **the bar is MISSED on "nobody guesses"** |

**What the three rounds say.** The six voices are told apart: 108 of 108 pairs right across the three
rounds, and 263 of 270 six-way lines. What none of them met is "nobody guesses", and since round 2 every
guess but one is between two of the BOLD men — Ney with Lannes, Ney with Murat, Murat with Lannes ("both are
bold, so this is less clear"; "a weak signal"). The careful and the politic men (Davout, Masséna,
Bernadotte) drew no guess in round 3.

**The lines that drew the guesses in round 3** (all three readers right, all three unsure):
- pair 1 — Ney "No task, Sire? I'll find a fight myself now, before I go mad sitting here." / Lannes "As I
  see fit, Sire. Wherever the guns are loudest, that's where you'll find me."
- pair 2 — Ney "Boldly? At last, Sire — no more sitting still, I go now." / Lannes "Boldly, Sire? Straight
  at them with the columns."
- pair 9 — Murat "You called me back last time, Sire. Let me see this one through." (no horse in it) /
  Masséna "You gave another man the ground that was mine to take, Sire. I remember it."
- pair 11 — Murat "Nothing worth chasing yet, Sire. Let me hold here with the horses saddled." / Ney
  "Nothing in reach to hit, Sire. I'm restless, but I'll hold here until something comes."
- six-way — Ney "We beat them, Sire. I'll go in sooner next time." with Lannes "We won, Sire. Next time
  I'll storm harder." (swapped by one reader); Lannes "No excuses, Sire. Send me at the next one and I'll
  storm it."; Murat "On his heels, Sire. He can hear us coming."; Ney "The men are moving, Sire. I'd have
  them run now if I could."

**What would close it, for your word** (`BUG_FIXES.md` IC4-R1 stays open): a systematic pass over the bold
three's lines that carry no mark of their man — a check over every line (kept in this session's scratch
work) found Lannes's "storm" lines, Murat's chase lines with no horse in them, and two of Ney's — then a
fourth reading; or your ruling on the "nobody guesses" clause.

**Round 1's guesses, by line** (every reader right; these are the lines they marked unsure):
- Ney / Lannes after a defeat — Lannes "We got the worst of it, Sire. I'll look harder before the next
  assault." carried no mark of his but "assault".
- Ney's "bolder" — "Boldly it is. Now I won't have to hold myself back." (no mark of his impatience).
- Bernadotte's "remembers" (both lines) and Ney's — no politic turn in Bernadotte's, none of Ney's
  impatience in his.
- Six-way: Ney's third turn of the same, task done and win; Lannes's win; Masséna's "remembers";
  Murat's "remembers"; Bernadotte's win.
