# The Peace Conundrum — why a crushed Austria cannot be brought to terms

**Date:** October 15, 2026 · **Source:** the user's live 1805 campaign (France, the second
backend on port 8006), turn 6, Early December 1805 · **Method:** read-only GETs against the
live game, code reading, and one in-process drive from a *copy* of the turn-6 autosave
(`tools/playtest_driver.py --from-save`, 2 end-turns, offers declined). The live game was
never written to. · **Status:** analysis + findings for the user's ruling. No code changed.

---

## 0. Verdict in six lines

1. France has won the Austrian war on every measure the game shows, yet **no road to peace
   is open on France's initiative** that is not either forbidden, unreachable, or gated on
   *liking* the beaten enemy.
2. The bilateral road is **forbidden** by France's own ally: Bavaria is still at war with
   Austria, and a separate peace that leaves an ally fighting is a hard stop (§2 F1).
3. The joint road is **arithmetically unreachable** while Britain is untouched: the coalition's
   pressure is an equal-weight average of three courts, and every court must reach 50 (§2 F4).
4. The truce road turns into peace on **relations, not on victory** — the victor must court
   the vanquished (§2 F7).
5. Meanwhile **Austria's own AI already wants out** (its war score is past its own sue-for-peace
   line and its break-ranks line) — and the game lets *Austria* write the very separate peace
   it forbids *France* to write (§2 F2, F8).
6. Three measurement faults sharpen the paradox: the war panel shows a different score than the
   one the peace math reads (F3), the AI reads last turn's score (F5), and a repulsed assault
   that killed three Austrians for every Frenchman was booked as a **decisive Austrian
   victory** (F6).

---

## 1. The situation (turn 6, Early December 1805)

