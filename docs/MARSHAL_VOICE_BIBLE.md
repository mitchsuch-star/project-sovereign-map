# Marshal Voice Bible

> **Status:** v1.0 — November 22, 2026 (row IC, Session 4 / IC-13).
> **Purpose:** one page that says how each French marshal talks, what he never says, what he remembers, and how a new line or a new man is added.
> **Source of the lines:** `backend/game_logic/own_voice.py` (the sets), `backend/game_logic/said_lately.py` (the "last three" rule). This guide is the shape of those files in plain words; if the two disagree, the code and its test win and this guide is fixed.
> **Sister document:** `docs/DIPLOMAT_VOICE_BIBLE.md` (the foreign diplomats). That one is period and formal. This one is not.

---

## 1. Purpose and the rules of a line

A marshal who is given a task, or who acts on his own, answers in a voice that is his. The line is flavour and character. It decides nothing. The cause, the numbers and the consequence always sit beside it in plain words from the staff.

The user's ruling (November 22, 2026): **plain and short.** Everyday English, at most two sentences, no number ever, "Sire" the only period word. A marshal's nature is shown as **Bold · Careful · To the letter** on every screen.

The rules, each pinned by `tests/test_ic13_every_man_his_own_line.py`:

- Written by hand, never by a model, and it decides nothing (golden rule 6). Pin: `TestTheRulesOfALine`.
- Plain: everyday English, at most two sentences, at most 120 characters. Pin: `test_every_line_is_plain_and_short`.
- No digit in any line; figures stay on the screen beside it. Pin: `test_every_line_is_plain_and_short`.
- "Sire" is the only period word (`PERIOD_WORDS` lists what is barred). Pin: `test_sire_is_the_only_period_word`.
- His own: no line stands in two sets, and no set repeats a line. Pin: `test_no_line_stands_in_two_sets`.
- He never says what `NEVER_SAYS` lists for him — nor does a line of his nature that falls through to him (`own_voice.pool` drops a nature's line that would break his words). Pin: `test_no_man_says_what_he_never_says`.
- Every line carries an explicit MARK of the man — Ney's impatience, Davout's order and counting, Murat's horses and his vanity, Lannes's guns and the assault, Masséna's ground ("mine", not an inch), Bernadotte's polite excuse. The blind readings showed that an unmarked line ("Done.", "On the road at last.") is anybody's. Pin: the reading (`docs/audits/ic_client/session4/README.md`).
- No line twice within his last three. Pin: `test_no_line_twice_within_his_last_three_on_a_long_walk`.
- A man with nothing new to say says nothing; the plain sentence stands alone. Pin: `test_a_man_with_nothing_new_to_say_says_nothing`.
- A kind he can say on nights running carries four lines or more. Pin: `test_a_kind_said_on_nights_running_carries_four_lines_a_man`.
- Every set of every kind a named man holds is four lines or more once his nature's lines are added. Pin: `test_every_named_mans_set_of_every_kind_is_four_or_more`.
- His own lines come before his nature's. Pin: `test_his_own_lines_come_before_his_natures`.
- On the historical seed the first line of each set is said first; another seed starts at a fixed place, never a die. Pin: `test_the_historical_seed_says_the_first_line_of_each_set_first`, `test_another_seed_starts_each_set_at_a_fixed_place`.
- The only placeholder allowed is `{orders}`, in the letter-following men's `repeat` line. Pin: `test_every_line_is_plain_and_short`.
- The same question asked twice gets the same answer (the chooser is pure) and there is one writer of what he said. Pin: `test_the_chooser_is_pure_and_there_is_one_writer`, `test_only_the_voice_modules_write_what_he_said`.

How "the last three" works (`said_lately.py`): each man keeps a short key of the last three lines he said, saved with him. `choose` walks the set from its starting place and takes the first line not among those three. If every line of a set is among them (only possible in a set of three or fewer), he says nothing. `say` is the one writer.

---

## 2. Where a line is said and where it is only previewed

Two functions in `own_voice.py`:

- `voice` is pure. It names the line he would say next and writes nothing.
- `speak` is `voice` plus the one record. It is called only where a line is really said.

**Previewed (nothing recorded):**

- the read-back under the typed line, which shows the line he will say when the order is given;
- a question put to him;
- "Tonight", the list of what each man will do before the turn ends;
- a court's heading on captured orders (`court_head`; no marshal says it).

Because `voice` and `speak` pick the same line from the same state, the line the player sees before pressing Enter is the line he says after. Pin: `test_the_read_back_shows_the_line_the_order_then_says`, `test_asking_him_changes_nothing`.

**Said (recorded):**

- an order given (his answer to it);
- a night's act, in the morning report;
- a battle (the after-battle line);
- a task ended (done, trial won, trial lost);
- the memory, once (`recall_memory` with `said`), then put away.

The record rides `marshals`, so an order taken back takes its line back with it. Pin: `test_an_order_taken_back_takes_its_line_back`.

---

## 3. The kinds

| Kind | The moment | Who has it |
|---|---|---|
| `ack` | given a task | the six named judging men; bold and careful natures |
| `bolder` / `careful` | told to do it boldly / carefully | the six; bold and careful natures |
| `object` | he objects to the task | the six; bold and careful natures |
| `proposal` | his own idea, when it is to take, chase or support | Ney, Murat, Lannes; the bold nature |
| `proposal_hold` | his own idea, when it is to hold (a bold man with nothing in reach; every careful man) | the six; bold and careful natures |
| `idle` | asked, with nothing to do | the six; bold and careful natures |
| `struck` | he fought or took something | the six; bold and careful natures |
| `marched` | he marched | the six; bold and careful natures |
| `fell_back` | he fell back | bold and careful natures only |
| `waited` | he looked, felt, waited | the six; bold and careful natures |
| `dug_in` | he dug in | Davout, Bernadotte and Murat by name; bold and careful natures |
| `stayed` | he stayed put | the six; bold and careful natures |
| `asks` | he asks you for a word | the six; bold and careful natures |
| `done` | the task is done | everyone, including the letter-following men |
| `third_night` | he changes his way of waiting rather than repeat it | the six; bold and careful natures |
| `after_win` / `after_loss` | the night after a battle | the six; bold and careful natures |
| `overruled` | today's order came over his own task | everyone, including the letter-following men |
| `recalled` | his task was called back | the six; bold and careful natures |
| `passed_over` | a junior was sent while he stood idle | natures only (bold, careful, literal) |
| `remembers` | the one thing he remembers, said once | the six; bold and careful natures |
| `trial_ask` / `trial_won` / `trial_lost` | the task to prove himself | everyone |
| `exact` / `repeat` / `not_covered` / `broken` / `refusal` | a man who follows orders to the letter | Soult, Grouchy; the literal nature |

`RECURRING` (`ack`, `idle`, `struck`, `marched`, `waited`, `stayed`, `dug_in`) are the kinds a man can say on nights running. Each must reach four lines or more for every man, counting his nature's lines after his own.

`KIND_OF_ACT` turns a night's act into a kind: attack, storm, besiege, take, strike say `struck`; march, move_up and join say `marched` (a join is a march to a friend's battle — no "I led"); fall_back says `fell_back`; look and probe say `waited`; dig_in says `dug_in`; stay says `stayed`; asks says `asks`. Then `own_order._voice_act` keeps each line true of the night: a night with no battle says no `struck` line (a take he marched into says `marched`; a siege kept up, or the ground he stands on claimed, says nothing); a stay says the line that fits WHY he stayed (`own_order.STAY_SAYS`: none when he did your order today, did his night's work, was drawn into a friend's battle or has no corps; `waited` on a quiet front; `stayed` only when the board changed). A night he only made ready or rested his men has no line; the plain words say it. A line never claims what the night did not hold: `struck` claims no victory, `waited` no particular way of waiting, `asks` no reason, `done` no particular task, an `ack` nothing false of a hold.

---

## 4. The named men

Six judge for themselves (Ney, Davout, Murat, Lannes, Masséna, Bernadotte). Two follow orders to the letter (Soult, Grouchy). Natures in the test: Ney, Lannes, Murat and Masséna are bold; Davout and Bernadotte are careful; Soult and Grouchy are literal. A kind a man has no set for falls through to his nature's set (section 5). The "never says" lists are whole words, any case, copied from `NEVER_SAYS`.

### Ney (Bold)

**Who he is:** the man who cannot stand still and will not be told to wait.

**How he talks:**
- Eager and a little rueful; he answers a task with relief and an order to hold with complaint.
- Short sentences, often with "Sire" at the end; he names the fight, never the plan.
- Waiting is a burden he says out loud ("I don't like it").

**Never says:** retreat, fall back, fell back, prudent, too strong, wait for.

**What he remembers:** an order you overruled (`overruled`). Said once, the next time he is given a task or reports a night.

**Exemplars:**
- ack
  > At last, Sire! A fight, I hope, and soon.
- object
  > Hold, Sire? With the enemy right there and the men itching to go?
- idle
  > Quiet again. I'm climbing the walls, Sire.
- remembers
  > You overruled me once, Sire. I've not forgotten — but I'll go.

### Davout (Careful)

**Who he is:** the man who never wastes a man and chooses his own ground.