| Measure | Value | Where read |
|---|---|---|
| War score, France vs Austria (live) | **+73** — territory 15, battles 15, decisive 0, capital 20, campaign 10, blood 15, ticking −2 | `/debug/war_scores`, armistice preview |
| War score, France vs Britain | **−2** (Britain's blockade) | `/debug/war_scores` |
| War score, France vs Russia | **0** (never met in battle) | `/debug/war_scores` |
| War panel headline | **"vs Britain · 71 · rising · Harsh Peace"** | `/status` → `active_wars` |
| Casualties | French 39,322 · Allied 103,293; 15 battles, 10 won | armistice preview |
| Held by France | Vienna (capital), Bohemia, Moravia, Tyrol, Swabia | campaign log |
| Austrian field army | Mack, a "screening force" in Hungary; Archduke Charles a prisoner in Paris; Archduke John's corps destroyed | `/status` |
| Coalition material share | Austria **94 %**, Russia 5 %, Britain **1 %** | war panel `contribution_share` |
| Relations France–Austria | −80 | `/debug/diplomatic_status` |
| Austria's design | **Revanche** sworn this turn (Bohemia, Tyrol) | campaign log, turn 6 |
| War exhaustion (start of turn 6) | Austria 113 · Britain 45 · Russia 45 (+8 a turn at war) | autosave copy |

The war is ONE war instance (`war_1`, labelled "France vs Britain"): France, Spain, Holland,
Bavaria and the Kingdom of Italy against the Third Coalition — Britain (leader), Austria,
Russia. Bavaria is France's **ally** (ALLIANCE, its own war with Austria); the Kingdom of Italy
is a **client** (vassal, follows France out of any truce or peace).

### The four doors, as the game offers them today

| Door | What the game says now | Why |
|---|---|---|
| **Propose Peace** (bilateral, France → Austria) | Greyed: *"Would break an ally's war — propose an armistice, or settle jointly"* | F1: Bavaria's war is a HARD_STOP |
| **Open Settlement** (whole coalition) | Will NOT carry — Austria 11/50, Britain 18/50, Russia 18/50 | F4: averaging + unanimity |
| **Propose Armistice** | Favorable, 64 (would be accepted) | — but F7: peace at expiry only if relations ≥ −60 |
| **Austria proposes** (AI P1) | No envoy yet | F5: the AI reads last turn's score; one is due at the next end-turn |

---

## 2. Findings

Severity key: **D** = defect (the code contradicts its own rule), **I** = inconsistency between
two rules, **L** = legibility (the player cannot see why), **G** = design gap.

### F1 — The bilateral peace is hard-stopped by France's own ally (G + L)

`get_peace_commitment_conflicts` (`backend/game_logic/diplomacy.py:5363`) walks France's
ALLIANCE / DEFENSIVE_ALLIANCE partners; any partner at WAR with the target makes the peace a
`HARD_STOP` (`:5456`). `treaty.can_sign(at_send=True)` reads it (`treaty.py:437-449`) and the
wizard greys the row with the short FA-D17 sentence (`diplomacy.py:12714`, `:13041`).

- **Legibility:** the chip never names the ally. The player sees "an ally's war" with no hint
  that the ally is Bavaria, nor that a two-step downgrade of the Bavarian alliance (to
  Non-Aggression; 1 DP each, Bavaria −15 then −20, all others −5 each, threat +5 each) would
  lift it.
- **Design:** this is the Peace of Pressburg moment. On 26 December 1805 Austria signed a
  separate peace while Britain and Russia fought on, and **Bavaria was a party to it** (it
  received Tyrol). The game's answer to "my ally is still at war with them" is to forbid the
  peace rather than to bring the ally to the table.

### F2 — The same separate peace is forbidden or allowed depending on who writes it (I)

One treaty — PEACE between France and Austria while Bavaria fights on — gets four verdicts:

| Road | Verdict | Evidence |
|---|---|---|
| France proposes | **HARD_STOP** | `diplomacy.py:5456` |
| Austria proposes, France accepts | **WARNING** ("she fights on alone") | `diplomacy.py:5430` (`if incoming:`) |
| A truce expires at relation ≥ −60 | **No check at all** | `_process_armistice_expiration`, `diplomacy.py:11179` |
| France had joined at an ally's call | **WARNING**, priced by the separate-peace penalty | `diplomacy.py:5438` |

Whatever the right rule is, it should be one rule. As built, the player is told the treaty is
a "diplomatic contradiction" — and then receives it by mail, or by waiting out a truce.

### F3 — Four different "war scores" for one war (L, borders on D)

| Score | Value | Who reads it |
|---|---|---|
| War panel headline ("vs Britain") | **71**, tier **Harsh Peace** | The player, every turn |
| Pair score France–Austria, live | **73** | Armistice preview, `/debug/war_scores` |
| Pair score France–Austria, *stored* | **54** (computed at the turn-5→6 advance, before Vienna fell) | The settlement scorer and the AI (`get_war_score_for`, `diplomacy.py:3852`) |
| Coalition side pressure | **17**, tier **white peace** | The settlement verdict (`settlement_scoring.py:337`) |

The panel aggregates every pair of the war under the leader's name and calls the result
"Harsh Peace". The settlement scorer reads the side pressure, files the war under **white
peace**, and charges a **−10 legitimacy penalty** for it (`settlement_scoring.py:483`, `:769`).
The player is shown a score that earns harsh terms and then told a white peace is illegitimate.
This is the user's own phrasing of the conundrum — *"my war score is very high against the
coalition"* — and on the panel it is.

Separately, every number the settlement verdict uses is **frozen for the turn**: stored scores
are recomputed once, inside `advance_turn` (`diplomacy.py:10750` via `world_state.py:11660`).
Taking Vienna this turn moved the panel to 71 and the preview to 73 but left the verdict on 54.

### F4 — The coalition math cannot be carried while Britain is untouched (G)

The joint settlement scores each court as:

> base side pressure (0.65 × the equal-weight mean of the three courts' scores)
> + tier legitimacy (−10 / 0 / +5 / +10 / +15 at 0 / 20 / 40 / 60 / 80)
> + own losses + objective alignment + war exhaustion (capped **+20**) + design − harshness …

and **every court must reach 50**.

Britain today: 11 (base) − 10 (white-peace tier) − 8 (design) + 5 (kept all) + 5 (objective)
+ 15 (exhaustion) = **18** — matching the live verdict exactly.

**Britain's ceiling while Britain and Russia are untouched.** Even if Austria's score reached
the maximum of 100, the mean is (100 − 2 + 0) / 3 ≈ 33, so the base is 21, the tier is
"favorable" (0), and with exhaustion maxed at 20: 21 + 0 − 8 + 5 + 5 + 20 = **43 < 50**.

**What it takes.** The side pressure must reach 40 (base 26, tier +5 → 53). That needs the
three courts' scores to sum to about 120: Austria at 100 **and** Russia + Britain at about +20
between them. At Austria's real 73, Russia + Britain need about +47.

So the peace of the whole war is set by the two courts that have done least of the fighting
(5 % and 1 % of the coalition's material effort) — with an equal vote, and Britain holding the
leader's pen. Austria's own court score (11) uses the *same* diluted base, not its own 54/73, and
charges it −15 for a capital France keeps under a no-terms package (`settlement_scoring.py:853`,
`:976`).

### F5 — The AI judges the war by last turn's score (D)

The end-turn order is: enemy military phase → **AI diplomatic phase**
(`turn_manager.py:547`) → … → `advance_turn()` (`:589`), which recalculates war scores
(`diplomacy.py:10750`). The AI's peace decision (`process_diplomatic_phase`, P1) therefore
reads the score *stored at the previous advance* — always one turn behind the battlefield.

Measured on the autosave copy (state at the start of turn 6):

| Austria's P1 input | Value |
|---|---|
| Stored score vs France | −54 |
| Effective peace threshold | **−44** = −40 base + 0 personality + 5 (exhaustion 113 // 20) − 1 ticking − 8 Revanche resolve (`ai_diplomacy.py:598`) |
| Break-ranks arms met | **score** (< −50) and **exhaustion** (113 > 80) (`ai_diplomacy.py:1533`) |
| P1 fires | yes |

**Reproduced:** driving one end-turn from the copy, Austria's envoy arrives with an
**armistice** (`armistice_losing`). The AI chooses peace rather than armistice only below
**−70** (`ai_diplomacy.py:1862`). Live, Austria is already at −73 — but at the next end-turn it
will still read −54 and ask only for a truce.

**Knock-on:** refusing that envoy sets a 3-turn per-nation cooldown, bypassed only if the score
drops a further 20 points (`_is_on_cooldown`, the R126 urgent arm). −54 → −73 is a 19-point
drop. So the ordinary way to answer an unwanted truce (refuse it) can delay the peace envoy by
about three turns.

### F6 — A repulsed assault that bled the garrison 3:1 was booked as a decisive Austrian victory (D)

Two of the turn-6 Vienna assaults did not break the garrison (`held: true`):

| Assault | Austrian dead | French dead | Recorded as |
|---|---|---|---|
| Davout | 8,030 | 4,657 | defender (Austrian) victory |
| Massena (first) | 8,485 | 2,872 | defender victory **and decisive** — ratio 2.95, total 11,357 |
| Massena (second) | 4,242 | 1,595 | garrison destroyed, Vienna taken |

- **The cause.** `_resolve_garrison_combat` sends a holding garrison through the post-combat
  pipeline as `defender_victory` (`combat_executor.py:5061-5069`). `record_battle` then
  credits a decisive battle to `winner_nation` whenever *either* side bled 2:1 over 10,000
  dead — without checking which side did the bleeding (`diplomacy.py:10631`).
- **The effect.** France's decisive component reads **0** (+10 for Swabia, −10 for "Vienna")
  instead of +10. The war's **second and last** decisive slot (max 2 per pair) is gone, so a
  future Austerlitz against Austria could no longer score.
- **What the panel shows.** It lists *both* repulsed assaults as decisive French defeats.
- **Sibling class (Rule 10):** any victory won at a 2:1 loss is credited as decisive *to the
  side that bled*. The predicate should credit the side that inflicted the exchange.

### F7 — The truce becomes peace on relations, not on the war (G)

An armistice lasts 5 turns. At expiry it becomes PEACE only if relations are ≥ −60
(`ARMISTICE_AUTO_PEACE_RELATION`, `diplomacy.py:4592`), otherwise the war resumes.

- **The thaw is not enough.** The 1805 boot's −80 thaws to −65 over one truce. To get peace,
  the winner must spend Talleyrand on Improve Relations (about +8 a turn) — courting the court
  it just beat. The user's reaction ("improving relations for peace is weird") is the correct
  one.
- **The score is wiped.** The truce strikes the battles from the war score ("if the war
  resumes, it resumes from nothing").
- **The score also erodes.** Battle records older than 10 turns are pruned from the score
  (`diplomacy.py:3797`). Every road that waits costs the victor score.
- **The peace is unsigned.** A truce that runs out into peace counts as an unsigned end, so
  contested treaty titles reopen (`game_end.resolve_contested_titles`).

### F8 — The Pressburg machinery exists, on one side only (G)

`coalition_break_ranks_reason` already has a **"pressburg" arm**: a member whose design is
satisfied breaks ranks at −30 instead of −50 (`ai_diplomacy.py:1533`; `agendas.py:34`). The
settlement offer gate reads the same predicate.

The game therefore already models *a coalition member who wants a separate peace* — but only
as something the AI may do. The player, who has driven Austria past every one of those lines,
has no verb that asks the question "will you leave the coalition?". Under Building Blocks
(same systems, different inputs) the player's proposal should be judged by the AI's own
predicate.

---

## 3. What this means for the live campaign

- **Next end-turn (prediction, reproduced on the copy).** Austria's envoy arrives with an
  **armistice**, because it reads −54, not −73.
- **If you accept the armistice:**
  - Five turns of truce, and the battle score is struck.
  - Peace only if relations reach −60; they are projected at −65 without Improve Relations.
  - The Kingdom of Italy follows you out; Bavaria keeps fighting Austria, with Bernadotte,
    Lannes and Murat on Bavarian soil.
- **If you refuse it:**
  - The per-nation cooldown runs 3 turns, unless the score collapses a further 20 points.
  - A peace envoy needs the AI to read a score below −70 *and* get past the cooldown. At the
    end of turn 7 it reads about −73, only 19 points past the refused −54, so the cooldown
    holds. The earliest is the end of turn 8, and only if a turn-7 victory takes the stored
    score below −74. Otherwise it comes when the cooldown lapses, around turn 10.
  - An *incoming* peace is only a WARNING on Bavaria (F2), so you could sign it.
- **The joint settlement stays shut** until Russia is beaten in the field (F4). Britain's
  exhaustion maxes out at +20 in about two turns, which is not enough on its own.

None of this is a recommendation to play one way; it is the board as the code reads it.

---

## 4. Recommendations for the user's ruling

**A. Conservative fixes (no new mechanic).** Each one makes the game say what it already does.

1. **F1 L.** Name the ally in every paradox refusal (wizard chip, counsel, Congress levers,
   typed refusal at `diplomatic_dialogue.py:1280`), and name both ways out: the armistice, and
   the downgrade.
2. **F3 L.** The war panel should show the number the peace math reads:
   - the per-court tally ("Austria ready · Britain 18/50 · Russia 18/50");
   - the scorer's tier, not the aggregate's;
   - a mid-turn note: "this turn's victories count from next turn".
3. **F6 D.** Credit a decisive exchange to the side that inflicted it, or not at all to a
   repulsed side. Rule on whether a garrison that *holds* should book a defender victory at
   all. Sweep the siblings: field battles won at 2:1 cost, and bombardment records.
4. **F5 D.** Run `recalculate_war_scores` before the AI diplomatic phase, or have P1 read the
   live score. This is a balance-touching change: the playtest baseline will shift and must be
   re-pinned.

**B. One rule for the separate peace (F2).** Pick one verdict for "PEACE with a court my ally
still fights", and apply it to all four roads. The options:

| Option | What it means | Cost |
|---|---|---|
| (a) | HARD_STOP everywhere | Closes the incoming and truce roads too: the game gets stricter and more frustrating. |
| (b) | WARNING everywhere | The ally fights on alone and resents it; priced by the existing separate-peace penalty. |
| (c) | Option C below — the ally comes to the table | The historically faithful answer. |

**C. Expansion — "The Pressburg Road" (recommended).**

- **The verb.** France may propose a *separate peace* to a single coalition member.
- **Who decides.** It is judged by that court's **own** pair score and the **AI's own
  break-ranks predicate** — one predicate, both sides (Building Blocks).
- **The treaty.** France's co-belligerents at war with that court are carried in as
  **co-signatories**. Bavaria's war with Austria ends in the same instrument, and Bavaria can
  be a named beneficiary; the war panel already marks it "Named beneficiary".
- **The costs, all from existing systems:**
  - The coalition loses a member, and its threat and cohesion react.
  - The court keeps its Revanche design.
  - Britain, abandoned, may subsidise a new partner.
- **Why this is the right answer.** It turns the strongest military result of the campaign into
  a meaningful diplomatic choice — dictate to Vienna now, or hold out for a general peace —
  instead of a greyed button. It is also how the Third and Fourth Coalitions actually ended
  (Pressburg 1805, Tilsit 1807).

**D. Expansion — "The Victor's Truce" (F7).** At expiry, an armistice converts to peace if
*either* relations ≥ −60 *or* the losing side's pair score is ≤ −50. The truce stops being a
courtship for a winner, and stays a reconciliation for a stalemate.

**E. Balance question (F4) — the user's call, not a defect.** Should the joint settlement
weight each court by its **contribution share** rather than by power tier, so that the court
which carried 94 % of the war carries matching weight in its end? Alternatively, keep equal
weights but let a court that has broken ranks be **covered separately**, which is C by another
name.

---

## 5. Evidence index

| Claim | Code | Live / measured |
|---|---|---|
| Paradox HARD_STOP | `diplomacy.py:5363`, `:5456`; `treaty.py:437-449` | `/diplomatic_preview?nation=Austria` → `propose_peace.closed_clause = "paradox"` |
| Incoming peace = WARNING | `diplomacy.py:5430` | — |
| Truce expiry has no paradox check | `diplomacy.py:11139-11200` | — |
| Side pressure / base / tier | `settlement_scoring.py:337`, `:694`, `:769`, `:483` | `/diplomatic_preview?mode=settlement&war_id=war_1` |
| Exhaustion cap +20 | `settlement_scoring.py:1563`, `:554` | Britain 45 → +15 |
| Stored vs live score | `diplomacy.py:3852` (stored), `:3809`/`:10750` (recalc) | direct score 54 vs live 73 |
| AI phase before recalc | `turn_manager.py:547` vs `:589` | drive from the copy: armistice envoy at −54 |
| P1 threshold, break-ranks, peace < −70 | `ai_diplomacy.py:598`, `:1533`, `:1862` | threshold −44; arms `score` + `exhaustion` |
| Cooldown / urgent bypass | `ai_diplomacy.py` `_is_on_cooldown` | — |
| Garrison held = defender victory | `combat_executor.py:5061-5069` | campaign log `garrison_assault … held: true` |
| Decisive credited to `winner_nation` | `diplomacy.py:10631` | panel: two "decisive" French defeats at Vienna; decisive component 0 |
| Battle records prune at 10 turns | `diplomacy.py:3797` | — |
| Truce → peace at −60 | `diplomacy.py:4592`, `:11179` | armistice preview: −80 → −65 projected |

Reproduction artefacts (scratch, not committed): the drive digest from the autosave copy, and
the read-only threshold probe. Re-derive by loading a copy of the turn-6 autosave with
`tools/playtest_driver.py --from-save <copy> --turns 2 --diplomacy decline`, with
`INK_IRON_SAVE_DIR` pointed at a scratch folder.