**How he talks:**
- Exact and dry; "properly", "in order", "by the book".
- Pushes back with odds and ground, never with feeling; he obeys "if you insist" and says he advises against it.
- Is the one who digs in, and says what the digging is for.

**Never says:** glory, luck, chance, gamble.

**What he remembers:** being passed over (`passed_over`), when a junior was given a task while he stood idle.

**Exemplars:**
- ack
  > Understood. I'll not waste a man.
- object
  > I'll do it if you insist, Sire. The cost in men is higher than it looks.
- dug_in
  > More earth moved today. It will save men later.
- remembers
  > You gave that task to a junior, Sire. I noticed.

### Murat (Bold)

**Who he is:** the cavalryman who wants to ride and cannot bear camp.

**How he talks:**
- Horses and roads; every task is something to chase or ride at.
- Bright and vain, with exclamation marks that are his alone ("Leave it to the cavalry!").
- When held back he is sulky about the waste, not angry.

**Never says:** dig, dug, trench, patience, slowly, on foot.

**What he remembers:** being called back in the middle of a chase (`recalled`).

**Exemplars:**
- ack
  > Leave it to the cavalry!
- marched
  > Half the country is behind my saddle already, Sire.
- object
  > Sit still, Sire? Horsemen are made to ride.
- remembers
  > I was recalled once in the middle of a chase. I've not forgotten it.

### Lannes (Bold)

**Who he is:** the friend who goes to the guns and stands beside whoever is in danger.

**How he talks:**
- Blunt and warm; says plainly when he thinks it is a mistake and then does it anyway.
- His ground is wherever a friend is fighting, so he marches "toward the sound".
- Calls the Emperor by his title when sore ("you're the Emperor").

**Never says:** retreat, fell back, give up, too strong, afraid.

**What he remembers:** an order you overruled that kept him from a friend's fight (`overruled`).

**Exemplars:**
- struck
  > I heard guns and went, Sire. You would have done the same.
- proposal
  > Put me where the guns are loudest, Sire. That's where I'm best.
- overruled
  > Fine, Sire. The horses can rest a night, and so can my task.
- remembers
  > You pulled me away from the guns once, Sire. Don't do it twice.

### Masséna (Bold)

**Who he is:** the man who will not let go of what he holds, and wants his share of the credit.

**How he talks:**
- Keeps ground and counts what he has not lost ("I've given up nothing").
- Advances slowly and for good, with the rear held.
- Wants credit said aloud when a task is done.

**Never says:** abandon, let go, glory.

**What he remembers:** being passed over (`passed_over`), the task another man was given. (He is the one bold man who remembers the careful men's thing.)

**Exemplars:**
- idle
  > Holding firm, Sire. Nobody is taking this ground from me.
- done
  > Finished, Sire. Every yard of it still mine.
- object
  > Give up good ground, Sire? I'd rather not.
- remembers
  > You gave another man the task I should have had, Sire. I remember.

### Bernadotte (Careful)

**Who he is:** the slow, courteous man who is never in a hurry and prefers not to presume.

**How he talks:**
- Soft and hedged ("if you insist", "I'd rather not presume", "no need to hurry me").
- Reports small safe gains and low losses; hopes his part is noticed.
- Agrees with caution warmly and with boldness reluctantly.

**Never says:** at once, charge, glory.

**What he remembers:** being recalled before he had begun (`recalled`).

**Exemplars:**
- ack
  > As you wish, Sire. I'm sure you'll let the men have a good night's rest first.
- asks
  > Perhaps you would decide, Sire. I'd rather not presume.
- dug_in
  > A little digging, Sire, just enough to sleep soundly.
- remembers
  > You recalled me once before I'd begun, Sire. I've kept that in mind.

### Soult (To the letter)

**Who he is:** the man who does what is written and nothing else.

**How he talks:**
- Repeats your orders back to you, whole, and adds nothing.
- Says plainly when his orders do not cover a case and waits for the next.
- Never guesses and never offers a view.

**Never says:** i think, i judge, perhaps, i guess, i would rather.

**What he remembers:** nothing. He holds his lines, not a grudge. No `remembers` set, no `passed_over` of his own.

**Exemplars:**
- exact
  > Exactly as you wrote it. Nothing added.
- repeat
  > As written: {orders} I add nothing.
- not_covered
  > My orders say nothing of this, Sire. I stand where I am.
- refusal
  > I follow orders, Sire. Write them and I'll carry them out.

### Grouchy (To the letter)

**Who he is:** the same obedience, but anxious: he will not put a foot wrong and will not be blamed for a guess.

**How he talks:**
- "Keep to every word", "to the last word", "not stray".
- Admits he hears the fighting and still does not move without a line for it.
- Asks to have it written down for him.

**Never says:** i think, i judge, perhaps, i guess, i would rather.

**What he remembers:** nothing. He holds his lines, not a grudge.

**Exemplars:**
- exact
  > Each line exactly as given. You may rely on it.
- not_covered
  > I hear the guns, Sire, but my orders don't mention them.
- refusal
  > Write it down for me, Sire. I'll do just that.
- done
  > Finished, Sire. I kept to the letter.

---

## 5. The natures' registers

Every other marshal, and any kind a named man has no set for, speaks from `BY_NATURE`. His own lines come first; his nature's follow, and a line is never said twice. The Emperor has no nature here and speaks no line. A man set to follow orders to the letter is never on his own, so he has no `ack`, `idle` or `struck` set, and the pin skips those.

Remembering by nature (`REMEMBERS_BY_NATURE`): a bold man remembers being overruled; a careful man remembers being passed over; a literal man remembers nothing.

### Bold

Eager, short, and impatient with waiting. Says what was done, not why.

- object
  > Hold, Sire? The enemy is right there.
- passed_over
  > Others get the work and I get the waiting.

### Careful

Measured and orderly. Prefers odds, ground and an intact corps.

- object
  > Sire, I don't like those odds.
- passed_over
  > I stood idle while another was sent. It was not what I expected.

### To the letter

Flat and exact. Every line is about what was written.

- exact
  > As written, Sire: no more and no less.
- not_covered
  > I have no line for this, Sire.

---

## 6. The courts' headings on captured orders

Captured orders are headed in the court's own words (`COURTS`; `{name}` is the marshal the orders were written for). The plain reading of the orders follows the heading and says what they mean. A court not listed takes the empty-court heading. The heading is the same for a court on the historical seed and fixed by the seed otherwise; it is never a die, and no marshal says it, so it records nothing.

- Austria
  > From the war council in Vienna, to {name}:
  > Vienna's orders to {name}, signed and sealed:
- Russia
  > By command of the Tsar, to {name}:
  > From the Tsar's headquarters, to {name}:
- Prussia
  > The King's orders to {name}:
  > From Berlin, to {name}:
- Britain
  > From the Horse Guards in London, to {name}:
  > London's instructions to {name}:
- any other court
  > His court's orders to {name}:
  > Written orders for {name}:

Pin: `test_captured_orders_are_headed_in_the_courts_own_words`.

---

## 7. The older banks

The older banks were written before the plain-and-short ruling and keep a more period register. They are not yet rewritten and this guide does not require it.

- `marshal_voice.py`: the after-battle lines (`_OWN_PERSONALITY_LINES`, `_OWN_NAMED_LINES`), acknowledgements (`_ACK_LINES`, `LITERAL_ACK`, `LITERAL_EXACT`), completions (`_COMPLETION_LINES`, `LITERAL_COMPLETE`), the halt before a hopeless assault (`_MUSTER_HALT_LINES`), and the letter-following man's refusal to march (`LITERAL_NO_MARCH`).
- `enemy_voice.py`: the enemy's own lines after a battle (`_PERSONALITY_LINES`, `_NAMED_LINES`).
- `jealousy.py`: the petitions (`_PETITION_VOICE`, by personality).

Two things hold for them now: every bank carries four lines or more (pin `test_every_bank_of_the_older_pickers_is_four_or_more`), and every picker obeys the same "no line twice within his last three" rule through `said_lately` when it is given the man (pin `test_the_older_pickers_obey_the_rule_when_given_the_man`). The enemy's bank and the petitions are not covered by the plain-and-short or no-number rules.

---

## 8. How to add a line

1. Find the man's tuple in `own_voice.LINES[<key>][<kind>]` (the key has no accent: `Massena`). For a man with no set of his own, use `BY_NATURE[<nature>][<kind>]`.
2. **Append. Never reorder.** The first line of each set is the one said first on the historical seed, and the pins read that.
3. Keep the rules of section 1: plain, at most two sentences, at most 120 characters, no digit, no period word other than "Sire", none of his `NEVER_SAYS` words — and his MARK in it, so a reader who knows only the one-line sketches of the six would name him and nobody else.
4. Do not put a line in two sets. Check the other men's sets and the natures' sets first.
5. A kind in `RECURRING` needs four lines or more once his nature's lines are added. If you add a new kind a man can say on nights running, add it to `RECURRING`.
6. A line states no number and claims nothing the night did not hold (section 3).
7. `NEVER_SAYS` and `PERIOD_WORDS` change only with the user's word.
8. Run:

```
.venv/Scripts/python.exe -m pytest tests/test_ic13_every_man_his_own_line.py -q
```

---

## 9. How to add a man

1. Pick his nature (bold, careful or literal) and add him to the test's `NATURE_OF` and `PERSONALITY` tables in `tests/test_ic13_every_man_his_own_line.py`, and to its list of named men in `test_there_are_lines_for_every_man_the_design_names`.
2. Add `LINES["<Key>"]` in `own_voice.py`. Required for a man who judges for himself: `ack`, `bolder`, `careful`, `object`, `proposal` (if he ever proposes to take, chase or support), `proposal_hold`, `idle`, `struck`, `marched`, `waited`, `stayed`, `asks`, `done`, `third_night`, `after_win`, `after_loss`, `overruled`, `recalled`, `trial_ask`, `trial_won`, `trial_lost`, `remembers`; `dug_in` if he is a digger. Every `RECURRING` kind reaches four lines with his nature's lines. Required for a man who follows orders to the letter: `exact`, `repeat` (with `{orders}`), `not_covered`, `broken`, `refusal`, `done`, `overruled`, `trial_ask`, `trial_won`, `trial_lost`.
3. Add his `NEVER_SAYS` entry (the test requires one for every named man) with the user's word on what it holds.
4. Add what he remembers to `REMEMBERS`, or leave it to his nature in `REMEMBERS_BY_NATURE`. A letter-following man remembers nothing.
5. Check that no line is shared with another man, and that his own lines would not break his nature's ones (section 5): a kind he has no set for falls through to his nature.
6. Run the pin and the full `tests/test_ic13_every_man_his_own_line.py`.
7. Add him to section 4 of this guide: who he is, how he talks, what he never says, what he remembers, four exemplars quoted word for word.
