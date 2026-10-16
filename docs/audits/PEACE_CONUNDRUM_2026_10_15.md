# The Peace Conundrum — why a crushed Austria cannot be brought to terms

**Date:** October 15, 2026 · **Source:** the user's live 1805 campaign (France, the second
backend on port 8006), turn 6, Early December 1805 · **Method:** read-only GETs against the
live game, code reading, and one in-process drive from a *copy* of the turn-6 autosave
(`tools/playtest_driver.py --from-save`, 2 end-turns, offers declined). The live game was
never written to. · **Status:** analysis + findings for the user's ruling. No code changed.

> **Update, October 16, 2026.** §4 A's four fixes landed in `40a3f7bc` (S13d: PC-F1, F3, F5,
> F6, with PC-X1 … X4; `BUG_FIXES.md` §PC). **Part II** (§6 onward) asks the wider question
> — does peace work, is it reactive, is it varied, is Talleyrand's advice worth having, does
> the war score climb too fast — and answers it from sixteen driven campaigns, per-turn and
> per-lever probes, and three code reads. It adds findings F9 … F22 and rulings F … H.
> **Part III** (§18 onward, October 16, 2026) tests the rulings as experiments, continues the
> user's game, and measures the losing side, France's own settlement table and the wars between
> AI courts; findings F23 … F33. **Part IV** (§27 onward, October 16, 2026) is the client study:
> what the player sees at each peace moment in the real client, at 5120×1440 and 1920×1080;
> findings F34 … F48. **Part V** (§35 onward, October 16, 2026) replays the five peaces of the
> period on the game's machinery, designs the rulings B–H (and two new ones, I and J), writes the
> copy for each peace moment, re-reads the earlier parts' assumptions, and files findings F49 … F88.
> **§46** (the same day, under the user's delegation) decides every ruling — B folded into C, C, D, I, E,
> H, G, J; F unchanged; K, Talleyrand's counsel alive, added — and re-sizes S13e to four parts.

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

---

# Part II — How peace works, measured (October 16, 2026)

Part I explained one stuck war. Part II asks whether peace works at all: how a war ends,
what the player can do about it, whether it varies from game to game, whether Talleyrand's
advice helps, and whether the war score climbs too fast. Everything below was run on master
at `40a3f7bc` (after §4 A's fixes) unless it says otherwise.

## 6. What was measured

| Instrument | What it is |
|---|---|
| **16 driven campaigns** | `tools/playtest_driver.py` Mode A (in-process, deterministic per seed), 40 turns each. A *commanded* France (`tools/playtest_scripts/commanded_full40.json`, which spends every action every turn) on five seeds — `historical`, `austerlitz`, `marengo`, `ulm`, `jena` — under three diplomacy policies: **decline** (refuse every envoy), **accept** (sign whatever is offered) and **propose** (France sues one court a turn and signs what it is offered). Plus one **passive** France (no orders; historical; decline). |
| **Per-turn probe** | On the five decline campaigns, a save every turn (after the player's orders, before end turn) — 40 a campaign. Each save was loaded read-only and read for every great power at war: the stored and live war score and its components, the war row and its peace table, Talleyrand's counsel, the acceptance of his own suggested peace and armistice, whether France may send them, the court's own peace threshold and break-ranks reason. 561 court-turns in all. |
| **Lever probe** | From one save, pull ONE lever at a time and re-read everything above. Run on a copy of the user's turn-6 save (France +54 against Austria) and on the austerlitz campaign at turn 9 (France +32). |
| **Live-case probes** | On the turn-6 copy with Vienna in French hands: what Austria's own AI phase sends at each score and war age; what a truce does to France's leverage. |
| **Three code reads** | War score; the AI's peace decisions; Talleyrand's counsel and terms — each with its own small probes. |

**The caveat that matters.** The commanded script is a fixed script, not a skilled player. It
peaks between +15 and +38 against Austria by turn 12. The user's own game reached **+73 by
turn 6**. Where the two differ, the lever probe on the user's save is the better guide.

## 7. The short answers

| Question | Answer |
|---|---|
| **Does the war score climb too fast?** | **Both too fast and too slow, in different places.** A pair score (France against one court) jumps early and then saturates: the first big battle is worth about +30 by turn 2 (decisive +15, blood +14), taking the capital is +25 in one step, and the battle component is full after five net wins, so every later victory adds nothing. Then it erodes: battle points decay after three quiet turns and expire after ten, and under the default war purpose the defender's claim ticks the occupier down to −25. The number that settles a *coalition* war — the side pressure — barely moves in France's favour: **never above 13 on any seed**, because Britain and Russia are never met in the field and their pair scores **never rise above 0 through turn 12 on any seed**. |
| **Is peace reactive?** | **To three levers strongly, to most not at all.** Taking the capital, the age of the war, and the terms you ask move a court's answer by 15–30 points. More victories (past five), relations, war exhaustion and Talleyrand's missions move it by **zero** (§11). The AI's own offers run on clocks more than on the battlefield (§10). |
| **Does it vary?** | **No.** No peace decision has any randomness in it, and shipped builds always run the `historical` seed, so the authored variance bands never reach a player (§13). Across five seeds the coalition war ended between turns 9 and 12, every time by the same letter. |
| **Is it fun?** | **Not as built.** The war ends by itself around turn 10 with a status-quo white peace the player did not shape. France's own overtures bounce off the alliance paradox or are refused. The strongest military result cannot be cashed: in the user's game a white peace from France would score 106 with Austria (it needs 50), but the paradox forbids sending it, Austria's own letter falls silent past −70 in a young war (F9), and accepting Austria's truce cuts France's leverage to zero (F17). The pieces for a good peace game are there — the break-ranks predicate, the Pressburg arm, the per-court table — but the player rarely gets to make a decision that matters. |
| **Is Talleyrand's advice worth having?** | **Rarely.** Four recommendations across 561 court-turns, one of them two-thirds of the time. His drafts are a bare white peace in a young war and grow absurd when France is losing. The recommendation, confidence and hints he computes never reach the screen — only his prose does. Two of his surfaces still offer a peace the game will refuse (§12). |

## 8. How the wars actually ended

**Signing what is offered (accept).**

| Seed | Austria's truce | The war ends | How |
|---|---|---|---|
| austerlitz | t9 | **t9** | Britain's settlement offer — white peace, 7 pairs resolved |
| historical | — | **t11** | Britain's settlement offer — white peace |
| jena | t7 | **t12** | Britain's settlement offer — white peace |
| marengo | t10 | **t12** | Britain's settlement offer — white peace |
| ulm | — | **t10** | Britain's settlement offer — white peace |

Every settlement carried a single term, `peace`, with no carves: each side keeps what it
holds. The war was ended by the coalition leader, on its own schedule, on the same terms,
on every seed.

**Suing every turn (propose).** France sent 16–35 overtures a campaign. Every one to Austria
or Britain while at war was refused at the send (Bavaria and Spain are still at war with them
— the paradox). Russia refused once (turn 3), then made peace or a truce at turns 8–11 (by
acceptance or counter). Britain's settlement still ended the war at turns 8–12. After Austria's truce in
ulm, France's peace to Austria was refused at turns 13 and 19, with the cooldown messages in
between.

**Refusing everything (decline).** The letters came on a cadence: Britain's settlement offer
every 5–6 turns (10, 15, 20, 27 …), Russia's truce every 7 (11, 18, 25), Austria's truce or
peace intermittently. A **passive** France — no orders at all — still received Austria's
peace (t11), Britain's truce (t12) and Britain's settlement (t13).

**After the peace.** Wars come back: on the accept arms Austria is at war again by turns
25–30, and on austerlitz Russia and Britain too by turns 37–39.

**The truces.** Of the truces that ran their course, **10 resumed the war and 2 became
peace**. The truce becomes peace only at relations of −60 or better (§14).

## 9. The war score

**The components** (`calculate_war_score`, `backend/game_logic/diplomacy.py` 3529–3674; a
pair score, positive = France winning, clamped to ±100):

| Component | Per event | Cap | Decays? | Wiped by |
|---|---|---|---|---|
| Territory | +5 per enemy *starting* province held | ±40 (Austria has 7: 35; practical 30) | no — live | — |
| Battles | +3 per net win (≥ 1,000 dead) | ±15 | yes: decays after 3 quiet turns; records expire after 10 | truce, peace |
| Decisive | +10 (> 10,000 dead, > 2:1, the winner inflicted it) | ±15; **2 slots per pair per war, shared** | no | truce, peace |
| Capital | +20 held (+10 besieged) | 20 in practice | no — live | — |
| Campaign | +2 per unique province taken this war | ±10 | no | peace only |
| Blood | 1 per 2,500 net enemy dead | ±15 | no | peace only |
| Blockade | min(15, turns ÷ 2) per side | ±15 | no | peace only |
| Captive eagle | ±15 while a sovereign is held | ±15 | live | release |
| Ticking | war purpose: conquest/forced alliance +2 a turn while the capital is held; **defense +1 a turn per own province the enemy holds**; liberation +1 | 25 per side | **never goes down** | peace |

**How fast, measured.**
- **The commanded campaigns** (France against Austria, stored, best by turn 12): austerlitz
  38, ulm 32, historical 28, marengo 19, jena 15. The opening battles carry it: by turn 2,
  decisive +15 and blood +14 on austerlitz and ulm. After that the battle component nets to
  about 0 (France and the AI trade wins), territory is small, and the score drifts down.
- **The user's game**: +73 at turn 6 — territory 15, battles 15, capital 20, campaign 10,
  blood 15, decisive 0, ticking −2. Battles, campaign and blood were already full.
- **A synthetic winning line** (code read; one win and one province a turn, Vienna on turn
  4): 9, 18, 26 (favourable), **53 on turn 4 (dictated)**, then 55–60. Harsh peace (60)
  arrives only by the slow blood creep (turn 13). **Total victory (80) is unreachable under
  the default purpose without decisives**: the ceiling is 30+15+20+10+15−25 = 65.
- **If the guns go quiet** after turn 6: the battle component falls 15 → 0 over turns 8–13
  and the total from 58 to 39 — back to favourable.

**Three numbers for one war.** France +58 against Austria and 0 against Britain and Russia
reads 58 on the live war row, 58 in the stored side sum, and **19 to the settlement scorer**,
which averages each court's best pair. The war row now shows the scorer's tier beside its own
score (PC-F3); the three still disagree.

## 10. How an AI court decides to offer peace

`process_diplomatic_phase` (`ai_diplomacy.py` 1693) — first match wins, no randomness:

1. **Captor** — a court holding the player's sovereign sends a harsh peace.
2. **Congress** — while a Congress sits, a great power at −40 or with its capital held sends a peace with a recognition clause.
3. **P1, losing** — the pair score is below the court's threshold: −40, ±20 for a hawk or dove, **+ war exhaustion ÷ 20**, ± ticking pressure, ± the design term. A coalition member also needs a break-ranks reason (score < −50; exhaustion > 80; or the Pressburg arm — design satisfied and score < −30). **Below −70 it sends a peace, otherwise an armistice.** The letter must clear the send filter (its acceptance from France's chair against a floor of 20, lowered for an honest letter).
4. **P2, stalemate** — a score within ±10 for several turns sends an armistice.
5. **P8, winning** — winning by more than 40 sends a harsh-peace demand.

Separately, **settlement offers** go out every 5 turns for each multi-party war that is two
turns old, once the opposing leader may break ranks. Their terms follow the side score: France
leading by 20+ is paid, trailing by 20 pays, in between a white peace — which is what every
measured settlement was.

**Exhaustion is a clock.** Austria's war exhaustion read about 20 at turn 1, 84–136 at turn 9
and the cap of 200 by turns 18–24 — on every seed, whatever the battlefield did (+8 a turn at
war, plus battle losses). The break-ranks "exhaustion" arm (> 80) was open from turns 6–9 on
every seed. So after about ten turns every coalition member is free to sue, and the
settlement letter's gate opens, even for a coalition that is winning. Exhaustion moves the
threshold by at most +10 and does not enter the bilateral acceptance at all.

**F9 — the silent band (live).** On the copy of the user's save with Vienna in French hands,
Austria's own AI phase sends:

| France's score | war age 6 | war age 8 | war age 10–14 |
|---|---|---|---|
| +50 to +69 | armistice | armistice | armistice |
| +71 to +80 | **nothing** | peace | peace |
| +95 | **nothing** | **nothing** | peace |

Below −70 P1 chooses a peace; in a young war the peace's score falls under the send filter
and there is no fallback to the armistice that would pass. **In the user's game (war started
turn 1) Austria at −73 sends nothing until the end of turn 9.** Before PC-F5 it read last
turn's −54 and would have sent the armistice; reading the true −73 puts it in the silent band.
The band existed before the fix (any court past −70 in a young war); PC-F5 is what puts this
game in it.

## 11. How a court answers France

`calculate_acceptance` (`diplomacy.py` 7952): **50 accepts, 30–49 counters, below 30
refuses**, read on arrival (a 15-point tolerance honours the at-send verdict). The terms: base
by type (peace 30, armistice 20 or 40), war score × 0.65, relations (clamped to ±10 at war),
+2 a turn of war (cap 20), the war-age penalty on extractive terms (−65 on the first turn,
fading to 0 by turn 8), the deal balance, harshness, the court's design, the battlefield
(+25 at a score of 70 with the capital held, +10 above 20), and smaller terms.

**What moves the answer** (one lever at a time; Austria's acceptance of Talleyrand's own
peace; armistice in brackets):

| Lever | User's save, turn 6 (France +54) | austerlitz, turn 9 (France +32) |
|---|---|---|
| One more victory | **0** (0) | +2 (+4) |
| Three more victories | **0** (0) | +5 (+8) |
| One decisive victory | +2 (+3) | +2 (+4) |
| Take the capital | **+15** (−15) | +8 (−9) |
| Relations +20 | **0** (0) | 0 (0) |
| War exhaustion +40 | **0** (0) | 0 (0) |
| Five more turns of war | **+18** (−12) | +4 (+4) |
| Lose a battle | −2 (−2) | 0 (0) |
| **His suggested terms vs a white peace** | **37 vs 67** | **30 vs 61** |

- **Victories stop counting** once the battle component is full; the user's save was already there.
- **Relations do nothing at war**: the term is clamped at −10 from −80 to −40, so Improve Relations moves no peace until relations pass −40.
- **Time is a lever as large as the capital**, through the war-age penalty on any term that asks for something.
- **Talleyrand's own terms are the biggest single cost**: his draft (a gold demand) scores 30 points below a plain white peace.
- **The paradox is the only thing between the user and peace.** With Vienna held (+79), a white peace from France scores **106** with Austria — accepted twice over — and the send road refuses it because Bavaria is still at war (F1; the ruling is B/C).

## 12. Talleyrand

**How the advice is made** (no LLM; fixed composition):
- **Counsel** (`_recommend_action`, `diplomatic_advisory.py` 1564) bands on the live pair score: above +20 "press for peace on favourable terms", below −20 "seek an armistice immediately", in between "the Tilsit model — win one more engagement". PC-F1 adds the paradox note. Hints are checked for *legality* (`can_sign`), never for whether the court would *accept*.
- **Suggested terms** (`generate_suggested_terms`, `diplomatic_templates.py` 3546): base terms from the score (a winning peace demands gold; a losing one offers gold, then provinces, men and an action point), tailored by the court's desires, capped, then **eased** — demands are stripped until the estimate is no longer a refusal. Easing only removes; it never adds a sweetener.

**What it said** (561 court-turns, five seeds):

| Recommendation | Share |
|---|---|
| "Win a battle, then propose peace." | 67 % |
| "Seek armistice immediately." | 25 % |
| "Propose an armistice — <ally> is still at war …" | 4 % |
| "Propose peace with strong terms." | 3 % |

His suggested peace, best and median acceptance by turn 12: Austria 52 / 25, Britain 49 / 25,
Russia 62 / 33. When he said "strong terms" his peace scored 15–36 — a refusal every time.

**Honesty.**
- **Young wars:** the war-age penalty makes any demand a refusal, so easing strips every draft to a white peace — including the "harsh" one — while the commentary still says "I've kept the demands firm but not humiliating" (F11).
- **Losing wars:** his draft demands back every captured marshal one by one. On ulm at turn 24 (seven French marshals in Austrian hands) it held seven prisoner-return demands *and* offered territory, gold, men and an action point: deal balance −262, acceptance **−250**. On marengo at turn 33, −116 (F13).
- **"What terms would they accept?"** says Austria "would likely accept" and offers "Propose these terms" on a peace the paradox refuses — the card is not stamped by the send verdict (the class of DDB-9 / PC-F1; F10). It also quotes the wrong price: 2 DP where the send charges 3.
- **The fields nobody sees.** The client renders only his prose; `recommendation`, `confidence_level` and `action_hints` are read by no `.gd` (F12).
- **His own mischief.** At authority 100 there is a 5 % chance a proposal is sabotaged; a white peace counts as "too generous" and gets 50 gold a turn bolted on, which turned a 53 into −14 in the probe (F22).
- **Two rolls for one draft.** Gold and men carry an unseeded ±20 % jitter, rolled separately on each surface: the card can quote 150 gold while the menu sends 182 (F14).

## 13. Variance

- **No randomness in any peace decision.** `calculate_acceptance`, the settlement scorer, the baseline and every P-rung are pure functions of the board. The same state gives the same answer, in the same order.
- **Shipped builds run the historical seed.** `/new_game` takes no seed; with `SOVEREIGN_SEED` unset the world resolves to `historical`, where every authored variance band collapses to zero. The AI Intent spec left "new campaigns default to a random seed" as a re-check decision that was never taken.
- **Where variance does come from:** combat dice and the AI's attack moods, and the player's own choices. That is enough to move *when* things happen by a turn or two, not *what* happens: the five seeds ended the war at turns 9–12 with the same letter.

## 14. The truce

- **A truce wipes the victor's leverage.** It clears the pair's stored score, battles and decisives. On the user's save with Vienna held, France's white peace scored **106 at war and 0 under the truce**: the war-score term went from +51 to 0, the battlefield bonuses went, and the relations term widened from −10 to −30 (F17).
- **It ends in peace only on relations.** A truce becomes peace at −60 or better; the truce thaws about +3 a turn, so a −80 court reaches −65 and the war resumes. Measured: 10 truces resumed the war, 2 became peace.
- **The AI asks for exactly this truce.** A beaten court between −50 and −70 sends `armistice_losing`; the player who accepts it gives up the score that made the court sue.

## 15. New findings

Severity: **D** defect, **G** design gap, **L** legibility, as in Part I.

| # | Kind | Finding | Evidence |
|---|---|---|---|
| **F9** | D | **The silent band.** A court past −70 in a young war (under 8 turns; under 10 at −95) sends nothing: P1 picks a peace, the send filter drops it, no armistice fallback. The user's Austria is in it until turn 9. | §10 table; `ai_diplomacy.py` 1862, 2217–2268 |
| **F10** | D | **The feasibility card offers a refused peace** ("Propose these terms" under the paradox) and **misquotes its price** (2 DP shown, 3 charged). Sibling of DDB-9 / PC-F1, missed by S13d's sweep. | `diplomatic_dialogue.py` 2060–2085 (not passed through `_stamp_menu_sends`), 2062 |
| **F11** | L | **The commentary promises demands the draft does not have** ("firm but not humiliating" on a white peace). | `diplomatic_templates.py` 3726–3732 |
| **F12** | L | **Talleyrand's recommendation, confidence and hints never reach the screen**; the gating that protects them (DD-1) protects nothing the player sees. | no `.gd` reads `action_hints` / `confidence_level` |
| **F13** | D | **The losing draft is absurd**: one prisoner-return demand per captured marshal plus every concession at once (−250). | §12; ulm t24, marengo t33 |
| **F14** | L | **Unseeded ±20 % jitter, rolled per surface**: the card, the menu and the objection see different amounts. | `diplomatic_templates.py` 4186–4198 |
| **F15** | G | **Victories stop counting after five**; the battle cap is applied before decay; two decisive slots per war, shared by both sides. | §9, §11 |
| **F16** | G | **The default war purpose taxes the winner**: the defender's claim ticks the occupier to −25 and never goes down, so total victory is unreachable without decisives. | §9; `diplomacy.py` 4477–4551 |
| **F17** | G | **A truce resets France's leverage to zero** while the AI's peace still turns on relations France cannot reach. | §14 |
| **F18** | G | **Relations do nothing for peace at war** (clamped at −10 below −40), yet decide whether a truce becomes peace — the one place they matter is the one place the player cannot move them. | §11, §14 |
| **F19** | G | **Exhaustion is a clock, not a consequence**: +8 a turn to 200 on every seed; it frees every coalition member around turn 11 and never enters the bilateral answer. | §10 |
| **F20** | D | **Coalition loyalty binds the AI's offers but not its acceptance**: `get_coalition_loyalty_penalty` has no caller (the module header says the acceptance formula reads it). A member blocked from suing still accepts France's white peace (53). P2 and P8 also lack P1's coalition and pending-settlement gates. | `coalition.py` 2008; `ai_diplomacy.py` 1878, 2009 |
| **F21** | G | **The coalition's peace is scheduled, not willed**: a settlement letter every 5 turns, always a white peace in the runs; `_letter_would_carry` counts every covered court as consenting. | §8, §10; `ai_diplomacy.py` 4610–4626 |
| **F22** | D | **Talleyrand's sabotage turns a white peace into a refusal** (+50 gold a turn, applied after the estimate and the verdict). | `diplomatic_defiance.py` 279–291; `diplomatic_executor.py` 4842–4856 |

## 16. What this means for the rulings

Part I's rulings stand, and Part II sharpens them:

- **B and C (the separate peace, the Pressburg road)** are confirmed as the centre of it: with Vienna held a white peace would be accepted at 106, and only the paradox stops it.
- **D (the victor's truce)** is now F17 and F18 together: a truce is a trap for the winner twice over — it zeroes the score and it can end in peace only through relations the war will not let France repair.
- **E (who prices the coalition's peace)** is now F21 as well: the coalition's peace arrives on a timer with no terms, so the question is also whether the coalition should ever *offer* something other than the status quo.

Three new rulings:

| | Ruling | Options |
|---|---|---|
| **F** | **Variance.** | (a) leave every campaign `historical` (today); (b) new campaigns roll a seed — the bands are authored and pinned; (c) a "historical / varied" choice on the new-game screen. |
| **G** | **The shape of the war score.** | (a) leave it; (b) let battles keep counting (cap after decay, or a larger cap) and give the default purpose's ticking a ceiling that falls when provinces are returned; (c) make a conquest purpose the default for the side that declared. |
| **H** | **What wears a court down.** | (a) exhaustion stays a clock; (b) exhaustion grows from losses and occupation rather than time, and enters the bilateral answer as the settlement scorer already lets it. |

**Recommended order.** Fix the defects first (F9, F10, F13, F20, F22, with F11, F12 and F14
as legibility rows) — F9 first, because it is live in the user's game. Then rule B/C and D,
because they are what the user met. Then F, G and H, which are balance and want a measured pass
of their own.

## 17. Evidence for Part II

| Claim | Source |
|---|---|
| The five war endings, the envoy cadence, the overtures | driven digests (`peace_timeline.txt`, `peace_summary.json`) |
| Score trajectories, exhaustion, thresholds, counsel shares, Talleyrand's acceptance | the per-turn probe over 5 × 40 saves (`probe.jsonl`) |
| The lever table | the lever probe on the user's turn-6 copy and austerlitz t9 |
| The silent band, the truce's cost | the live-case probes on the turn-6 copy |
| Component caps, the synthetic line, the three aggregations | the war-score code read (`diplomacy.py` 3446–3674, 3800–3818, 4241, 4477–4551) |
| The decision tree, cooldowns, no randomness, the seed | the AI-decision code read (`ai_diplomacy.py` 598, 1533, 1693–2268, 4610, 5069; `main.py` 6090; `campaign_variance.py` 41) |
| Talleyrand's composition, honesty and jitter | the Talleyrand code read (`diplomatic_advisory.py` 1541–1669; `diplomatic_templates.py` 3546–4239; `diplomatic_dialogue.py` 1947–2085; `diplomatic_defiance.py`) |

The scripts and data are scratch, not committed. To re-derive: drive the commanded script with
`tools/playtest_driver.py --script tools/playtest_scripts/commanded_full40.json --turns 40
--seed <seed> --diplomacy decline --save-at 1,2,…,40` (with `INK_IRON_SAVE_DIR` in a scratch
folder), then load each save read-only and read `calculate_war_score`, `build_active_wars`,
`_recommend_action`, `generate_suggested_terms(..., deterministic=True)` +
`calculate_acceptance`, `effective_peace_threshold` and `coalition_break_ranks_reason`.

---

# Part III — Five more studies (October 16, 2026)

Part II measured how peace works today. Part III tests the rulings before they are made,
continues the user's own game, and looks at the three corners Part II did not reach: the
losing side, France's own settlement table, and the wars between AI courts. Run on master at
`a7e6fb3a` (which includes the CC-2 commit `4645de5f`). Nothing here changed the game.

## 18. What was run

| Study | What it is |
|---|---|
| **1. The rulings as experiments** | Each proposed ruling turned into a temporary switch, applied inside the driver's own process (never on master), then the commanded 40-turn campaign driven on the five seeds. 67 campaigns: every arm under **accept**, and the arms where France's own peace matters (BASE, F9, B, C) under **propose** as well. |
| **2. Your game, continued** | The copy of the user's turn-6 save with Vienna put in French hands (Massena in the city, the garrison gone), driven 15 more turns with France holding what it has, under accept / propose / decline and the arms BASE, F9, B, C, D. |
| **3. The losing side** | A passive France (no orders) that signs whatever it is offered, five seeds. |
| **4. France's own table** | The joint settlement swept on 48 boards and the two live ones: 934 packages, every court scored; one staged and ratified on an in-memory copy. |
| **5. Wars between AI courts** | Every AI–AI war in the per-turn saves of Part II: 193 saves, 39 pair-wars, plus the AI–AI peace code. |

**The switches are approximations, not designs.** B makes the paradox a warning. C adds that a
France–X peace also ends each French ally's war with X. D makes a truce end in peace when the
loser's live score is −50 or worse. E weights each court by its material share of the war in
the settlement scorer. F9 sends the armistice when a beaten court's peace would fail its send
check. G raises the battle cap from 15 to 30 and lowers the war-purpose ticking cap from 25 to
10. H stops the per-turn exhaustion tick, so exhaustion comes from losses only. Each is the
smallest change that answers its ruling's question; a built ruling would be designed properly.

The client study (what the screens show at the peace moments) was not run here: it needs the
Godot client driven against a spare backend. It ran the same day as Part IV (§27 onward).

## 19. The rulings as experiments

**Signing what is offered (accept)** — when Austria's war ended, and when the coalition's did,
on austerlitz / historical / jena / marengo / ulm:

| Arm | Austria's war ends | The coalition's war ends | France's provinces at t40 | Truces → war / peace |
|---|---|---|---|---|
| **As shipped** | 9, 11, 7, 10, 10 | 9, 11, 12, 12, 10 | 28, 24, 29, 26, 20 | 2 / 1 |
| F9, B, C, D, E, G | **identical to shipped** | identical | identical | identical |
| **H — no exhaustion clock** | 9, **33**, 8, 13, **25** | **16, 33, 28, 35, 25** | 26, 25, 24, 26, **13** | **11 / 3** |

**Suing every turn (propose)** — Austria's war, and France at turn 40:

| Seed | As shipped | B (the paradox warns) | C (B + the allies co-sign) |
|---|---|---|---|
| austerlitz | truce t5 · **at war with Austria, Britain, Russia at t40** · 29 provinces | truce t5 · at peace · 28 | truce t5 · at peace · 28 |
| historical | settlement t11 · **at war with all three at t40** · 27 | settlement t11 · at peace · 28 | settlement t11 · at peace · 28 |
| jena | truce t6 · at peace · 28 | **peace t7** · at peace · **16** | **peace t7** · at peace · 28 |
| marengo | settlement t11 · **at war with Britain, Russia** · 27 | **peace t7** · at peace · 22 | **peace t7** · at peace · 28 |
| ulm | truce t8 · at peace · 20 | settlement t10 · at peace · 16 | settlement t10 · at peace · 21 |

What the experiments say:

- **Nothing about the score decides when a war ends; the clock does.** F9, B, C, D, E and G change nothing in the accept campaigns. G changes the shape of the war score and E the scorer's weights, yet the wars ended on the same turns with the same letters, because the letters are driven by the exhaustion clock and the settlement schedule (§10). **H is the only arm that moves the accept campaigns**, and it moves them a lot: without the per-turn exhaustion tick the coalition's war runs to turns 16–35, eleven truces collapse back into war, and on ulm France falls to 13 provinces. The clock is load-bearing: remove it and nothing else ends the wars.
- **B and C give France a peace that lasts.** When France sues, the shipped game leaves France at war with a major at turn 40 on three seeds of five (its truces collapse, and later wars resume); under B or C, on none. On jena and marengo Austria accepts France's own peace at turn 7.
- **C keeps what B loses.** Under B France keeps 16–22 provinces on three seeds; under C, 28 on four and 21 on ulm. On jena, B's separate peace — Bavaria left fighting — was followed by a Fourth Coalition at turn 32 (Austria, Britain, Hanover, Russia, Sardinia, Sweden) that took French provinces before France made peace court by court; under C, with Bavaria's war ended in the same instrument, no new coalition formed in the campaign. One seed is a path, not a law; but every C run kept France at least as large as its B twin.
- **D never fired.** In 40 commanded turns no truce reached its expiry with a loser at −50 or worse: France's truces were superseded by Britain's settlement first, or the score behind them was small. A victor's truce matters only for a France winning big, which the scripted France never is.
- **E changes France's own table, not the AI's.** The coalition's settlement letters are white peace either way (they follow the side score's ±20 bands, not the scorer). On the user's boards E is decisive (§22): weighted by material share (Austria 99 %), France's white peace carries with every court — 56 / 51 / 51, and 63 / 70 / 70 with Vienna held.
- **F9 is invisible here** because the scripted France never drives a court past −70; it matters on the user's board (§20).

## 20. Your game, continued

The copy of the user's turn-6 save, with Vienna put in French hands as it was after the
assaults (Massena in the city, the garrison gone), driven 15 more turns with France holding
what it has (no new orders), under each policy and the arms that bear on it.

| Arm | What happened (signing what is offered) | When the war with Austria ended | When the whole war ended |
|---|---|---|---|
| **As shipped** | Austria silent at turn 6 (F9's band). Russia's truce t7, Austria's truce t9 (signed t10), Britain's settlement t10, ratified t11. | t10 (truce) | **t11** |
| **F9 fallback** | Austria's truce arrives at once (t6, signed t7). Britain's settlement at t11 then covers only Britain and Russia — Austria, already in a truce, is left out of it. | **t7** (truce) | t11 — without Austria |
| **B** (the paradox warns) — suing | France's own peace to Austria is **accepted at turn 6**. Russia counters at t7 (signed t8); Britain's settlement t8. | **t6** (peace) | **t8** |
| **C** (B + the ally co-signs) — suing | As B; Bavaria's war with Austria ends in the same instrument. | **t6** (peace) | **t8** |
| **D** (the victor's truce) | No change within 15 turns: the truce that expired (Russia's, t12) had no war score behind it. | t10 | t11 |

- **What the status quo gives.** The settlement that ends the shipped line reads "Bohemia, Tyrol and **Vienna** stay ours by the treaty" — the coalition's "white peace" is *uti possidetis*: each side keeps what it holds. For a France standing in Vienna that is a conquest, not a white peace; the tier label hides it.
- **Refusing everything** (decline, every arm): Russia's truce t7, Austria's t10, Britain's settlement t11 and t16, Russia's *peace* t19 — the letters keep coming on the clocks of §10.
- **F9's trade-off.** The fallback ends the silent band — Austria's truce comes three turns sooner — but a court in a truce is not covered by the next settlement. The fix should be paired with the settlement covering a court whose truce it outlasts, or the player should be told that accepting the truce takes Austria off the table.
- **Rulings B / C are the fast road**: the white peace France can already afford (106 with Vienna held, §11) goes through on the turn it is sent.

## 21. The losing side

A passive France (no orders) that signs whatever it is offered, on the five seeds:

| Seed | Austria's war ends | The coalition settles | Terms | France's provinces t10 / 20 / 30 / 40 |
|---|---|---|---|---|
| austerlitz | t7 truce | t12 | white peace | 28 / 28 / 24 / 24 |
| historical | t12 peace | t13 | white peace | 28 / 25 / 25 / 25 |
| jena | t13 settlement | t13 | **France pays Britain 4,357 gold; Franche-Comté stays Austrian** | 27 / 27 / 27 / 26 |
| marengo | t6 truce | t12 | white peace | 28 / 28 / 28 / 28 |
| ulm | t7 truce | t12 | white peace | 28 / 19 / 13 / 13 |

- **Losing is cheap and quick.** Courts that are *winning* still send truces and peaces from turn 6 (Austria at +25 offered peace on historical), and the coalition settles at turns 12–13. Four seeds of five end in a white peace; one charges France 4,357 gold and keeps a French home province.
- **The trap is the truce, again.** On ulm France accepted four truces; two expired into war, and Austria's renewed wars took France from 28 provinces to 13 by turn 30 — the only seed where a losing France was hurt, and it was hurt *after* accepting peace terms.
- **No harsh terms were imposed** on any seed: the winning AI's harsh-peace rung (P8, winning by more than 40) never sent a letter, and the snapshots never show a court ahead of the passive France by more than 26 before the clocks of §10 brought a settlement.

## 22. Can France's own settlement carry?

The joint table (Open Settlement) was swept on 48 boards from the five campaigns (turns 3–35)
and on the two live boards: white peace, partial coverage, Talleyrand's baseline, France
paying gold, France ceding a province, and the presets — 934 packages, every court scored.
One package was staged and ratified on an in-memory copy of the live world.

**A white peace never carries; a paid peace always does.**

| Package | Result |
|---|---|
| White peace, all three courts | never carries — the best worst-court score on any board is 27 |
| **France pays one court gold** | **carries on every board**. On the user's turn-6 board: 775 gold falls short (49), **800 gold carries** (Austria 55, Britain 50, Russia 50) and ratifies — the treasury goes 4,688 → 3,888 and the whole war ends. With Vienna held it takes about 1,000 (51 / 58 / 58). |
| France cedes a province back | +35 to every court: returning Bohemia or Tyrol carries the user's board (78 / 53 / 53) |
| **Austria alone** (the table can drop courts) | a white peace **carries on the user's boards** (62; 50 with Vienna held) and ratifies — France at peace with Austria, still at war with Britain and Russia |
| Talleyrand's baseline | a bare peace wherever France is not losing — never carries |
| **Courts weighted by their share of the war** (ruling E, re-scored) | a white peace **carries on the user's boards**: 56 / 51 / 51, and 63 / 70 / 70 with Vienna held (Austria carried 99 % of the coalition's material effort) |

- **Why a white peace fails.** The scorer averages France's war across every covered court, and Britain and Russia sit at 0 all game. The user's +54 against Austria averages to 17 — the white-peace tier, a −10 on every court — and +79 with Vienna averages to 26, the best on any board. To carry unpaid, France would need about +58 *averaged*: beating Britain and Russia in the field.
- **What a point costs.** The scorer credits one point per 25 gold France pays, up to 40 per clause (1,000 gold) and 120 in all. The price of the war is therefore **25 gold × (50 − the worst court's score)**: 575–1,300 gold across the boards, median 1,025 — 6–50 % of France's treasury, about 17 % typically.
- **One payment buys every court (F23).** A payment to any one court lifts *every* court's score equally: 1,000 gold to Russia gives exactly the table that 1,000 to Britain gives. "Every court must reach 50" is bought by paying the cheapest court once.
- **A separate peace through the table (F24).** Dropping Britain and Russia from coverage turns the joint table into a bilateral peace with Austria that the ratifier signs — the very treaty the alliance paradox forbids on the bilateral road (Part I F1–F2). It is a **fifth road with a fifth verdict**.
- **Nobody tells the player.** Talleyrand's baseline prices a point at 100 gold (four times the scorer's 25), aims at 35 rather than 50 and pays up to 1,500 a clause, beyond the 1,000 the scorer credits: on jena t12–20 and ulm t15–20 his draft pays 1,500 to Austria and still does not carry (F25). A France-pays package that falls short is told "the terms claim a victory the field has not delivered" — the phrase SRX-6 and DDB-6 fixed for other shapes (F26). Ceding French home soil lowers *every* court's score (France's defense objective "contradicts" it, −20), which reads backwards (F27).

## 23. Peace between AI courts

Every AI–AI war in the five refuse-everything campaigns and the passive one (193 saves; 39 pair-wars):

| Origin | How they ended | How long |
|---|---|---|
| **Declared by an AI during play** (Prussia → Hanover, "The Hanoverian Prize", on every seed) | negotiated at the first chance: Hanover pays 1,670–3,222 gold, Prussia keeps what it took | exactly 3 turns (the minimum) |
| Britain–Spain (1805) | a white peace by exhaustion at turn 15, every seed | 15 |
| **Austria–Bavaria (1805)** — the war behind France's paradox | the exhausted-pair exit at turns 14 (austerlitz, ulm), 16 (historical), 24 (jena); **Bavaria eliminated** at t27 on marengo (t14 for the passive France) | 14–27 |
| Austria–Kingdom of Italy, Britain–Holland (France's clients) | elimination, a defection, or still running at turn 40 (31–40 turns, both at exhaustion 200) | to 40+ |
| Cascades from Switzerland's rebellion | all ended by Switzerland's elimination | 1–10 |

- **Two kinds of war, two rules.** A war an AI declares stands in its own war instance, and its loser sues through the same threshold P1 reads — it ends in three turns. The 1805 wars are all folded into France's own instance, and there a loser **never sues**: the only exits are the exhausted-pair white peace (both sides' exhaustion ≥ 120, ten turns of war, the pair score within ±15), elimination, or a client's defection (`settlement_third_party.py` 48–50, 365–370, 456–491). A decisive sub-war has no road out: marengo's Austria–Bavaria sat at +35 to +60 for eight turns until Bavaria was destroyed (F28).
- **The paradox lifts by itself — sometimes.** Bavaria's war with Austria ended on its own at turns 14–24 on four seeds, which frees France's bilateral peace from then on. Nothing tells the player when that happens.
- **Clients have no exit** (F29). A client's pair is excluded from the exhausted-pair exit, so Britain–Holland and Austria–Italy run at exhaustion 200 for 15+ turns. A client that defects keeps fighting its new lord's ally: on marengo Holland went over to Russia at t32 and Britain, Russia's ally, was still taking Holland's provinces at t38 (`vassal.py` 729–732 skips pairs whose instance either court leads; the 1805 boot made Britain the leader of France's instance) (F30).
- **A latent silent band of their own** (F31). Between AI courts there is no −70 peace/armistice split and no send filter, so P1's band does not recur; but when the loser has crossed its threshold while the winner's score is still under 20, the package is a white peace the scorer rejects, it is not "surrender-shaped", the broker does not fire (it fires only *above* the threshold) and there is no AI–AI armistice: nothing is sent. Probed on the Prussia–Hanover war: Hanover at −12, −15, −19 — nothing; at −20 — peace with 1,899 gold. Not met in the runs (that war jumped from −3 to −40 in one turn).

## 24. New findings

| # | Kind | Finding | Evidence |
|---|---|---|---|
| **F23** | G | **One payment buys every court.** A gold payment or cession to any one court lifts every court's score equally (`settlement_scoring.py` 1528–1536 credits the whole accepting side), so "every court must reach 50" is met by paying the cheapest court once. | §22 |
| **F24** | I | **A fifth road to the separate peace.** Dropping courts from the settlement table yields a bilateral peace with Austria that the ratifier signs, while the bilateral road calls the same treaty a paradox. Part I F2's four verdicts are now five. | §22 |
| **F25** | D | **Talleyrand's settlement baseline is mis-priced**: 100 gold per point of gap (`settlement_baseline.py` 1609) against the scorer's 25, aimed at 35 not 50, up to 1,500 a clause beyond the 1,000 the scorer credits — it pays 1,500 and still does not carry. | §22 |
| **F26** | L | **A France-pays package that falls short is told "the terms claim a victory the field has not delivered"** — the white-peace tier's −10, not a claim (`diplomatic_templates.py` 2589; the class SRX-6 and DDB-6 fixed for other shapes). | §22 |
| **F27** | D | **Ceding French home soil lowers every court's score** (France's defense objective "contradicts" the cession, −20 on every court); the receiving court should not like the deal less. *Inference from the scorer; to verify.* | §22 |
| **F28** | G | **A decisive war between AI courts inside France's war has no exit**: the 1805 wars are folded into France's instance, where a loser never sues; only a stagnant score, elimination or a defection ends them. | §23 |
| **F29** | D | **A client's pairs have no exit at all**: excluded from the exhausted-pair exit, Britain–Holland and Austria–Italy ran 15+ turns at exhaustion 200. | §23 |
| **F30** | D | **A client that defects keeps fighting its new lord's ally**: Holland, gone over to Russia, still at war with Britain (Russia's ally) eight turns later (`vassal.py` 729–732). | §23 |
| **F31** | D | **A latent silent band between AI courts**: a loser past its threshold while the winner is under 20 sends nothing (a rejected white peace, no armistice, the broker not firing). | §23 |
| **F32** | G | **F9's fallback takes the court out of the next settlement**: a court in a truce is not covered, so on the user's board the settlement no longer confirms Vienna. A fix to F9 should keep the court covered, or say so. | §20 |
| **F33** | L | **The "white peace" is *uti possidetis***: it confirms every province each side holds — Vienna included — while the tier, the panel and the letter call it a white peace. | §20, §21 |

## 25. The rulings, re-read with data

| Ruling | What the experiments say | Recommendation |
|---|---|---|
| **B** one verdict for the separate peace | Lets France's own peace through: no major at war with France at t40 on any seed (shipped: 3 of 5). But a separate peace that leaves an ally fighting cost France provinces on three seeds and, on jena, a new coalition. | **Take C rather than B (b).** |
| **C** the Pressburg road | Everything B gives, and France keeps its provinces (28 on four seeds, 21 on ulm); the ally's war ends in the same instrument; no new coalition on any seed. On the user's board, Austria accepts at turn 6 and the whole war ends at turn 8. | **Build C.** It is the one ruling that gave the player a peace that was both available and lasting. |
| **D** the victor's truce | Never fired in 67 campaigns: the scripted France never held a truce with a loser past −50 at expiry. | **Defer.** It would matter for a France winning big, and C covers that case directly. |
| **E** who prices the coalition's peace | No effect on the coalition's own offers; decisive on France's own table (the user's white peace carries at 56 / 51 / 51). F23 is the other half: today one payment carries every court. | **Rule E together with F23**: weight the courts by their share of the war, and make a payment count for the court it is paid to. |
| **F** variance | Measured in Part II: seeds move the end of the war by at most three turns. | Unchanged: the user's call, and no peace outcome depends on it. |
| **G** the shape of the war score | No effect on when or how wars end. | **Low priority** for peace; worth doing for the war score's own legibility (victories that count, a ticking that can fall). |
| **H** what wears a court down | The exhaustion clock is what ends wars today; without it wars run 2–3 times longer and France bleeds. | **Keep the clock** unless something else ends wars. If exhaustion should come from losses, raise what losses cost before removing the time term. |

**The recommended order, now with data:** the S13e defects (F9 first, live in the user's
game), then **C**, then **E with F23**; D and G after; F and H stay the user's.

## 26. Evidence for Part III

| Claim | Source |
|---|---|
| The ruling arms | 67 driven campaigns (`run_rulings.py`: one switch per arm, applied in the driver's process); digests, saves at t10/20/30/40, reach counters |
| Your game, continued | 15 runs from the Vienna-held copy of the turn-6 save |
| The losing side | 5 passive campaigns, saves at t10/20/30/40 |
| France's own table | 934 scored packages on 50 boards; one staged and ratified in memory; the user's boards re-checked (800 gold carries 55 / 50 / 50; Austria alone 62) |
| E on the user's boards | the scorer re-run with the courts weighted by material share (Austria 0.99, Britain 0.01, Russia 0.00) |
| AI–AI wars | 193 saves; `settlement_third_party.py` 48–50, 351–383, 456–491; `ai_diplomacy.py` 3781, 3968–4100; `vassal.py` 729–732 |

The scripts and data are scratch, not committed. To re-derive a ruling arm: apply the switch in
a bootstrap that then runs `tools/playtest_driver.py` through `runpy` in the same process, with
`PYTHONHASHSEED=0` (so the driver does not re-launch itself) and the child's stdin closed (a
batch with stdin inherited stalled mid-run once).

---

# Part IV — What the player sees (October 16, 2026)

Parts I–III read the peace math in code and in campaigns. Part IV asks whether the screens
carry it: at each peace moment, does the client answer *"why won't they make peace, and what
can I do?"* without a report? Run on master at `06b24faa`. Nothing here changed the game.

## 27. What was captured

| | |
|---|---|
| **The client** | The real Godot client — the title screen, then `main.tscn` — driven one player action at a time by DD-B's hands (`tools/dd_b_client.gd` through `tools/dd_b_play.py`; `docs/PLAYTESTING.md` Mode C): real clicks and keys, a frame and a state record per action. A scratch copy of the client added two things and changed nothing else: the window size, and a `hover` action that rests the pointer and waits for the engine's own tooltip, so the tooltips are drawn as a player sees them. |
| **The backend** | A sandboxed `-m backend.main` on port 8017, saves in a scratch folder, the mock parser, the historical seed. 8005 and 8006 were never touched. |
| **The boards** | The two copies of the user's turn-6 save that Parts II–III used. **Vienna held**: France in the city; France against Austria +79 live, +54 stored. **The turn-6 copy**: Vienna still Austrian, +54. Both were loaded through the menu's Continue and Load, as a player would. |
| **The sizes** | **5120×1440** at the Interface Scale the game derives for it (140 %), the user's monitor. **1920×1080** at 100 %, which is what that screen derives. The window was set to 100 % with Ctrl+−, because the menu derives its scale from the physical monitor, not from the window. |
| **The runs** | Six runs, 147 actions, 0 SCRIPT ERRORs. 33 frames are kept in `docs/audits/peace_client/`, one crop per moment per size. `moments.json` beside them holds each frame's own record of the lines and controls it shows. |
| **The math** | For the "what the math is" column: Parts II–III, and one read-only probe on the same saves. It read the per-court pair scores, the feasibility card's draft and its acceptance components, a plain white peace's acceptance, and the send verdict. |

## 28. The short answer

**No.** No peace screen says why the peace is not made, or what the player can do about it.
The numbers on the screens are right: PC-F3's peace table is on the HUD tooltip and the war
popup, the paradox names Bavaria and both ways out, and the armistice letter states the
truce's cost honestly. But:

1. **The averaging is never shown.** The war card says +77. The table says 17, and "the
   field stands at 26". No screen says that these are the mean of three courts' scores
   (Austria +79, Britain −2, Russia 0). That one fact is why a crushed Austria reads 11/50.
2. **The screens blame the wrong court.** The table says "Austria will not sign … until that
   court is eased toward terms"; Talleyrand says "I'd ease Austria, Britain, Russia". The
   lever that works is the opposite one: drop the two courts France has not fought, and
   Austria signs a white peace at 50/50.
3. **The roads that work are hidden; the roads offered are traps or dead ends.** On the
   user's board two roads end the Austrian war today: Austria alone through the table (a
   white peace that also ends Bavaria's war), or gold.
   - The wizard recommends neither. It recommends the armistice, which strikes France's
     score. The war card read +52 the turn before; it is hidden while Austria's letter
     waits (F48), and comes back at −3 the moment the truce is signed.
   - The one peace Talleyrand offers ("Propose these terms") is refused by the paradox, and
     the refusal is drawn nowhere: the click does nothing.
4. **Talleyrand's words contradict the buttons beside them.**
   - "Press Austria alone: the separate peace. It costs 3 diplomatic points" stands beside a
     disabled "Make peace with Austria only".
   - "The others — Britain and Russia — can each be treated with alone" stands beside a
     disabled "Separate peace with Britain".
   - "Every covered court has been beaten in the field" is said of two courts France has
     never met.
5. **The truce's cost is below the fold.** The letter's honest paragraph sits 640 px under a
   box that shows "Assessment: GENEROUS" and the gold, with Accept one click away.

What a player concludes from the screens alone: *Austria is the obstacle; it wants more than
France can give; the armistice is the sensible step.* What the math says: *Austria is ready;
Britain and Russia hold the table because they average in at 0; the armistice is the one step
that makes it worse.*

## 29. Moment by moment

Frames are named in brackets (`docs/audits/peace_client/<name>_5120x1440.jpg` and
`_1920x1080.jpg`). The words are the same at both sizes; §31 gives the differences.

**M1 — The war card and its tooltip** (`m1_war_card_tooltip`; Vienna held)

| | |
|---|---|
| **The screen** | "Britain + Austria + Russia **+77**". Tooltip: "Settlement: White Peace / The peace table reads the war at 17 — White Peace. A settlement carries only when every court reaches 50 — with no terms: Austria 11/50 · Britain 18/50 · Russia 18/50. / This turn's battles and captures count from next turn: the table reads 17 until the turn ends; the field stands at 26." |
| **The player concludes** | France is winning big (+77), yet the peace is a White Peace, and Austria — the beaten court — is the lowest of all. Three numbers for one war, and nothing on the screen relates them. |
| **The math** | +77 is France's pairs summed: Austria +79 live, Britain −2, Russia 0. 26 is their mean, live; 17 is the mean of the stored scores (+54, −2, 0). The tier reads the mean, and every court's base is 0.65 × that mean (F4). Austria is lowest because its own row also charges −15 for Vienna kept. |
| **The gap** | The mean is never named, and the per-court scores are never shown (**F37**). The lag note is right and readable. |

**M2 — The war-detail popup** (`m2_war_detail`)

| | |
|---|---|
| **The screen** | "WAR WITH BRITAIN + AUSTRIA + RUSSIA +77" under Britain's flag. A Score Breakdown (Territory +15, Battles +15, Decisive +10, Capital +20, Campaign +6, Blood +15, Blockade −2, Ticking −2), then the peace table's lines and "Enemy War Exhaustion: Unknown". Buttons: **Negotiate Peace** ("Open bilateral peace options for this court only"), **Open Settlement**, and **Request Terms**, disabled with "… exhaustion 45 of 80 …". |
| **The player concludes** | The breakdown is the war's. Negotiate Peace talks to "this court", and the court France is winning against is Austria. |
| **The math** | The breakdown is France–Austria's pair plus Britain's blockade. Negotiate Peace opens **Britain's** page: the coalition's leader, which carried 1 % of its effort. |
| **The gap** | No per-court breakdown (**F37**). The button does not say whom it addresses (**F41**). Exhaustion reads "Unknown" in the same popup whose button states it (**F42**). At 1080p the popup's text column is 352 px wide: the peace table's first sentence sits at the fold and the lag note is below it (§31). |

**M3 — The diplomacy wizard, Austria's page** (`m3_wizard_austria`)

| | |
|---|---|
| **The screen** | Talleyrand: "Austria falters, Your Excellency. Our armies press the advantage — we may dictate the terms, though a court not yet broken will be slow to sign them." "Recommendation: Talleyrand recommends: Propose Armistice." Rows: **Propose Armistice (1 DP) — Favorable**, **Open Settlement**, **Propose White Peace**, and **Propose Peace (3 DP)**, disabled with "Bavaria is still at war with Austria — propose an armistice, or first Downgrade the alliance with Bavaria (2 steps) below a defensive alliance". |
| **The player concludes** | Peace is barred by Bavaria. The armistice is the recommended and favorable road. "Propose White Peace", which is enabled, must be a white peace with Austria that somehow escapes the bar. |
| **The math** | PC-F1's words are exact. But the armistice strikes the score (§14, F17). "Propose White Peace" stages the whole-war table, which cannot carry at 17. The road that carries, Open Settlement with Austria alone, is not named. |
| **The gap** | The paradox is legible; the alternatives are not. Propose White Peace on Austria's page does not say it addresses all three courts (**F41**). The recommendation is the trap (**F43**). |

**M4 — Propose White Peace: the whole-war confirm** (`m4_white_peace_confirm`)

| | |
|---|---|
| **The screen** | "This settlement cannot be ratified now … Holding out: Austria 11/50, Britain 18/50, Russia 18/50."<br>• Austria — "Blocker: Leader's own losses" ("their crown is asked to sign away too much of its own").<br>• Britain and Russia — "Blocker: Settlement legitimacy" ("it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents").<br>• Talleyrand: "… London and Vilna are unbeaten … Press Austria alone: the separate peace. It costs 3 diplomatic points; you have 7."<br>• "What the treaty titles: Status quo: Bohemia, Tyrol and Vienna stay ours by the treaty", over "White Peace — no terms will be exchanged."<br>• Buttons: **Make peace with Austria only** (disabled — the paradox), **Armistice with Austria only**, **Open War Detail**, **Back Out**. |
| **The player concludes** | Britain and Russia refuse because the others refuse. Talleyrand says to press Austria alone, and the button for it is dead. |
| **The math** | The blocker the screen calls "legitimacy" is the white-peace tier's −10, on a base diluted by Britain's and Russia's own zeros. Austria's −15 is Vienna, which France keeps. |
| **The gap** | The advice is refused by its own popup (**F35**). The legitimacy sentence is circular (**F37**). "White Peace — no terms" sits over "Vienna stays ours" (PC-F33, confirmed on screen). |

**M5 — Talleyrand's counsel, and "What terms would they accept?"** (`m5_counsel`, `m5_counsel_make_peace`, `m5_counsel_paths`, `m5_feasibility`, `m5_feasibility_after_send`)

| | |
|---|---|
| **The screen** | **"Talleyrand, what about Austria"** gives: "I am confident in this assessment, Sire … War score stands at 79 from our perspective. In the field we outmatch them decisively. Metternich is calculating — skill 9." Options: [What terms would they accept?] [Thank you]. No recommendation, no paradox note.<br><br>**"…how do we make peace with Austria"** reaches the counsel that carries PC-F1's note: "I recommend pressing for peace on favorable terms … Mark one thing, Sire: Bavaria is still at war with Austria … Two ways out — propose an armistice, or first Downgrade …". Its [What should we do?] offers **Generous peace** and **Firmer terms**, both disabled, and **Continue fighting** ("We can extract more concessions on the battlefield"). The refusal (452 characters) lives only in the disabled buttons' tooltip: "… Propose an armistice instead — the court reads it Favorable (65) … Or settle the war jointly at the settlement table." It is drawn as one unwrapped line that runs off a 1920×1080 window at "…the alliance with Bavar".<br><br>**The card**: "the terms I would draft: Peace Treaty; Austria pays 130 gold/turn for as long as the treaty stands; Offer: Prisoner return … My assessment yields 45 — they might counter-offer. The sticking point appears to be deep-seated hostility. We would need 2 diplomatic steps to reach PEACE. The proposal itself would cost 2 DP." [Propose these terms] [Dismiss].<br><br>**Propose these terms** changes nothing on screen. The terminal prints "Directing Talleyrand: execute proposal". The backend's answer ("Bavaria is still at war with Austria: a separate peace would break her war. Two ways out …") is drawn nowhere. |
| **The player concludes** | A war score of 79 and yet only 45: the problem is hatred. Peace takes two steps, so an armistice first. The button is broken. Fighting on will extract more. |
| **The math** | 79 is the live pair: a fourth number for the war. The draft scores 45 because of its own gold demand: the war-age penalty on a demand in a six-turn war is −24, the largest term; relations are −10, the second (clamped at war). A plain white peace scores **75** on this board today, and 106 once the turn's victories count (§11). The paradox refuses both. A peace is signed straight from war, one step, and the send costs 3. Another victory adds 0 (§11). The joint table cannot carry a white peace (17); Austria alone can. |
| **The gap** | Part II's F10 is live as filed. The silent refusal is new (**F34**). The card names the second obstacle, miscounts the road, shows no estimate line and never says that a white peace would be accepted (**F40**). The counsel's "settle jointly" names the table road that fails, not the one that carries (**F43**). The unwrapped tooltip is **F47**. |

**M6 — Open Settlement** (`m6_table_white`, `m6_table_gold_carries`, `m6_table_britain_gold_removed`, `m6_table_austria_alone`)

| | |
|---|---|
| **(a) A white peace** | "Will NOT carry … Austria will not sign; the settlement … cannot be ratified until that court is eased toward terms or dropped to fight on." Talleyrand: "I'd ease Austria, Britain, Russia." Each court has Demand more / Ease / Drop. |
| **(b) More generous, four clicks** | Each click pays **every** court 100 gold. The table goes 11 / 18 / 18 → 23 / 30 / 30 → 35 / 42 / 42 → 47 / 54 / 54 → **59 / 66 / 66, "This peace carries"**: 1,200 gold of 4,688. |
| **(c) Britain's 400 removed** | Austria falls 59 → 43 ("Austria Will sign → Holding out (close)"), and Britain "Will sign (50/50) **White peace**". Talleyrand: "Every covered court has been beaten in the field … Press Austria alone … The others — Britain and Russia — can each be treated with alone, at 3 points apiece." Beside it, "Separate peace with Britain" is disabled ("Spain is still at war with Britain …"). |
| **(d) Britain and Russia dropped** | "France vs Austria — **Separate settlement** … Will carry as drafted … Austria Will sign (50/50) White peace … This peace carries." Beside it: **Separate peace with Austria**, disabled with "Bavaria is still at war with Austria — a separate peace would break her war …", and "Allies and Standing: Bavaria — Consulted ally". Submit, then **Ratify White Peace**: "Austria has signed a separate peace and left Third Coalition"; "Settlement Ratified: France vs Austria (3 pairs resolved)". The ledger: France–Austria, **Bavaria–Austria** and Kingdom of Italy–Austria at peace, turn 6. |
| **The player concludes** | (a) Austria is the problem. (b) Peace costs 1,200, 400 a court. (c) Austria's price somehow depends on Britain's gold: visible, inexplicable. (d) A separate settlement carries, but it "would break Bavaria's war". |
| **The math** | One payment lifts every court (F23): about 975 gold to any single court carries, and the dial pays all three. Ratifying (d) ended Bavaria's war in the same instrument: the table road already does what ruling C asks of the bilateral road. |
| **The gap** | The wrong court is blamed (**F37**). The counsel is refused by its own buttons (**F35**) and calls unfought courts beaten (**F36**). The separate settlement ends the ally's war and the screen says the opposite (**F43**). F23 can be seen working, but nothing explains it; the dial spends about 225 gold more than one payment would. |

**M7 — Austria's armistice letter** (`m7_armistice_letter`, `m7_armistice_letter_scrolled`; the turn-6 copy, one end turn)

| | |
|---|---|
| **Above the fold** (327 of 966 px, at both sizes) | "DIPLOMATIC ENVOY / Metternich (Schemer) of Austria / Proposes: Armistice / France demands: Austria pays 168 gold per turn to France for as long as the treaty stands / Mutual: Armistice / Assessment: **GENEROUS** / War score: 52 ^ (Territory +10, Battle +15, Decisive Battle +10, Ticking −4)" — and **Accept** · Let Talleyrand haggle (1 DP) · Reject · Not Now. |
| **Below the fold** | "Settlement: Dictated Terms" …<br>"A 5-turn ceasefire: fighting stops, and the battles fought so far are struck from the war score — if the war resumes, it resumes from nothing … When it expires: peace if relations have healed to −60 or better — otherwise the war resumes. Relations stand at −80 and will thaw to −65 by expiry — short of −60; the war resumes when the truce expires unless relations improve by other means, or a second truce follows."<br>"Bavaria stays at war with Austria … Our clients follow us out of the truce: Kingdom of Italy." |
| **The turn's envoy list** | "ENVOYS AWAITING RESPONSE … Austria — **Armistice Losing**". |
| **The HUD** | The war card is not on screen on this turn. The turn opened with a standing-order report (Napoleon's pursuit ended), and that path never refreshes the war HUD. The card comes back only with the truce's reply, at −3. |
| **The player concludes** | From what shows without scrolling: a generous truce that pays France 168 a turn, at a war score of 52. Accept. ("Armistice Losing": whose loss?) |
| **The math** | Below the fold the letter is honest and complete about F7 and F17. The breakdown "52 (…)" leaves out Campaign +6 and Blood +15, so it adds up to 31. "Dictated Terms" is the pair's own tier; the table reads White Peace. |
| **The gap** | The cost is below the fold (**F46**). The breakdown does not add up (**F39**). The tier is the pair's (**F38**). "Armistice Losing" is a raw key (**F45**). The war card, which would show the score the truce strikes, is hidden (**F48**). Not stated anywhere: that a court in a truce leaves the next coalition settlement (F32). |

**M8 — After accepting** (`m8_truce_card`, `m8_armistice_popup`, `m8_wizard_under_truce`, `m8_truce_next_morning`, `m8_armistice_popup_turn8`, `m8_table_under_truce`)

| | |
|---|---|
| **The screen** | The war card reads "Britain + Russia **−3**" (it was +52).<br>The truce row "Austria 5t": "Armistice with Austria — 5 turns left, on course to collapse back to war unless relations heal." The rail: "Austria and France have signed an Armistice."<br>The armistice popup: "Relations: −80 (Hostile) · Trend: = · On course to collapse: unless relations heal to −60 or better, the war resumes at expiry."<br>Austria's wizard page: "No proposal would find purchase now. Talleyrand recommends: Improve Relations mission …", with the rows **Improve Relations (1 DP) — +8 relation/turn** and, below the fold, **Propose Peace (2 DP)** disabled ("… let the truce run its course (it becomes the peace if relations stand at −60 or better) …").<br>Next morning: "A truce with Austria: the fighting stops for 5 turns — peace if relations heal to −60 or better, else the war resumes"; "War Purpose: … vs Austria … Settlement: White Peace (+0)"; "Carniola passes from Austria to Bavaria"; Berthier: "A truce is a clock, Sire, not a treaty. Use its turns — the war is paused, not over." Relations −77, trend up.<br>France's own table: "Vienna, London and Vilna are unbeaten … (Austria 12/50, Britain 9/50, Russia 9/50)". |
| **The player concludes** | The truce cost the war score (now plain: −3) and leads back to war unless relations heal. Talleyrand says to improve them. |
| **The math** | Relations thaw −80 → −65 by expiry. One turn of Improve Relations (+8) puts them at about −57, so the truce ends in peace: by the screens' own numbers, one action point of diplomacy. The truce struck Austria's score to 0, so the table now calls Austria — whose army and capital France beat — "unbeaten". |
| **The gap** | The −60 rule is on five surfaces, and the cure is two rows away on the same wizard page; no surface joins them (**F44**). "Unbeaten" reads the struck score. That is F17's effect in words, and it rides ruling D. |

## 30. What the screens hide

1. **Austria alone, through the table.**
   - On the user's board, dropping Britain and Russia from France's own settlement makes a
     white peace with Austria that carries at 50/50 and ratifies.
   - It ended Bavaria's and the Kingdom of Italy's wars with Austria in the same instrument
     ("3 pairs resolved"). That is the Pressburg behaviour ruling C asks for, already built,
     on the settlement road.
   - Nothing points to it. The wizard recommends the armistice; the counsel says "settle
     jointly"; the table blames Austria; and the disabled "Separate peace with Austria" says
     the opposite of what the table then does.
   - This is Part III's F24 (a fifth road with a fifth verdict). The screen half is **F43**.
2. **Gold, paid once.**
   - The dial buys the carry for 1,200 by paying every court; about 975 to any one court
     would do.
   - The table shows the coupling — remove Britain's gold and Austria falls — and never
     says it. This is F23's legibility half, and it rides ruling E.
3. **The truce's cure.** One turn of Improve Relations inside the truce turns it into peace
   at expiry (**F44**). The game prices the mission (+8 a turn) and the gap (−65 against
   −60), and leaves the sum to the player.

## 31. 1920×1080 against 5120×1440

- **The fixed-size popups are the same logical size at both resolutions.** The envoy
  letter's box is 650×327, so the same 640 px of 966 is hidden. At 5120×1440 (logical
  3657×1028 at 140 %) that box is a third of the screen's height, and there is room for the
  whole letter.
- **The war-detail popup's text column is 568 px at 5120 and 352 px at 1080p.** At 1080p
  the peace table's first sentence sits at the fold, its lag note is below it, and the three
  buttons wrap onto two rows.
- **Tooltips at both sizes** are drawn on Godot's default translucent tooltip panel (the
  theme styles no TooltipPanel), so the map's place names show through the HUD's peace
  table. At 1080p "Kingdom of Italy", "Papal States" and "Sardinia" sit under its first
  lines. A tooltip is one unwrapped line: the 452-character refusal under Generous peace fits
  5120's width with nothing to spare and runs off a 1920 window.
- **The settlement table and the wizard read the same at both sizes.** The table's
  Talleyrand paragraph (the "Press Austria alone" one) is in a scroll pane with its top lines
  showing; "What the treaty titles" (the *uti possidetis* line) is below the fold at both.
- **Not a peace matter:** a 1920×1080 window on this monitor boots at 140 % (logical
  1371×771), because the menu reads the physical screen. It is noted because it governs any
  1080p capture made on this machine; this study set 100 % by hand.

## 32. New findings

| # | Kind | Finding | Evidence |
|---|---|---|---|
| **F34** | D | **A refused send from the feasibility card is silent.** The backend refuses "Propose these terms" in PC-F1's words, and the client re-mounts the unchanged card. `proposal_confirm_popup._build_feasibility_content` never renders `transient_error_display`: DDB-9 gave that line to `_build_content` and PF-1 to the settlement builder. The sibling sweep: **12 of the 14 dtype builders** drop a refusal (mission, advisory, war purpose, war confirm, conflict alert, ultimatum, scope-replace, pair-substitute, incoming settlement offer, ally petition, peace preview, feasibility). | M5; `proposal_confirm_popup.gd` 160, 405, 505, 1791; `main.gd` 3842–3857 |
| **F35** | D | **The table's counsel recommends separate peaces the table refuses.** `settlement_staging.legitimacy_sentence` says "Press Austria alone: the separate peace. It costs 3 diplomatic points", and "The others — Britain and Russia — can each be treated with alone". The same popup's "Make peace with Austria only" / "Separate peace with Austria" / "Separate peace with Britain" are closed by the paradox: the sentence is not stamped by `can_sign(at_send)`. This is the class of PC-F1, F10 and X1. | M4, M6c; `settlement_staging.py` 2422–2487 |
| **F36** | D | **"Every covered court has been beaten in the field" is said of courts France never fought.** The same function counts "unbeaten" among the holdouts only. When Austria is the sole holdout, Britain (−2) and Russia (0), both signing because they are paid, become "beaten". | M6c; `settlement_staging.py` 2438–2461 |
| **F37** | L | **The peace screens never show the averaging, and they blame the wrong court.** The card's +77, the field's 26 and the table's 17 are never related, and no screen shows a court's own score. The table names the lowest court as the obstacle ("Austria will not sign … until that court is eased"), and its legitimacy blocker is circular ("… needs every covered court's consent, and not every court consents"). Dropping the two unfought courts carries. | M1, M2, M4, M6a |
| **F38** | I | **Two surfaces still print each pair's own tier.** The morning dispatch says "Settlement: Dictated Terms (+54)" against Austria, and the envoy's War Summary says "Settlement: Dictated Terms". The table reads White Peace. PC-F3's sibling, missed by S13d's sweep. | M7; `dispatch.py` 6594–6602; `incoming_proposal_popup.gd` 311–319 |
| **F39** | L | **The envoy's War Summary breakdown does not add up to its score.** The client lists only territory, battle, decisive, capital and ticking, and drops Campaign, Blood, Blockade and Captive: "52 (Territory +10, Battle +15, Decisive Battle +10, Ticking −4)". | M7; `incoming_proposal_popup.gd` 298–305 |
| **F40** | L | **The feasibility card names the wrong obstacle and miscounts the road.** On a counter-offer it names the *second* negative ("deep-seated hostility", −10) and not the largest (its own gold demand's war-age penalty, −24). It says "2 diplomatic steps to reach PEACE" for a peace signed straight from war (`_UPGRADE_ORDER` index distance). It renders no estimate line (the payload carries no `acceptance_estimate`). It never says that a white peace would be accepted (75 on the same board). | M5; `diplomacy.py` 8561–8569; `diplomatic_dialogue.py` 2008–2054 |
| **F41** | L | **The peace buttons do not say whom they address.** The war popup's "Negotiate Peace" ("for this court only") opens Britain, the leader. "Propose White Peace" on Austria's page stages the whole-war table with Britain and Russia, and the terminal echoes it as "propose white peace with Austria". | M2, M3, M4 |
| **F42** | I | **War exhaustion is "Unknown" beside a button that states it.** The war row fog-gates the opponent's exhaustion on its visibility (`war_status.py` 352–359), and the same popup's Request Terms tooltip says "exhaustion 45 of 80". Diplomacy carries no fog (the standing rule). | M2 |
| **F43** | L | **The separate settlement ends the ally's war, and the screens say the opposite.** Ratifying the Austria-only table signed France–, Bavaria– and Italy–Austria peace ("3 pairs resolved"). The same popup lists Bavaria as "Consulted ally", and its "Separate peace with Austria" says the separate peace "would break her war". The wizard recommends the armistice, and the counsel's way out is "settle the war jointly", the table road that cannot carry. | M3, M5, M6d |
| **F44** | L | **The truce's cure is never priced.** Five surfaces state the −60 rule, and the letter projects −65. The wizard sells Improve Relations at +8 a turn two rows away. No surface says that one turn of it makes this truce a peace. | M7, M8 |
| **F45** | L | **A raw proposal key in the envoy list.** "Austria — Armistice Losing", "Client Petition", "Open Borders" come from `str(proposal_type).capitalize()` in the dispatch view and the terminal (`dispatch_view.gd` 386, `main.gd` 5263). It is an R7 leak, and it reads as France losing. | M7 |
| **F46** | L (layout) | **The armistice letter's cost sits below the fold, under Accept.** The envoy popup shows 327 of 966 px at both 1920×1080 and 5120×1440. "GENEROUS" and the gold are on screen; the struck score, the −60 rule and its projection are 640 px down. On the 1080p war popup the peace table sits at the fold. | M7, §31 |
| **F47** | L (layout) | **Hover text is on the default tooltip panel.** It is translucent over the map, and a tooltip is one unwrapped line: the 452-character refusal under Generous peace runs off a 1920 window. The HUD tooltip is the only place PC-F3's peace table reaches the HUD. | M1, M5, §31; `ui/main_theme.tres` (no TooltipPanel) |
| **F48** | D | **The HUD war card vanishes on a turn that opens with a standing-order report.** The enemy phase hides the war panel (it is modal). `_on_enemy_phase_dismissed` re-shows it through `_process_active_wars`, but returns before that call when the response carries `strategic_reports`, and `_on_strategic_report_dismissed` never makes it. The panel stays hidden until the next backend reply, against N4i's own rule ("ALWAYS refreshes panel visibility"). The two `redemption_event` branches return the same way. Seen on turn 7 in three runs (Napoleon's pursuit ended), with Austria's letter waiting; on turn 8, with no report, the card was back. | M7; `main.gd` 6296–6346, 6944–6987, 8677 |

## 33. What this means for the rulings

- **C (the Pressburg road)** gets the strongest evidence yet: it is already built, on the
  settlement road. Ratifying the Austria-only table brings Bavaria to the table and ends the
  war the bilateral road says it would break. Ruling C can be one verdict, read by the
  bilateral road from the settlement road's carry-in. Until it is ruled, **F43** is the only
  way a player finds it.
- **D (the victor's truce).** The letter is honest; its trap is layout (F46) and an unpriced
  cure (F44). If D stays deferred, as Part III recommends, those two rows make today's truce
  legible.
- **E with F23.** The table's "More generous" dial is where F23 costs the player real gold,
  and where it reads as nonsense (one court's gold moves another court's answer). Ruling E
  with F23 ("a payment counts for the court it is paid to") would make the dial's per-court
  look true.
- **Order for S13e.** F48 and F34 first: the two client defects, one a hidden HUD and one a
  silent refusal, both at the peace moment. F34 goes with F10 (same card). F35, F36 and F43 with the paradox class. F37,
  F38, F39, F41 and F42 (one per surface). F40, F44, F45. F46 and F47 go to UXR-4 at S15's
  head with the re-homed marks.

## 34. Evidence for Part IV

| Claim | Source |
|---|---|
| Every quoted line, button and tooltip | the client's own state records, kept beside the frames in `docs/audits/peace_client/moments.json` (lines and controls per frame) |
| The fold measurements, the popup sizes, the tooltip widths | the state records' rects and scroll extents at both sizes |
| +77 / 26 / 17 decomposed; the card's 45 and its components; a white peace at 75; the send verdict | the read-only probe on the two saves (`calculate_war_score`, `get_war_score_for`, `generate_feasibility_dialogue`, `calculate_acceptance`, `treaty.can_sign(at_send=True)`) |
| The Austria-only ratification ended Bavaria's war | `GET /diplomatic_ledger` on the sandbox after the ratification (France–, Bavaria–, Kingdom of Italy–Austria peace, turn 6) and the rail's "3 pairs resolved" |
| The silent refusal's cause | `proposal_confirm_popup.gd` (the builders that render `transient_error_display`: `_build_content`, `_build_settlement_content`) |

The run scripts and states are scratch, not committed; the frames and their index are. To
re-derive, copy `tools/dd_b_client.gd` with two edits:
- read the window size from an environment variable;
- add a `hover <words>` action: notify the root viewport that the pointer entered
  (`Node.NOTIFICATION_VP_MOUSE_ENTER`), push a mouse motion to the control's centre, and wait
  1.6 s of real time.

Then run `tools/dd_b_play.py start --road diplomacy --out <run> --port 8017` with that client
and the save copied into `<run>/saves`. Click Continue, and `act` the moments in §29's order.

---

# Part V — History as the test, the rulings designed, and what the player should see (October 16, 2026)

Parts I–IV measured the game. Part V asks three harder questions: could the game sign the
peaces the period actually signed; what should each ruling B–H be, as a design with costs;
and what should the player read at each peace moment. It also re-reads the earlier parts'
own assumptions, on the user's instruction ("don't be afraid to re-engage with its
assumptions"), and says where they do not hold. Run on master at `ae9ba8df`. Nothing here
changed the game.

## 35. What was done

| Instrument | What it is |
|---|---|
| **Five histories, fact-checked** | One researcher per peace (Pressburg, Tilsit, Schönbrunn, Lunéville/Amiens, 1813–14) with treaty texts and the standard literature; an independent checker per peace corrected 9–13 facts each (dates, signatories, article numbers). Corrections are applied below. |
| **Five comparable games, fact-checked** | EU4, CK3, HOI4, Victoria 3, Total War — wikis, defines, patch notes, dev diaries, player threads; a checker per game. Version drift is named where it matters. |
| **Six read-only code readings** | The table and its ratifier; the scorer; the AI's offers; the truce, relations and the war score; clients, the Congress, the Continental System and the call to arms; the client's surfaces (`.gd` by line). Each named the seam a ruling would touch and corrected Parts I–IV where they were wrong. |
| **Three challenges** | A diplomatic historian, a strategy-game designer and a systems engineer each attacked the earlier parts' premises; 36 assumptions were tested. |
| **Eight measurements (M1–M8)** | Mode A drives and read-only probes on copies of the user's two turn-6 boards, the suite's fixtures and fresh seeds: the Pressburg replay (M1), Tilsit (M2), Schönbrunn (M3), Amiens and Lunéville (M4), France losing badly (M5), the two-front coalition (M6), peace after the Congress (M7), clients and the Continental System (M8). About 33 driven campaigns (32 usable) and 2,000 scored packages. |

Every number below is per board or per seed, never a law. Scratch (the digests, the probes'
JSON, the scripts) lives in the session scratchpad under `pv/`; the re-derivation recipes are
in §45.

## 36. The assumptions of Parts I–IV, re-read

| # | The earlier part assumed | Verdict | What the evidence says | Consequence |
|---|---|---|---|---|
| 1 | "Bavaria was a party to Pressburg; it received Tyrol" (§2 F1); ruling C carries allies in as **co-signatories** | **Does not hold** | Pressburg was signed by two parties: Talleyrand; Liechtenstein and Gyulai. Article 6 *declares the treaty common* to Bavaria, Württemberg, Baden and the Batavian Republic; their gains are France's own articles (7, 8, 13–15). Napoleon had already signed separate reward treaties with each at Brünn (10–12 Dec) and Pressburg obliged Austria to confirm them. Tilsit: two instruments two days apart, Prussia dictated to after Russia signed; Schönbrunn: one plenipotentiary per side, allies "comprehended" by Art. II, cessions to France and redistributed later for a price (Bavaria paid 15 million francs at Paris, 28 Feb 1810, for the whole transfer — Salzburg, the Innviertel, Bayreuth, Regensburg — and ceded South Tyrol and Swabian districts besides). | C is **the leader stipulating for its allies**, not a second signature. The game already has the noun (`beneficiary_only`, `settlement_presentation.py:82`) and the SIDE rule (`settlement_ratify.py:190`). What it lacks is an authored beneficiary (F53), a consent read, and the words. |
| 2 | The alliance paradox forbids what history allowed (§2 F1, F8) | **Partly holds** | No **senior** partner was ever stopped: Napoleon stipulated for Bavaria (Brünn, then Pressburg Art. 6); Alexander negotiated Prussia's fate inside his own treaty, and Prussia signed a separate, harsher one; Francis signed for the Reich at Lunéville. The code stops the leader (`diplomacy.py:5550`) and lets the junior (incoming = WARNING `:5514`; joined-at-call = WARNING `:5524`). The HARD_STOP's lineage: `COALITION_SPEC.md` §6a made the separate peace the **primary** coalition-breaking verb with a loyalty penalty; `BILATERAL_PEACE_HARDENING_SPEC.md` §10.1 later borrowed the `commitment_paradox` (a war that puts France on both sides of an alliance) and applied it to peace-making. The table road never adopted it. | B is decided by precedent: the code has ruled "allowed, priced" four times. The one outlier is `:5550`. Name the owning spec (§10.5 vs FA-D17) before S13e fixes a sixth surface. |
| 3 | The settlement scorer is "an equal-weight average of three courts" (§0, §2 F4, §22) | **Partly holds** | It is a **power-tier-weighted** mean: major 3 / secondary 2 / minor 1 (`settlement_scoring.py:67-71`, `:418`, `:435-437`), written to stop France farming pressure by dragging minors in (`WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md:218`). Equal only because Britain, Austria and Russia are all majors. The direct score per court is the **max over France's side** (`:302-323`), so Bavaria's pair against Austria is eligible. | Ruling E **replaces** a weight the report never named. Its material-share form (Austria 0.99) has its own farm: France makes the whole war's peace by beating whichever court fought hardest. |
| 4 | "The coalition's peace is scheduled, not willed" (F21) is a defect | **Partly holds** | Amiens was exactly that: Britain, never beaten on land, signed from exhaustion, cost, the fall of Pitt and the loss of its last continental ally — on near-status-quo terms — the London preliminaries 234 days **after** Lunéville, Amiens itself 409. The game's fault is the **order** (the leader's letter can arrive before the continental member has left or been beaten; measured on the user's board it then **pays France** — Britain dunned 2,819 gold for Austria's defeat, M4) and the **content** (a bare peace). The letter is also self-consented: `_letter_would_carry` passes `consenting_courts = covered` (`ai_diplomacy.py:4620`); re-scored as France's draft the same package reads −24 / −32 / −32 (M4). | Re-file F21 as mis-ordered and self-consented, not scheduled. The clock is defensible; the letter should follow the continental collapse and be scored as the player's would be. |
| 5 | The "white peace" is *uti possidetis* mislabelled (F33) | **Holds, and more** | Napoleonic peaces transferred territory with **exchanges and compensation** (Salzburg to Austria at Pressburg; Talleyrand's Strasbourg plan to compensate Austria at Ottoman expense in south-east Europe — the standard account). "Each keeps what it holds" with no exchange is neither the eighteenth-century restitution peace nor a Napoleonic one. The package vocabulary has no exchange or third-party compensation clause, and the guided offer rows exclude capitals (F54) though returning Vienna is the single largest lever on the board (50 → 100, M1). | A compensation clause is a new design question (ruling J below). Without it ruling C can write only the harsh Pressburg. |
| 6 | The truce turns on relations, not victory (F7, F17, F18); ruling D converts it at loser ≤ −50 | **Partly holds; D was untested** | Every armistice of the era **froze the field in the victor's favour, levied on the held soil, took sureties and fixed a line** — a timetable only at Austerlitz, open-ended at Znaim, one month's notice at Tilsit (Austerlitz: Russians out of Moravia and Hungary within 15 days, Pressburg 20 days later; Tilsit: the Niemen thalweg, treaties in 16 days; Znaim: Graz and Brünn handed over as sureties, contributions levied for 94 days). The game's truce **wipes** the pair's stored score, battles and decisives (`cleanup_war_end`, `diplomacy.py:5755-5758`), pops `war_start_turns` so the war is **new** on collapse (`:2942-2945`; the −65 war-age penalty returns, M3), and ends on relations alone (`:11284`). Part III's D "never fired" because (a) the scripted France stops attacking at turn 13 and (b) the stored score the switch could read is 0 under every truce by construction; the live score keeps territory, capital, campaign and blood (32 of 51 on the probe board). | D is a design about **what a truce keeps**, before it is a rule about expiry. The historians' fork — a dictated peace on the held line when the loser's hope has died, a courted peace otherwise — is the shape (§40 D). |
| 7 | "Exhaustion is a clock, not a consequence" (F19); ruling H (b) replaces time with losses | **Partly holds** | A clock is half true: Austria's war finance ran out over years (paper money at 5:1 in 1811; the Pressburg indemnity made 1809 harder). What is unhistorical is that the tick is **uniform** (an untouched Russia wears at +8 like an invaded Austria), **reads no subsidy** (`_process_british_subsidy` runs beside the tick and the tick ignores it, `coalition.py:3222-3236`), **resets** at a truce for a single-front court (Russia 90 → 0 on a France–Russia truce, `diplomacy.py:5774-5787`) and at the peace, and **saturates** on the table (+20 from exhaustion 60, `settlement_scoring.py:553-554`): on every measured board the term is a constant from about turn 7. Part III's H arm removed the tick and never added the occupation term H (b) names. | H is "what the clock is made of": finance, occupation, subsidy received and paid, persisting across the peace; shown with a forecast turn (§40 H). |
| 8 | "Victories stop counting after five" is a gap (F15); G (b) raises the cap | **Does not hold as a defect** | The cap is PT-J2's deliberate anti-farm rule ("EU4 caps battles at 25 %", `diplomacy.py:3490-3499`). Two warts are real: the cap is applied **before** the quiet decay (`:3566-3567`), so a sixth win cannot refill what decayed; and no screen shows "Battles 15/15 — full; take ground". The larger truth is symmetric: the **loser's shield** — the `defense` ticking gives the side losing provinces +1 a turn per province to 25 (`:4510-4517`, `TICKING_CAP :3904`) — is why France's total victory is unreachable (Part II §9) **and** why the AI never reaches its harsh tiers against a losing France (Austria holding 13 French home provinces read +23, M5). | G: keep the caps, fix the order, show the fill; decide the shield (§40 G). |
| 9 | "Does it vary? No" (§13); ruling F rolls a seed | **Does not hold as stated** | Determinism is the design (`VISION.md` principle 3; GR6; the byte-pinned series). The five-seed instrument **could not** vary peace: the seed is consumed by the authored Tier-2 bands and a handful of in-campaign rolls (the intent and Congress jitters, design-ask patience, fortunes of war, captivity, jealousy, the naval rolls); no acceptance, war-score, threshold or scorer function reads it (`campaign_variance.py`; grep). The real finding hides in §11: six of ten levers move a court's answer by zero — a **reactivity** gap (AI_INTENT §2 principle 9), not a variance gap. | F stays the user's; measure reactivity, not seed spread. Rewrite §7's "no variance" as "no reactivity to six of ten levers". |
| 10 | "The player rarely gets to make a decision that matters" (§7, §28) | **Partly holds** | Two roads work today on the user's board and both are the player's act (Austria alone through the table; gold). What the screens withhold is the **stake**: only a signed peace titles soil toward the Congress's 45 (`game_end.py:110-117`), a truce that lapses into peace titles nothing (`:94-96`), and no peace surface shows the count. And the **after**: a harsh peace writes the punitive memory that forecloses the volte-face and promotes Revanche (`emergent_designs.py:5-24`, `:72`, `:519-526`); a confirmed cession **reconciles** the Revanche while the treaty holds (`agendas.py:305-320`) — Part I listed "the court keeps its Revanche" as a cost of C; it is the cost of the harsh draft. | Peace becomes a decision when the stake and the after are on the screen (§41), not by a new verb. |
| 11 | "Losing is cheap and quick … P8 never sent a letter" (§21) | **Does not hold** | §21's passive France **accepted** the first truce and left the war at turns 6–13; it was a France the AI mostly could not beat (24–28 provinces at turn 40 on four seeds; on ulm it fell to 13 by turn 30 after accepting four truces). A France that **refuses** every letter falls: Paris to Britain at turn 15 (ulm), the Emperor taken at turn 34, the Fall at 38; P8 fired 5–7 times per seed (M5). What it demanded was **one gold lump** — 349 to 1,818 gold, falling as France fell because both channels price to the payer's purse — and, multilaterally, at most the Duchy of Normandy. The AI **cannot dictate territory** bilaterally (`_build_proposal_terms`' harsh arm, `ai_diplomacy.py:990-1011`). | A new ruling I: what the AI may dictate (§40). The 1814 mirror is absent by construction, not by balance. |
| 12 | The commanded script is the baseline; the user's +73 is the exception (§6) | **Partly holds** | The script issues its last attack at turn 13 and then fortifies for 27 turns (`commanded_full40.json`); it peaks at +15…+38. D, G, E and F9 were read on a France that wins small and quits. The +73 is an **attractor** of the caps — battles, blood and campaign were all full by turn 6 — so any France that takes Vienna by then lands near +70. No fixture in the repo shows France ahead of Austria at all. | Every "per seed" result in Parts II–III about France's own peace describes a quitting France. A "skilled France" script is the first thing still unmeasured (§42). |
| 13 | "C is already built on the settlement road" (§33) | **Partly holds** | The table resolves every pair between a member of France's **side** of the instance and a covered court (`settlement_ratify.py:190`, `:215-220`); the paradox reads France's **ALLIANCE / DEFENSIVE_ALLIANCE** partners at war with the target anywhere (`diplomacy.py:5479-5488`). They coincide on this board (Bavaria is both) and diverge for a non-allied co-belligerent or an ally whose war lives in another instance. A carried ally **consents to nothing and reacts to nothing**: its contribution episode closes before the reactions run (`settlement_ratify.py:1555-1565` vs `:1660-1690`; measured, Bavaria 60 → 60, no reaction). The table's own "Separate peace with Austria" chip runs the bilateral paradox (`settlement_validation.py:530-545`). The bilateral hand-off re-routes an ally's cession to France silently (`settlement_staging.py:2548-2551`). | C needs one carry-in set, one consent read, an authored beneficiary and the words. The table is the right chassis; it is not yet the ruling. |
| 14 | The lever table: "one more victory 0; take the capital +15" (§11) | **Unverified** | `calculate_acceptance` reads the **stored** score (`diplomacy.py:8007`); a lever probe that adds a battle or a province and re-calls it without `recalculate_war_scores` reads every battlefield lever as 0 by construction. The 561 court-turn probe's saves were taken before the advance, so Talleyrand's acceptance column read last-advance scores throughout. The capital's +15 is not reproducible from the formula either way. | Re-run the lever probe with the recalculation and publish the script (§42). F15's "victories stop counting" rests on the cap (true) and on this probe (unverified). |
| 15 | "One payment buys every court" (F23) is a defect | **Contested** | The whole-side `accepting_set` is the spec's model of a common peace as one instrument the side signs (`settlement_scoring.py:1528-1535`; `SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` §2). The lie is the **dial**: "More generous" pays every court 100 (Part IV M6b), 225 gold more than one payment, and the screen shows the coupling without explaining it. The same whole-side set credits a returned province +35 to every court. | Keep F23 under ruling E as Part III did; the dial's words and the per-line gold cap (F62) are rows. |
| 16 | "Relations do nothing at war" is a gap (F18) | **Partly holds** | The ±10 clamp is R141, deliberate — it "prevents deep hatred from making wartime peace mathematically impossible" (the rationale at `diplomacy.py:124-127`; the clamp `:11530-11536`). The inconsistency is the truce's **raw** relation gate (`:11284`) from another era (R5a). Under a truce the relation term widens to ±30 (`:8019`), which is the −10 → −30 Part II §14 saw without naming. | D's design space is "what ends a truce"; do not un-clamp R141. F44 (price the cure) is the stop-gap. |
| 17 | "France has won the Austrian war on every measure" (§0) at turn 6 | **Holds, with the calendar** | Turn 6 is Early December 1805; Pressburg was signed 24 days after Austerlitz — turn 7 or 8 on the half-month calendar (`calendar.py:23`). An extractive peace at turn 6 would be faster than the fastest peace Napoleon dictated. The war-age penalty (−65 → 0 over 8 turns) refuses the **terms**, not the peace; the paradox refuses the peace. | Leave the war-age window alone; say it on the card (F40). |

**The questions the report never asked.** Should France ever *want* peace, and what does
refusing one cost (the Charges of Empire, the marshals' petitions, the next harsher letter —
Prague, Frankfurt, Châtillon)? Who is the senior partner — the leader stipulating for allies,
or a junior deserting? Can the loser be paid in a third party's land (Salzburg; the
Strasbourg plan; Austria's own authored Eastern Question)? What does the enemy *hope* for
under a truce, and can the player cut it (Znaim ran 94 days on Walcheren and Prussia)? What
does this peace do to the next war, and is the player shown it at signing? Does Britain's
gold buy its allies' endurance? What is a turn in days, and is the 8-turn war-age window
calibrated to Ulm → Pressburg (it is)? Should exhaustion survive the peace? Who speaks for
the enemy — can a defeat change the minister (Cobenzl → Stadion)? And: does the game have a
losing peace at all?

**The vision, in one paragraph.** At the Pressburg moment the player stands in Vienna at turn
7 or 8 and is handed two drafts, not one greyed button: Talleyrand's moderate peace, which
confirms the line and leaves the door to an alliance open, and the Emperor's dictated peace,
which gives Tyrol to Bavaria, takes the indemnity and writes the memory that swears Austria
to revanche. Both are France's to sign, because France is the senior partner and stipulates
for Bavaria in the same instrument; the only question the enemy answers is whether its court
will leave the coalition, judged by the same predicate its own AI uses. Britain and Russia
are not at that table because they have not been beaten; their letters come later on their
own clocks, and the war card says whose and why. At the Tilsit moment the truce does not
erase Friedland: the score freezes, the enemy's hope is a named line, and the player chooses
between letting the truce lapse into a dictated peace on the held line and spending its weeks
courting so the beaten court proposes the alliance itself. At the 1814 moment the roles
reverse on the same executor: a winning coalition sends France the natural frontiers, then
the 1792 frontiers, each refusal priced in the Charges and in a harsher next letter, so
"Continue fighting" is Châtillon with a cost on screen. The shapes are assured and the
casting varies: a beaten power is humiliated into revanche or courted into partnership, the
paymaster pays others' endurance and sues last, the leader writes its allies' peace, and a
status quo as held is called by its name.

## 37. History as the test

The dates are the fact-checked ones; where sources split, the split is named.

| Peace | Battle → armistice → treaty | Who signed | How allies were carried | What the victor took | Why the loser signed | Why not more |
|---|---|---|---|---|---|---|
| **Pressburg** (26 Dec 1805) | Austerlitz 2 Dec → interview 4 Dec → armistice signed 6 Dec (Berthier, Liechtenstein) → treaty 26 Dec: **24 days**, armistice to peace 20 | Talleyrand; Liechtenstein, Gyulai. Two parties. | Victor's allies: Brünn reward treaties 10–12 Dec (Bavaria, Württemberg, Baden), then Pressburg Art. 6 "declares the treaty common" to them and writes their gains (Arts. 7–8, 13–15). Loser's allies: Russia marched home under the armistice (out of Moravia and Hungary within 15 days), signed nothing; Britain fought on; Prussia bought at Schönbrunn 15 Dec and the unsigned Prussian text waved at Vienna. | Venetia, Istria, Dalmatia to the Kingdom of Italy; Tyrol, Vorarlberg and more to Bavaria; the Swabian lands to Württemberg and Baden; two kingdoms recognised; **40 million francs** in a lump plus a stream (8 at ratification, then 6, 6, 2 a month); no army cap; the integrity of what remained guaranteed (Art. 17). Austria compensated with Salzburg and Würzburg. | The army gone (Ulm, Austerlitz), the capital held since 13 Nov, requisitions running, the Russians gone, Prussia bought, Charles too far, the war party out (Cobenzl 24/25 Dec). | Prussia's Potsdam clock; the Russians beaten not destroyed; typhus; and he already had the client belt. He **refused** Talleyrand's moderate plan (compensate Austria in the Danubian principalities) — the choice that bred 1809. |
| **Tilsit** (7 and 9 Jul 1807) | Friedland 14 Jun → Russian armistice 21 Jun → Prussian truce 25 Jun → Russian treaty 7 Jul (16 days) → Prussian treaty 9 Jul: **25 days** | Talleyrand; Kurakin, Lobanov (Russia); Kalckreuth, Goltz (Prussia). Two separate instruments; a secret alliance beside the first. | The senior (Russia) negotiated the junior's fate inside its own treaty ("out of esteem for the Emperor of all the Russias", Art. IV) and took Białystok from it; Prussia signed a harsher instrument two days later. The armistice's Art. III shielded Prussia for 4–5 days while its own truce was arranged. France's allies (Saxony, Westphalia, Holland) were beneficiaries by article. Britain and Sweden fought on. **France sold its own allies**: Persia (Finckenstein, May 1807) and the Porte. | From Prussia: everything west of the Elbe, the Polish lands (Duchy of Warsaw), Danzig a free city, ports closed to Britain, half its people; indemnity left **blank** and fixed later (140 million, Sept 1808) with three fortresses held until paid and an army cap of **42,000** for ten years. From Russia: nothing in soil (Białystok gained), recognition, the Ionians, mediation, the Continental System on refusal. | Russia: Friedland, the fear of a Polish rising in its own partition, Britain's subsidy unpaid, the Turkish front. Prussia: no army, no soil, no sponsor but Alexander. | Russia was the instrument against Britain; a stripped Russia could not serve. Prussia was in hand. The indemnity was left open as a lever (occupation as collateral). |
| **Schönbrunn** (14 Oct 1809) | Wagram 5–6 Jul → Znaim 11–12 Jul → treaty 14 Oct: **100 days**, armistice to peace 94 | Champagny; Liechtenstein (who signed a "Project" beyond his instructions; Francis ratified because a peace announced by cannon could not be repudiated). One plenipotentiary per side. | France's allies comprehended by Art. II; cessions made **to France** and redistributed later for a price (Bavaria paid 15 million francs for the whole transfer, Paris 28 Feb 1810). Russia, France's sham ally, paid 400,000 Galician souls. Austria's only ally Britain was at Walcheren, unconsulted, and Austria was bound to break with it (Art. XVI). Sweden made its own peace in Jan 1810. The Tyrolese were abandoned by a written guarantee broken. | ~3.5 million souls: Salzburg and the Inn to Bavaria, Illyria to France, West Galicia to Warsaw, Tarnopol to Russia; **85 million francs** (of 200 "owed"); army capped at **150,000**; the Continental System; recognition. | Three months of **hope** — Walcheren, Knesebeck's Prussian offer, Russia's friendliness — each dying in turn; finance (paper at 15 % by 1810; default 1811); Napoleon's first demand had been the dynasty. | Russia bounded the terms over Poland; the army was fought to a standstill; occupation paid, so delay cost him little until September; he set his own yardstick ("a loss equal to Pressburg"). |
| **Lunéville / Amiens** (9 Feb 1801; 25 Mar 1802) | Hohenlinden 3 Dec 1800 → Steyr 25 Dec → Lunéville 9 Feb: **68 days**. Lunéville → London preliminaries 1 Oct 1801: **234 days** → Amiens: 409 days. | Lunéville: Joseph Bonaparte; Cobenzl, who signed **for the Empire** (Art. I) because the Diet could not be consulted. Amiens: France, **Spain and the Batavian Republic** as parties; Britain. | Four modes: the loser signs for its dependents (Francis for the Reich); the victor's co-belligerents co-sign and **pay in their own coin** (Trinidad, Ceylon); the victor's clients are guaranteed beneficiaries (Art. XI); the loser's other allies are left to their own instruments (Naples, Portugal, Russia, the Porte). The loser's ally bond was **priced and dated**: the £2 million subsidy forbade a separate peace before 1 Feb 1801 (per the Alessandria and Steyr accounts); Austria signed 8 days after. | Lunéville: the left bank of the Rhine, Belgium, the Adige line, Tuscany to Parma; **no indemnity**, no army cap. Amiens: Britain returned nearly every colony (kept Trinidad, Ceylon), Malta to the Order under thirteen stipulations, silence on Belgium, Holland, Switzerland and Italy. | Austria: the army "a rabble" after the pursuit, outposts 80 km from Vienna, Britain refusing a naval armistice and suspending the subsidy. Britain: no continental ally left, the Baltic, the fall of Pitt, the debt — and it believed the peace reversible (it never evacuated Malta). | Isolating Britain was worth more than a province; a quick peace consolidated the Consulate. Silence on the continent was taken as licence (Piedmont annexed 170 days later) and the peace broke in 14 months. |
| **1813–14** (Paris, 30 May 1814) | Pläswitz 4 Jun–10 Aug 1813 (armed mediation → Austria declares war) → Frankfurt bases 9 Nov → Châtillon 5 Feb–19 Mar 1814 → Chaumont dated 1 Mar, signed 8/9 Mar → Paris falls 31 Mar → abdication 6 Apr → convention 23 Apr → treaty 30 May | Four identical bilateral treaties (Britain, Austria, Russia, Prussia) plus accessions; Talleyrand for Louis XVIII. Napoleon signed **no peace** — he refused three and signed one armistice and one abdication. | Chaumont bound the Four to **no separate peace** for £5 million for 1814 (Art. III), 150,000 men each (Art. I), 20 years (Art. XVI) — written right after Austria had sounded a separate armistice. The minors were represented by the Four. France's allies were **bought by the enemy** before any peace (Ried, Fulda) or defected at Leipzig. | France to the 1792 frontiers plus additions; **no indemnity, no occupation, no army cap**, colonies mostly returned, the Louvre kept — the mildest terms France ever received, at maximum defeat, because the signatory had changed ("the paternal government of her kings"). The real transfers rode in secret articles among the Four. | Each refusal was a bet that the next battle would re-price the offer; the end came by legitimacy collapse (the Senate) and a subordinate's defection (Marmont), not by score. | The counterparty had changed; Britain's hard goods were taken in the secret and colonial articles; a punitive peace would have broken the Bourbons; Castlereagh wanted the alliance, not the indemnity. |

**What the record says a peace game must be able to do.**

1. **A coalition war ends by subtraction, court by court.** Pressburg, Tilsit, Schönbrunn, Lunéville: the beaten continental member left and the paymaster lingered. The one joint instrument of the era (Paris 1814, Chaumont) was the **winners'** form. The game offers one table for both.
2. **The leader stipulates for its allies; the ally is a beneficiary with a bill.** Brünn then Pressburg Art. 6; Alexander bargaining Prussia's fate inside his own treaty (Prussia then signing a harsher one); Francis for the Reich. Not a co-signature.
3. **The armistice is the victor's instrument.** It freezes the field, levies on the held soil, detaches the loser's ally, takes sureties and holds the line (a timetable at Austerlitz; open-ended at Znaim; a month's notice at Tilsit). The game's truce inverts the score and the levy, replaces the line, the sureties and the open hold with an automatic five-turn fork, and keeps only the war's aims.
4. **Tempo.** 24 days from Austerlitz to Pressburg (under two half-month turns); 25 for Tilsit; 100 for Schönbrunn. At Pressburg the loser asked within hours, on a channel that pre-dated the battle; at Tilsit and Schönbrunn the request came five to six days after the decisive battle. A court that goes silent for three turns (F9) is slow; a court that stalls three months on hope (Schönbrunn) is right.
5. **The loser's clock is hope and finance**, not time: Austria signed when Walcheren, Prussia and Russia had each failed; its paper money and the indemnity stream decided 1809 and 1811.
6. **The neutral is bought as part of the peace** (Prussia at Schönbrunn, 1805), and the ally can be bought by the enemy before any peace (Bavaria at Ried, Württemberg at Fulda, 1813).
7. **Gold and land are not fungible.** Austria offered 100 million to keep Tyrol and was refused; indemnities were streams, with fortresses held until paid (Tilsit's three, by the 1808 convention); the victor's cash was itself collateralised.
8. **Terms ratchet with each refusal**, pegged to the coalition's internal bargain (Reichenbach → Frankfurt → Châtillon), and **regime change decouples harshness from score** (Paris 1814).
9. **Relations follow the peace; they do not gate it.** Schönbrunn was signed at the nadir; the marriage contract followed in 116 days (7 Feb 1810), the proxy wedding in 148.

## 38. The replays — what the game can sign today

Each element of each peace was staged or probed on the game's own machinery (M1–M8). "Road"
names where it carries: the **table** (Open Settlement with coverage narrowed), the **wizard**
(the bilateral peace), the **truce**, or the **AI's own letter**.

**Pressburg** (M1, the Vienna-held board, seed historical)

| Element | Today | Road | Why not |
|---|---|---|---|
| Austria out while Britain and Russia fight on | **Yes** — ratified turn 6 | Table, Austria alone (white peace 50/50 exactly) | Wizard: paradox at send (`treaty.py:437-449`); AI letter: Austria's P1 is a truce or a peace on its terms, not Pressburg's |
| Bavaria's and Italy's wars end in the same instrument | **Yes** — "3 pairs resolved"; Austria leaves the coalition | Table | Bilateral ratifier carries clients only (`follow_the_lord`, `diplomacy.py:3131`) and charges France −20 with Bavaria (`apply_separate_peace_penalties`, `world_state.py:13455-13467`) |
| Tyrol to Bavaria | **No, on every road** | — | Austria cannot cede what France occupies: the guided verb refuses, the ratifier **silently skips** the clause after the scorer priced it and the review promised it (`settlement_ratify.py:352-353`, **F52**); France cannot cede to an ally (V3, `settlement_validation.py:1398-1412`); the guided payee is hardwired to France (`settlement_actions.py:1240`, **F53**) |
| Venetia to the Kingdom of Italy | **By wire only** (the map has no Venetia; Carniola stands in) | Table — valid, scored and ratified (Carniola transferred to Italy, probe) | Unauthorable in the client (F53); the ally's reward is priced as harshness against Austria like a French demand (58 → 34 at +70) |
| An indemnity | **Yes, inside a trade** | Table: 1,000 gold alone 16/50; with Vienna and Bohemia returned 87–100, ratified (D2) | The bilateral formula counts France *returning* provinces as harsher than taking them (`diplomatic_templates.py:4533-4541`, **F55**): return Vienna + Bohemia = 35 COUNTER |
| Napoleon returns Vienna (the actual Pressburg) | **Scorable (50 → 100), ratifiable, hidden** | Table by typed wire params | The offer rows skip capitals (`settlement_baseline.py:534-535`, **F54**); the client authors only from the rows |
| Russia marches home under the armistice | **No** | — | Nothing makes a coalition partner stand down when a member signs; on D2 a Russo-Austrian non-aggression pact (an open-movement state) gave Kutuzov a road through Moravia |
| Armistice first, dictated peace at expiry | **No as a dictated peace** | A concession-funded trade still carries at the table under the truce (62 / 57) | The truce pops the stored score the bilateral reads (75 → 0); expiry is PEACE with no terms or WAR (`diplomacy.py:11284-11292`) |
| Austria's revanche | Re-sworn turn 6 on both arms; Britain pays Austria 200–400 gold a turn; no new coalition in 12 loops | — | The coalition's alarm moved **95 → 94** when the court that did 94 % of the fighting left (M4) — Part I's "the coalition's threat reacts" does not hold |

**Tilsit** (M2, `fixture_agd_tilsit.json`; **the fixture's +100 is hand-set** — the live board computes 30–37 and the first advance stores 34, **F85**)

| Element | Today | Road | Why not |
|---|---|---|---|
| The Duchy of Warsaw carved | **Yes, as a purchase** | Table's carve carried by `seek_bilateral_peace`; the proclamation fires | At the real score (34–37) the carve alone is bilateral 2 / table −10; the only signable form is carve + **France pays Prussia 6,000** (62). Napoleon did not buy Posen. |
| Prussia's western lands taken | **No** | — | Prussia on the registry is six provinces east of the Elbe; no Westphalia template |
| The indemnity, Tilsit's way | **No** | — | Demanding 300 gold drops the carve 58 → 46 at the fixture's 100; every signed indemnity flowed France → Prussia |
| An army cap | **No clause exists** on either dialect | — | `CANONICAL_CLAUSE_TYPES` has eleven types, none military (`settlement_scoring.py:100-141`); the ledger's force ceiling already exists as its natural write |
| The Continental System joined | **Yes**, alone, at a strong but not total victory (bilateral 54 at 65; table 51 at 80) | Both | Added to the carve it fails everywhere; and where the joiner's port already counts (Berlin held), the clause closes **11 → 11 ports** and costs the member nothing (**F68**) |
| Russia made an ally in one treaty | **In the ratifier, not in the scorer** | Table only (forced_alliance has no bilateral dialect) | Carries at exactly 50/50 at a stored 100 with Russia's exhaustion; Part II's no-decisive ceiling is 65 (FA 25–31) |
| Russia courted after (Tilsit → Erfurt) | **Two-step, by the AI's own letter** | The volte-face courier proposes the alliance itself | From −95, 17 turns of Improve Relations, and Russian homeland soil must stay in France's hands — not what Tilsit did to Russia |
| The peace holds | **No** — torn up at turn 8 by a coalition declaration | — | The bilateral peace writes **no fresh-peace floor** (the table writes 5; **F69**); Prussia's emergent Revanche forecloses her volte-face while France holds the soil; a carve writes **no punitive record** (**F57**) |

**Schönbrunn** (M3, seeds austerlitz and historical, commanded, accept)

| Element | Today | Road | Why not |
|---|---|---|---|
| Austria starts a war of her own | **One seed**: austerlitz t20, "Primacy in Germany" on **Bavaria**, with the deterrence beat two turns before | The design road (`war_council.py:720-787`) | France is dragged in by alliance with **no letter asked**; Britain joins Austria; at t24 the coalition's declarations are **welded into Austria's instance** (`settlement_helpers.py:685-745`), so the instance leader (Austria) is not the coalition leader (Britain) and the league gate reads the wrong court (**F58**). Historical: Austria's second war was the coalition clock's (t37), Austria gutted by Bavaria at the first peace. |
| A lone war that ends by itself | **No** — 26 turns, the slowest war the game has | The instance leader's white peace after the league dissolved | With France inside, the AI–AI exits are skipped; Austria's letters are P2 truces that collapse at −85 and **reset the clocks** (`war_start_turns` re-stamped; exhaustion −5 a turn in truce; **F59**) |
| A peace France dictates | **No road at any score** | — | While France is not its side's leader the table is **closed** ("Only the war leader can settle this side", `settlement_validation.py:1105-1111`) and the bilateral is paradox-blocked by the very ally whose war France joined (**F49, P1**). Once open, the Schönbrunn bundle reads −79 … +2 from −1 to a forced +80: raw harshness 2.3 exceeds the total-victory ceiling 1.0, the penalty caps at −45 (**F61**). At +80 the table buys a white peace, **or** CS alone, **or** one province. |
| Salzburg to Bavaria | **Not representable** (no Salzburg; Tyrol stands in; Bavaria dead at t27) | — | — |
| Illyria to France | Carries **alone** at +80 (53) | Table | Both Carniola and Croatia: 39 |
| An indemnity | **Never carries**: 1,500 gold 21/50 at +80; 500 gold 27 bilaterally | — | While Austria's own P1 letter **offers** 300 gold a turn as a sweetener — the four exchange rates for gold against land contradict one another (**F60**) |
| The Continental System | Table only, 61 at +80 | Table | The bilateral scorer prices no CS clause |
| An army cap | **No clause** | — | — |

**Lunéville and Amiens** (M4, both turn-6 boards)

| Element | Today | Road | Why not |
|---|---|---|---|
| Austria out while Britain fights on (Lunéville) | **Yes** (62 on the copy, 50 Vienna held) | Table, Austria alone | As Pressburg |
| Britain makes peace unbeaten (Amiens) | **Yes, by the AI's letter** at turn 10–11 (exhaustion > 80) | AI letter | Wizard: paradox on **Spain** (an ALLIANCE partner; Holland, a client, is invisible to it); even with Spain downgraded Britain answers 20 REJECT — nothing but the France–Britain pair moves `calculate_acceptance`. Table, Britain alone: a white peace 6/50 (worse than 18 on the whole-war table, because the base stops being diluted by Austria's +54); one gold line caps at 46/50 at any amount (**F62**) |
| Spain and Holland sign alongside | **Yes** on every table road (3 / 4 / 7 pairs) | Table; AI letter | The bilateral road would leave Spain fighting — which is why it is barred |
| No indemnity / colonies returned | **Partly** | — | If Austria is still covered when Britain's letter comes, the letter has **Britain pay France 2,819 gold** (40 % of its chest) — the letter's direction reads the side **SUM** (47 ≥ 20) while the table's tier reads the **MEAN** (17, white peace) (**F63**). With Austria out first (the Lunéville sequence), the letter is a white peace: Amiens in shape, at turn 11–12. |
| Peace by weariness | **Yes** — and the only fleetless lever on Britain is the Continental System's closure notch, which **cancels itself**: the Royal Navy's blockade and France's closure credit both sides one turn every turn, the differenced component is 0 for ever (`naval.py:2954-2990`; `diplomacy.py:3598-3610`; 8 / 8 after eight turns, M7; **F64**) | — | London by expedition: 6 % at 15,000 men |

**The 1814 mirror** (M5, seeds ulm, historical, jena; France refusing every letter)

| Element | Today | Road | Why not |
|---|---|---|---|
| Frontiers / half the territory dictated | **No, on any road** | — | The AI's harsh peace appends **one gold lump** (`ai_diplomacy.py:990-1011`); the captor and Congress rungs reuse it; no AI producer emits `territory_cede` at war. Multilaterally: peace + one indemnity + at most one `create_client` from a catalogue whose only French-soil template is Normandy (`:4393-4517`) |
| The Normandy carve | **Yes, settlement road only**, from the turn Normandy falls | AI letter | The rail announces such a letter as "Asking N gold" and nothing else (`turn_manager.py:951-979`, **F65**) |
| An indemnity | In kind, inverted in scale | Both | Priced to the **payer's purse** (40 % cap; 15 % floor): the ask on the rail fell 2,543 (t11) → 363 (t32) as France fell 26 → 1 provinces, rising to 872 at t37; the Emperor's ransom was 349 gold |
| An army cap | **No clause** | — | — |
| Abdication / exile | **As a game end only** ("The Eagle in Chains", "Without Soil or Sword") | — | No peace in which the dynasty falls and France survives |
| The coalition's joint dictate (Chaumont → Paris) | Partly: one leader's letter covers every court | AI letter | The coalition object **dissolves for low threat while its members hold Paris** ("Coalition against France has dissolved — Austria, Britain and Russia remain at war with us", `coalition.py:2444-2447`, **F77**) |
| Why the AI's score stalls | — | — | The **loser's shield**: France's own `defense` ticking +25 against each occupier; Austria holding 13 French home provinces read +23; the territory cap bites at 8 provinces (`diplomacy.py:3554`). The same term caps France's own victories (Part II §9). |

**Five peaces, one verdict.** The game can sign, today, a Pressburg-*shaped* separate peace
and an Amiens-*shaped* exhaustion peace — by the table and the AI's own letter, never by the
wizard, never by the truce. It cannot pay an ally out of the loser's soil, return a capital
from the client, cap an army, dictate a Schönbrunn, or be dictated to as France was in 1814.
The historical shape the game is **furthest** from is the armistice: every one of the era's
truces was the victor's instrument, and the game's is the loser's.

## 39. Other games

| | Beaten member of the enemy bloc | Your ally still at war | The truce | What makes the AI want peace | Peace as a decision | What the screen says |
|---|---|---|---|---|---|---|
| **EU4** | One war object, two sides. The war leader may make a **separate peace with any non-leader enemy**, judged by that pair's own occupation and blockade score; the signer "enters truce with every enemy still in the war". Coalition members and subject nations may not; a junior participant may treat only with the enemy war leader. | Cannot arise inside one war. A junior's exit costs −10 trust with each remaining participant, −30 relations with co-belligerents. Call to arms: dishonouring costs −25 prestige, the alliance, −1 reputation for 10 years, and hands the caller a casus belli. | No armistice. The truce **follows** the peace and is sized by it (5 + 0.1 × warscore-% years). Breaking it: −5 stability, +5 exhaustion, −50 AE. Nothing is ever wiped. | A signed sum of named reasons: +1 per own warscore point, −1 per demanded point, war enthusiasm (+45 at the start decaying 0.75 a month; occupation, siege, exhaustion −1 per point to 20). Exhaustion is **event-driven** (attrition, battles, blockade, occupation). | What to buy with one legible budget, and when (the truce you buy, the coalition risk). Players still reset games to learn why a won war will not end (one thread: three resets at 74 %); the folk explanation is that the AI leader waits on its secondaries. | The demands with their warscore and DP costs against the running total; the reason list; the truce end date; the ledger's current wars. War enthusiasm, exhaustion included, is summed in the war screen; whether the enemy's exhaustion shows as its own number is unconfirmed. |
| **CK3** | No per-member peace at all: two signatories, one stake (the casus belli), allies released by the leader's signature. | A called ally has **no documented exit** (community reports — "stuck 9 years in a war against my own liege" — unverified); a liege can end a vassal's offensive war (1.1). War Contribution dunns a 0 % ally after two years. | No armistice; a 5-year post-peace truce; breaking it −250 prestige, −1 Fame. **Purchase Truce** lets the weaker side buy a pause. 1.20 adds clerical mediation ("Request White Peace", "Request Victory" at 90 %). | Thresholds (+30 white peace may be called; +100 enforce; −100 surrender) plus a small named stack (Peace Acceptance perks) and, since 1.1, the AI weighs war length and bankruptcy for a white peace. The tick rewards whoever **holds the war goal**, with memory. Capturing the ruler = +100. | Made before the war (which CB, which title, whom to call); then a race to a number. Legible because small; tedious because three outcomes. | The war's **name is its stake**; one bar, four hover components; Will accept / Will not accept with the modifiers. No percentage, no cure. |
| **HOI4** | No separate peace for a member and no acceptance step: a country **capitulates** when it loses more than its surrender limit of core victory points (80 %, lowered by war support and collaboration, floor 20 %), to the enemy with the highest war score; it persists as a government in exile and its occupied soil **pays the victor**. One conference when the faction's majors have all fallen. | Cannot leave a faction at war; the tooltip does not warn. Unmerged wars resolve in an order nobody can predict ("Before I even had a chance to bid for things", Steam, 2019). | No mid-war ceasefire verb; a 180-day post-peace truce priced in political power. The war score is **never wiped**, only spent. | Collapse is a visible **state** read live (the surrender bar), not a letter; war support falls from casualties, raids and bombing since 1.12. The only negotiated exit is the faction leader's conditional surrender (3 months, 0.5 ratio, six signed terms). | During the war, none; at the end, a dense click-contest the designers call "rightly one of our most disliked" features. Participation (casualties 0.5 per 1,000, strength, captures) decides the budget; under 5 % gets nothing when the redistribution game rule is on. | Every price decomposes into named multipliers on Shift-hover; the surrender bar per nation. Not shown: why a victor arrives with negative score. |
| **Victoria 3** | The beaten country **capitulates by itself** at −100 war support, binding only itself; every goal against it is enforced; the war continues if goals remain. A negotiated peace is whole-war only and needs every stakeholder's ratification. | Cannot arise inside one war; a secondary participant cannot propose or leave ("my only option is to capitulate"). | No ceasefire; a 60-month post-peace truce; nothing to wipe. | **Two meters per court, never averaged**: war support (occupation tiers 0.1 → 10 a week, casualties scaled by battles lost, radicals, lobbies; only 0.2 a week for time; a **floor at 0 lifted by the capital or the goal state**) and peace-deal acceptance pricing the **terms** (−8× per goal enforced on itself, the achievable-goal look-ahead, debt +200). | Front-loaded: terms declared with the play, so the peace screen is press/drop over a known list; no Pressburg bargaining at the end (from 1.9 treaty articles may be addable at the table — unverified). Paradox has patched capitulation for four years (the 1.1 clock, the 1.2 rewrite, the 1.15-beta "capitulate when clearly defeated"). | Per-court war support with sources; per-negotiator signed acceptance; a white-peace button that predicts; the end-of-war ledger of enforced goals; "why this court cannot capitulate". |
| **Total War** | No coalition instrument and no leader: every war is a pair, every peace bilateral, the enemy's allies stay at war. Rome II satrapies follow the overlord's peace (Patch 3); the rule for ETW/NTW protectorates and Warhammer vassals is undocumented. | Allowed everywhere, priced in reliability; the residue is twenty years of "the ally made peace the next turn and left me at war" and no verb to ask an ally to stop. | No truce; peace is total and instantly reversible; a hidden re-declaration cooldown (10 turns = −30 reliability in Warhammer; 5 turns shown in Three Kingdoms). | No formula published: relative strength, attitude, strategic threat, distance, trustworthiness; **no exhaustion** in the classic titles — players report never seeing the AI "take a peace treaty unless they were down to absolutely no armies left"; a Warhammer III mod reportedly adds war exhaustion to the peace evaluation (unverified). | A purchase whose price is computed for you (3K "Make it work", WH3 scales) and a timing decision priced in reputation; worthless in Napoleon: Total War because victory needs Vienna held and the AI never cedes its capital region at the table. | 3K: attitude breakdown, trustworthiness as a second axis, a greylist that tracks an offer's progress. WH2/WH3: a Quick Deal list ranked by willingness. ETW/NTW: no reason, no percentage. |

**Borrow** (each with its reason):

1. **The leader's separate peace as an ordinary verb, judged by the pair's own score** (EU4): the signer's exit is an exit from the war against the side; the ally's war ends with it. The table road does this; the wizard forbids it.
2. **Price the separate peace in standing, never in a stop** (EU4 trust −10 / relations −30; TW reliability): `apply_separate_peace_penalties` already prices the junior arm (`diplomacy.py:5122-5141`); extend it to the leader's arm and the greyed button becomes a choice.
3. **The truce never wipes the ledger** (EU4, HOI4, Vic3 — none has a mid-war ceasefire; HOI4's score is only ever spent): if the armistice stays, it freezes.
4. **Acceptance as a signed list of named reasons, sorted by size, with the one term that would flip the verdict** (EU4, HOI4's Shift-hover, Vic3's per-negotiator number): `calculate_acceptance` and the common-peace scorer already compute every component; no surface lists them (F12, F37, F40).
5. **Capitulation as a visible state, read live** (HOI4's surrender bar, Vic3's −100): a per-court "will she break?" line on the war card computed from the predicate P1 actually evaluates, from the same store — or it reproduces F3 in a new place.
6. **A stake floor instead of an equal vote** (HOI4 under 5 % participation gets nothing under its redistribution rule; Vic3 non-stakeholders "have no say"; CK3 War Contribution): the game already classifies France's allies by material share (`war_contribution.py:87-88`); under Building Blocks the same ladder should classify the enemy side — a court under consult share is covered, not consulted.
7. **The war's name is its stake** (CK3; Vic3's declared goals): title the war by its purpose, not by the coalition's leader (F41), and let every surface price the same object.
8. **Event-driven exhaustion that enters acceptance** (EU4, Vic3): occupation tiers, casualties scaled by battles lost, debt; time only as a small base. Ruling H (b) in finished form, with EU4's warning: its +45 early-war enthusiasm term, decaying 0.75 a month, is the class of rule that breeds "the AI never accepts peace" threads unless its decay is shown (a 2013-era forum post, read via search summary).
9. **A re-declaration cost printed where the resume button is** (TW; EU4's truce-break penalties): a truce the loser can resume for free is a pause, not a treaty.
10. **The loser's letter carries terms** (3K: the AI pays when losing; Vic3: a capitulation enforces goals): Austria's `armistice_losing` should arrive with Pressburg-shaped terms, not a bare truce that strikes France's score.
11. **A truce the loser buys** (CK3 Purchase Truce): if the AI asks for a pause, it pays for it.

**Avoid:**

1. **Requiring every secondary to be satisfied before the leader may sign** (EU4's won-but-endless wars; Vic3's −140 ally with no goals; HOI4's unmerged wars): the game's F4 in three other games' clothes.
2. **A bare time gate with no battlefield condition and no shown cure** (EU4's five-year clock — a time-plus-occupation exception players still call arbitrary; Vic3's 1.1 white-peace-by-duration term, which players by April 2025 blamed for how "the AI loves to white peace currently" — a complaint that may trace to it, not a documented consequence; its 1.15-beta goal-expiry clock was reverted as "the wrong solution"): F21's 5-turn letter is this shape.
3. **Hiding the enemy's exhaustion** (an EU4 forum complaint that the game does not show that data, read via search summary; F42's "Unknown").
4. **Binding a junior partner with no exit** (CK3's called ally with no documented exit; HOI4's "leave before the call"; Vic3's secondary who can only capitulate): ruling B (a) imports exactly this.
5. **Allies as traps** (TW's twenty years of threads): the residue of B (b) alone — allowed, priced, and the ally fights on with no verb toward it. C with a price is the option Total War never tried.
6. **A score that rewards the side that bled** (HOI4 1.12 cut casualty-taken participation; Part I F6 was the same class, fixed in S13d).
7. **A verdict of "you won and get nothing" with no named term** (HOI4's negative-score conference "as if this war NEVER HAPPENED"; the table's −10 white-peace legitimacy under a Harsh Peace panel).
8. **Three fixed outcomes** (CK3's "lack of deepness"): shrink the explanation, not the guided terms.
9. **A balance button that only knows gold** (3K, WH3): the game knows the non-gold answers (win a battle, drop a court, return a province); do not borrow the button without its missing half.
10. **Hidden floor rules** (Vic3's per-goal contestion table on the wiki, not the screen): a rule that gates peace must be on the screen that refuses it.

## 40. The rulings, designed

Each ruling is given as a design the user can take or refuse, with its costs, the seams a
build would touch, what Golden Rule 5 (Building Blocks) requires of it, and the evidence for
and against — measured where it was measured, read where it was only read. **None of this is
built.** Two rulings are new (I and J); B folds into C.

### B — one verdict for the separate peace → **fold into C: "allowed, priced, and the leader's peace is common to its side"**

- **Design.** One predicate, read by every road: France's peace with a court is never stopped by an ally's war; it is **priced** (the existing `apply_separate_peace_penalties`) when France leaves an ally fighting, and it **ends the ally's war** when France leads the side (C). The seven readers — the send road, the table's chip, the counsel's "press X alone", the Congress lever, the incoming letter, the truce expiry and the typed `break treaty` — read that one verdict. The owning spec is named: `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` §10.5 (partial coverage, the side's pairs carried) owns the treaty; FA-D17's paradox is amended to defer to it.
- **Costs.** About half a session: the predicate and its readers; the sign-ability sweep re-run (A = 0, B = 0); PC-F1's word pins re-seated.
- **Seams.** `diplomacy.get_peace_commitment_conflicts` (`:5446`, the HARD_STOP arm `:5533-5550`); `treaty.can_sign` step 9 (`treaty.py:437-449`); `settlement_validation.evaluate_pair_peace_substitute_eligibility` (`:530-545`); `settlement_staging.separate_peace_chip` (`:2593-2644`) and `legitimacy_sentence` (`:2466-2480`); `_process_armistice_expiration` (`diplomacy.py:11284`, no verdict read today); `break_treaty` (`:11946-11962`, a truce broken becomes an unsigned PEACE — **F82**); `ai_diplomacy.deliver_ai_proposal` (`:2686`; its guard `treaty_offer_refusal` `:2637-2669`, called at `:2713`, exempts peace and truce).
- **Golden Rule 5.** The AI's separate peace is checked neither at send nor at delivery; France's is hard-stopped at send. One predicate for both chairs also means the AI's P1 letter names the pairs it ends (today `_build_proposal_terms('peace')` carries no coverage, `ai_diplomacy.py:866-879`).
- **For.** The code has ruled "allowed, priced" four times (incoming, joined-at-call, the truce, the table); the measured B arm left no major at war with France at turn 40 on any seed (Part III §19); every historical leader did it.
- **Against.** B (b) alone — the ally left fighting — cost France provinces on three seeds and seeded a Fourth Coalition on jena (Part III §19); Total War's twenty years of "my ally fights on and I have no verb toward it" are the residue. Hence C.

### C — the Pressburg road → **the leader stipulates for its allies; the ally is a beneficiary with a bill**

- **Design.**
  1. **One carry-in set.** The instance's co-belligerents on France's side at WAR or ARMISTICE with the covered court — the table's plan rule (`settlement_ratify.py:190-222`) — becomes a shared helper. The bilateral ratifier resolves those pairs (`set_diplomatic_state` + `cleanup_war_end`, as `_resolve_pair_state_transitions` does); `apply_separate_peace_penalties` skips the carried allies; the HARD_STOP falls away when every paradox ally is in the set. Clients already follow (`follow_the_lord`).
  2. **One consent read.** The covered court's willingness to leave the coalition is judged by its **own** readiness — `coalition_break_ranks_reason` and `effective_peace_threshold` read for the recipient of France's letter — not by the side mean (the table today) and not by the bare bilateral formula. The same predicate the AI uses to decide whether to sue (`ai_diplomacy.py:1533-1561`, `:598-621`).
  3. **The ally's bill.** The Slice H petition fires at the stipulation: `_objective_has_material_claim` returns False for a `defense` objective (`settlement_offers.py:565-571`), so on the 1805 boot Bavaria never asks for Tyrol; read the ally's desire profile instead (`diplomatic_templates.py:3243-3250` already lists it). The guided demand verb gains a `to` (the payee is hardwired to France, `settlement_actions.py:1240`, **F53**) and the ally's reward is priced as the leader's demand, not as extra harshness (measured: Tyrol → Bavaria dropped Austria 58 → 34 at +70). The reward writes the ally's gratitude memory; its refusal the shut-out memory (both exist in `settlement_reactions`). The ally's standing is read **before** its episode closes (today it reads `no_standing` and reacts to nothing, `settlement_ratify.py:1555-1565` vs `:1660-1690`, **F81**).
  4. **The words.** "Bavaria's war ends in this instrument; she is named for Tyrol" replaces "would break her war" on the chip, the counsel and the refusal (F35, F43); the bilateral hand-off stops re-routing the ally's cession to France (`settlement_staging.py:2548-2551`, **F70**).
  5. **The two Pressburgs.** The confirm names which draft this is: a cession of two provinces or the capital writes the punitive memory that forecloses the volte-face and promotes Revanche (`emergent_designs.py:72`, `:519-526`); a confirmed cession reconciles the Revanche while the treaty holds (`agendas.py:305-320`). "Revanche stands" or "Revanche lapses" is one line, read from the seam the AI reads.
- **Costs.** One and a half to two sessions. The DD-1 sign-ability sweep and fuzzer re-run; `BASELINE_SERIES` moves wherever the AI's P1 letter gains coverage — attributed, not re-pinned blind. Risk: pricing an allied beneficiary at full harshness means the historical Pressburg clause never carries where a bare white peace does; the rate is a decision.
- **Seams.** `settlement_ratify._build_pair_ratification_plan` (`:172-252`) → shared helper; `world_state._ratify_war_end` (`:13177-13217`) and `:13455-13467` (the penalty); `diplomacy.get_peace_commitment_conflicts` (`:5446`); `settlement_staging._pair_substitute_seed_terms` (`:2490-2590`); `settlement_actions` `:1240`, `:1265`, `:1314-1317`, `:1345-1348`; `settlement_offers` `:565-571`, `:592-607`, `:731`, `:771`; `treaty.py:535`; `settlement_reactions` `:505-508`; `ai_diplomacy._build_proposal_terms` (`:866-879`); `settlement_scoring.compute_settlement_package_raw_harshness` (`:733-766`) for the beneficiary's rate.
- **Golden Rule 5.** The carry-in is the predicate the AI's own letter already uses (every opposing court at war with the side, `ai_diplomacy.py:4645-4660`); the consent is the AI's own break-ranks read. The player's wizard and the AI's letter would then describe the same instrument.
- **For (measured).** The Austria-only table ratified on turn 6 and ended Bavaria's and Italy's wars (Parts III–IV, M1, M4). The C arm kept France at 28 provinces on four seeds against B's 16–22, with no new coalition (Part III §19). History: Pressburg Art. 6; the Brünn treaties; Alexander bargaining Prussia's fate inside his own treaty; Francis for the Reich.
- **Against (measured).** The ally's claim never fires on the 1805 boot (the `defense` objective; no Bavarian deck); without the bill C is a cutscene. The coalition's alarm moved 95 → 94 when the court that did 94 % of the fighting left (M4) — Part I's "the coalition's threat reacts" is not there to collect. The table charges a carried ally's reward against the loser like a French demand.

### D — the victor's truce → **the truce freezes the ledger, keeps the war's age, and ends in a dictated peace when the loser's hope has died**

- **Design.**
  1. **Freeze, don't wipe.** The pops of `battle_records`, `decisive_battles`, `war_scores` and `war_score_history` move behind `conclude_objectives` (the campaign ledger already survives a truce by that rule, `diplomacy.py:2843-2845`); `recalculate_war_scores` keeps the stored score for ARMISTICE pairs, or the signing snapshots it. The exhaustion pop for a single-front court (`:5774-5787`; Russia 90 → 0 on one truce) goes with it.
  2. **The war is not new on collapse.** The original `war_start_turns` is carried across the truce (the instance keeps its `war_id`); today it is popped at the truce and re-stamped at the collapse (`:2942-2945`), so the −65 war-age penalty returns for eight turns and the young-war band re-opens (**F59**, measured on austerlitz: three truces in 26 turns).
  3. **A peace signed under a truce is signed** (`game_end.SIGNED_PEACE_REASONS`, `:110-117`); today a truce that lapses into peace titles nothing (`:94-96`) and no surface says so.
  4. **Two exits.** At expiry: a **dictated** peace on the held line if the loser's live pair reads ≤ −50 and no hope has revived (no new member joined the coalition, no subsidy landed, the victor's exhaustion not past the loser's) — the terms are the sureties filed at the truce; otherwise the **courted** peace at the −60 relation line (the volte-face's door); otherwise WAR. The AI's `armistice_losing` carries sureties (gold a turn, a held province) and the player may refuse a truce; a court that asks for a pause pays for it (CK3's Purchase Truce).
- **Costs.** One session plus the client words (`armistice_mechanics.display_lines`, `diplomacy.py:5011-5037`; `war_status.py:641-669`; F44). The series moves on every AI truce — attributed. Risk: a truce that keeps the score makes the AI's P1 armistice between −50 and −70 a surrender-in-waiting; move the −70 split (`ai_diplomacy.py:1862`) or let the letter say so.
- **Seams.** `diplomacy.cleanup_war_end` (`:5755-5758`, `:5774-5787`, `:5790-5792`); `recalculate_war_scores` (`:3813`); `set_diplomatic_state` (`:2932-2945`); `_process_armistice_expiration` (`:11282-11308`); `armistice_resolves_this_turn` (`:4625-4645`); `game_end.SIGNED_PEACE_REASONS`; `war_status.py:641-651`; `coalition.next_war_exhaustion` (`:245-272`, the −5 in truce).
- **Golden Rule 5.** The same expiry walks AI–AI truces; verify whether `_ratify_ai_ai_events`' +10 relation (`world_state.py:13615-13620`) lands on an AI–AI armistice while the player's gets none — the identical −80 truce would then end in peace between two AI courts and in war for France (**F87**, to verify).
- **For.** Every armistice of the era froze the field and kept the victor's leverage (§37); Part III's "D never fired" was unreadable by construction (the stored score is 0 under every truce; the scripted France stops attacking at turn 13); the live score under a truce keeps territory, capital, campaign and blood (32 of 51 on the probe board; 79 → 54 on the user's, M1).
- **Against.** The expiry fork itself is unmeasurable until the freeze exists; the stalemate's reconciliation (the −60 arm) must stay or a level war has no exit but collapse.

### I — what the AI may dictate (new: the 1814 mirror)

- **Design.**
  1. The AI's harsh peace (P8, the captor, the Congress rung) may demand what the player may: a province, a client state, the Continental System, a forced alliance — the player's clause types, priced by the player's scorer. Today it appends **one gold lump** (`ai_diplomacy.py:990-1024`); the multilateral letter carries at most one `create_client` from a four-template catalogue (`:4393-4517`).
  2. **The ratchet.** A refused offer raises the next offer's demand by a tier (an offer history on the war instance), as Reichenbach → Frankfurt → Châtillon; today a refusal buys a 3-turn nation silence and a 6-turn same-type block (a settlement letter: 5) and the next letter is identical (`_is_on_cooldown` `:343`; `NATION_REJECTION_COOLDOWN` `:47`, `TYPE_REJECTION_COOLDOWN` `:51`, `SETTLEMENT_OFFER_COOLDOWN_TURNS` `:4165`).
  3. **The indemnity is priced to the war**, not to the purse: a lump plus a stream, with provinces held until paid (Tilsit's three fortresses by the 1808 convention; Braunau held past Pressburg's date). Today both channels price to the payer's chest (40 % cap, 15 % floor, `:4211-4250`, `:1027-1041`): the ask on the rail fell 2,543 (t11) → 363 (t32) as France fell 26 → 1 provinces (872 at t37), and the Emperor's ransom was 349 gold (M5).
  4. **Refusal costs France.** The Charges of Empire name the refused peace; the marshals' petitions carry it; the war panel shows the next letter's tier. "Continue fighting" (Part IV M5) becomes Châtillon with a price.
  5. **The regime arm** (GE-2's owner): a Fall that ends in a peace the successor government signs (Talleyrand for Louis XVIII, after the Senate's déchéance) — recognition of the successor as the term that buys leniency (Paris 1814).
- **Costs.** One and a half sessions; the losing campaigns' series move (attributed); the Normandy carve's rail line (**F65**).
- **Seams.** `ai_diplomacy._build_proposal_terms` harsh arm (`:990-1024`); `_settlement_offer_build_terms` (`:4393-4475`), `_settlement_offer_carve_clause` (`:4477-4517`, the first eligible template only); `purse_scaled_indemnity` (`:4211-4250`); `_reduce_p8_demands` (`:1043-1123`); `world_state.get_state_charges_rate` (`:6608-6640`); the petition channel (`jealousy.py`); `game_end` for the regime arm.
- **Golden Rule 5.** This ruling *is* Golden Rule 5: the player may author `territory_cede`, `create_client`, `continental_system_join` and `forced_alliance` at war; the AI may not.
- **For (measured).** Eighteen harsh letters on three seeds, all gold (M5); no AI producer emits `territory_cede` at war; the loser's shield holds the AI's score at 23–49 while it holds 10–13 French provinces and the Emperor.
- **Against.** None measured; the design cost is a new letter shape and a series the deploy's balance pins must absorb.

### E — who prices the coalition's peace (with F23) → **each court on its own war, a stake floor, a payment to the court paid**

- **Design.**
  1. **Not material-share weights inside the mean.** Re-scored that way the user's white peace carried 56 / 51 / 51 (Part III §22) — Britain and Russia sign *because Austria lost*: the opposite error.
  2. **Each court's base reads its own pair** (blended with the side pressure), so Britain at 0 is unmoved by Austria's defeat and Austria at +79 is not held at 11 by Britain's 0. The seam is `calculate_base_side_pressure` at its call (`settlement_scoring.py:694`, `:2255`) with `selections[court]` (`settlement_baseline.py:1937`, `:1978-1984`).
  3. **A stake floor.** A covered court under `CONSULT_MATERIAL_SHARE_THRESHOLD` (0.10, `war_contribution.py:88`) is **covered** by its side's settlement, not consulted — no veto. The ladder France's allies already live under (`classify_standing`, `:483`) classifies the enemy side too (HOI4's 5 %; Vic3's "no stake, no say").
  4. **F23 and the dial.** A payment credits the court it is paid to in full and the side fractionally; the gold cap binds per package, not per line (**F62**: 1,000 + 100 in two lines carries where 1,100 in one does not); "More generous" pays one court once and the words say so.
  5. **The AI's letter is dry-run as the player's is** (`_letter_would_carry` passes `consenting_courts = covered`, `ai_diplomacy.py:4620`), and the leader is re-seated by contribution when the letter is written (`_choose_leader_for_side`, `settlement_helpers.py:1264-1280`; today Britain's letter settles Prussia's war — **F50**).
- **Costs.** One session; seven test files reference the concession credit; the tier legitimacy must then read the court's own tier or the −10 white-peace charge keeps biting a victor in Vienna.
- **Seams.** `compute_side_pressure_score` (`:337-472`; the weight at `:418`); `calculate_concession_credit` (`:1516-1561`); `compute_per_court_acceptance` (`settlement_baseline.py:1873`); `war_contribution.classify_standing` and the thresholds (`:87-88`, `:483`); `ai_diplomacy._letter_would_carry` (`:4599-4626`); `settlement_helpers._choose_leader_for_side`.
- **Golden Rule 5.** Three acceptance regimes exist for one scorer today: the player's table (every court ≥ 50), the AI's letter (every court consents by fiat), the AI–AI road (the winner alone). E should leave one.
- **For (measured).** Britain alone reads 6/50 — *worse* than 18 when diluted by Austria's +54 (M4): the mean, not the weight, is the trap. The league's letter covered and signed away a **winning** Prussia because Britain was paid (M6). The per-line cap (M4).
- **Against.** The spec's rationale for the weighted mean — stop France farming pressure by dragging minors in (`WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md:218`) — is answered better by the stake floor than by weights; keep the floor, drop the weights.

### H — what wears a court down → **keep the clock; make it of finance, occupation and subsidy; never reset it by a truce; show it**

- **Design.** The +8 base stays (it is the one thing that ends wars: without it the coalition's war runs to turns 16–35, Part III §19). Add: **occupation** (+1 per own home province held, the defender's ticking already measures it); **subsidy** (−k a turn for the court receiving the paymaster's gold, +k for the payer — `_process_british_subsidy` runs beside the tick and the tick ignores it, `coalition.py:3222-3236`); **persistence** (not zeroed at the peace that ends the court's last war, `emergent_designs` R49 note, nor popped at a truce). Re-cut the table's term so it discriminates after turn 7 (today +20 from exhaustion 60: a constant on every measured board, `settlement_scoring.py:553-554`, `:1563-1631`). Delete or redefine `get_coalition_loyalty_penalty` (its sign makes a fresh member *harder* to peace; **F20 amended**). And **show it**: every court's exhaustion on the war card with a forecast turn, the fog gate dropped (F42).
- **Costs.** One session; the league gate's clock arithmetic assumes +8 (`ai_diplomacy.py:1637-1638`); the series moves (attributed).
- **Seams.** `coalition.next_war_exhaustion` (`:245-272`), `add_war_exhaustion_from_battle` (`:2040-2052`), `_process_british_subsidy` (`:3236`); `diplomacy.cleanup_war_end` (`:5774-5787`); `settlement_scoring.calculate_war_exhaustion_component`; `ai_diplomacy.effective_peace_threshold` (`:614`), `coalition_break_ranks_reason` (`:1533`); `war_status.py:352-359`.
- **Golden Rule 5.** The tick is symmetric already; only AI courts read it for peace. France's row feeds the Charges, never a verdict — which is where ruling I wants it.
- **For.** The clock is load-bearing (Part III §19); history's clock was finance and hope (§37); exhaustion 54 → 16 across one truce on austerlitz (M3).
- **Against.** None measured against the finance/subsidy terms; the H arm Part III ran tested half of H (b).

### G — the war score's shape → **keep the caps; decay then cap; a ticking that can fall; decide the loser's shield; show the fill**

- **Design.** Keep PT-J2's caps (the anti-farm rule). Swap decay and cap (`diplomacy.py:3566-3567`). Give the defender's ticking a decrement when provinces are returned (`:4531`, add-only today) and a rule for `objective_met_turn`. Decide the **shield**: the `defense` ticking (+1 a turn per own province held, cap 25) protects a court still fighting; it should not protect one whose capital is held — cap it, or halve it, once the capital falls. Show each component's fill against its cap in the war popup and print the trend (**F84**). Tell the player at the war's first turn that the war is defensive and `set war purpose` exists (F16 becomes copy).
- **Costs.** Half a session; every literal on the ±100 scale is a consumer (P1 −40 / −70, P8 40, break-ranks −50, the Congress −40, the exhausted-pair band 15).
- **Seams.** `diplomacy.py:3498-3523`, `:3904`, `:4477-4551`, `:4366-4392`; `war_detail_popup.gd:453-473`; `war_status.py:289-298`.
- **For.** PT-J2's own rationale; the loser's shield measured from both chairs (Part II §9; M5); CK3's tuning history let the score climb for conquest wars rather than adding timers.
- **Against.** Part III's G arm was tested only under accept, where the clock ends wars — a test with no power.

### J — the stake named, and the moderate peace (new)

- **Design.** The war's **purpose** is its title on every surface — "War for Bohemia", not "vs Britain" (F41) — and the thing the table titles. A **compensation clause**: the loser is paid in a third party's province or by pointing its design elsewhere (Salzburg at Pressburg; Austria's authored Eastern Question) — the only way the moderate Pressburg exists in the vocabulary. Terms may be **declared** at the declaration (Vic3) and **composed** at the table (Pressburg's side payments); a declared term dropped at the peace refunds part of its cost. The coalition's **no-separate-peace bond** is a priced, dated clause the paymaster pays for (Chaumont), so the league's cohesion is a lever the loser can bid for.
- **Costs.** Two sessions; a clause type, a title, a subsidy term.
- **Seams.** `settlement_routes._war_label` (`:100-105`); `CANONICAL_CLAUSE_TYPES` (`settlement_scoring.py:100-141`); `agendas`; `coalition` subsidy; `war_status` labels.
- **For.** CK3's one legible design; Vic3's declared goals; the historian's Strasbourg plan; the player's "whom am I fighting" (F41).
- **Against.** None measured; a vocabulary change touches every settlement spec.

### F — variance → **unchanged, the user's**

Determinism is the design. Default `historical`, an opt-in roll on the new-game screen (F (c)); the seeded pattern already exists (`design_ask_patience`, `ai_diplomacy.py:562-572`). Measure **reactivity** — how many of the ten levers move a court's answer — not seed spread.

### The ranking

| Rank | Ruling | In one line | Cost | Measured evidence | Risk |
|---|---|---|---|---|---|
| 1 | **C** (with B folded in) | The leader's peace is common to its side; the ally is a named beneficiary with a bill; one verdict, one consent read | 1.5–2 sessions | Austria alone ratifies on turn 6; C kept 28 provinces vs B's 16–22; no new coalition | The beneficiary's rate; the series moves |
| 2 | **D** | The truce freezes the ledger and the war's age; a dictated peace at expiry when hope has died, a courted one otherwise | 1 session | Every historical truce; the stored score is 0 under every truce by construction; F59's clock resets measured | The P1 split at −70 |
| 3 | **I** (new) | The AI may dictate what the player may; refusals ratchet; indemnities priced to the war; refusal costs France | 1.5 sessions | 18 harsh letters, all gold; the ask fell as France fell | Balance pins on losing campaigns |
| 4 | **E** (with F23) | Each court on its own war; a stake floor instead of a veto; a payment to the court paid; the AI's letter scored as the player's | 1 session | Britain alone 6/50 vs 18 diluted; the letter signed away a winning Prussia; the split payment | Seven test files; the tier charge |
| 5 | **H** | Keep the clock, make it of finance, occupation and subsidy, never reset by a truce, shown | 1 session | The clock ends wars; saturation at +20 from turn 7; 54 → 16 across a truce | The gate's arithmetic |
| 6 | **G** | Keep the caps, decay then cap, a ticking that can fall, the shield decided, the fill shown | 0.5 session | PT-J2; the shield from both chairs | Every ±100 literal |
| 7 | **J** (new) | The war named by its stake; a compensation clause; declared and composed terms; the bond priced | 2 sessions | None | Touches every settlement spec |
| 8 | **F** | Unchanged — historical by default, opt-in roll; measure reactivity | — | The five-seed instrument could not vary peace | — |

**Why this order.** C is where the user's own game stopped, and it is the one ruling that gave
a peace both available and lasting on every seed. D is the trap beside it. I is the half of
the peace system that does not exist. E, H and G are balance; they want a measured pass on a
skilled France first (§42). J is the vision's vocabulary and should be ruled before content
update 1 writes more clause types. F is settled.

## 41. The player's question — copy at each peace moment

Copy and information only: no new mechanics. "Information" names the payload field and
whether the client reads it today. Each proposal names the row it closes; **new** means the
information is not in the payload and the row is filed in §43.

| Moment | It says now (Part IV frames) | It should say | Information | Row |
|---|---|---|---|---|
| **The war card** (Part IV M1) | "Britain + Austria + Russia **+77**"; tooltip: "The peace table reads the war at 17 — White Peace … Austria 11/50 · Britain 18/50 · Russia 18/50" | "**War with the Third Coalition** — Austria +79 · Britain −2 · Russia 0. The table reads their mean (17) and asks each court for 50." Then the lever: "Austria alone would sign a white peace today; a payment of ~975 to any court carries the whole table (measured); Vienna returned would too (+35 to every court — measured on the Austria-alone table, predicted for the whole)." | The per-court stored and live pair scores are computed and discarded in `war_status._stored_and_live_pressure` (`:122-134`); `coalition_member_rows` carry each pair's live score (`:770-778`) and are read only by the coalition popup. The lever needs the Austria-alone preview (`build_settlement_preview(covered=[Austria])`, exists). | F37 (amended: the coalition popup already draws per-court bars; the **card** and the **table** do not) |
| | — | "Austria's own court would sue alone at −50 (she reads −54) — but in a war under eight turns her peace is silent; her truce comes." | `coalition_break_ranks_reason`, `effective_peace_threshold`, the −70 split and the send floor are not on the row. | **F88 (new)** |
| | no trend glyph | "+79, rising" | `trend` is computed on every row (`war_status.py:289-298`) and drawn by no surface — Part I's "71 · rising" was the JSON | **F84 (new)** |
| **The war popup** (Part IV M2) | "Negotiate Peace — Open bilateral peace options for this court only" (opens Britain); "Enemy War Exhaustion: Unknown"; one Score Breakdown; Request Terms: "exhaustion 45 of 80" | "**Negotiate with Britain** (the leader) · **with Austria** · **with Russia**" as three buttons; "Britain's exhaustion 45 — she tires at 80; her letter comes in about five turns"; the breakdown labelled "France against Austria"; a per-court breakdown behind each name | `settlement_eligibility.coverable_enemy_participants` and `opponents` ride every row unread (`war_status.py:502`, `:906`); the exhaustion is fog-gated at `:352-359` against the no-fog rule while the tooltip states it from `league_offer_gate_display` | F41, F42, F37 |
| **The wizard, Austria's page** (Part IV M3) | "Talleyrand recommends: Propose Armistice"; "Propose White Peace"; Propose Peace disabled: "Bavaria is still at war with Austria — propose an armistice, or first Downgrade …" | "Peace is barred by Bavaria's war. **A truce wipes our battles from the ledger (+79 reads +54 on the field, 0 at the table) and titles nothing.** The road that carries today: **Open Settlement with Austria alone** — a white peace at 50/50 that also ends Bavaria's war — or ~975 gold to any one court." "Propose White Peace **to the whole coalition** (Austria, Britain, Russia)." | The recommendation is structural: `_base_recommendation_and_mission` picks the best **available** row and skips the paradox-shut peace (`diplomacy.py:14098-14143`) — copy alone cannot remove it; the page needs the Austria-alone preview beside it. `war_context_snapshots` (per-action acceptance) is computed on every page open and read by nothing (`:13757-13780`). | F43 (amended: structural), F35, F41, F12 (amended) |
| | the paradox text names "propose an armistice" as a way out | Drop that clause when the armistice itself would be refused (Britain's is: 15 REJECT, M7); add "a truce strikes the score" | `armistice_variant_for` + `calculate_acceptance` of the truce exist | **F67 (new)**, F44 |
| **Talleyrand's counsel and the feasibility card** (Part IV M5) | "My assessment yields 45 — they might counter-offer. The sticking point appears to be deep-seated hostility. We would need 2 diplomatic steps to reach PEACE. 2 DP." "Continue fighting — we can extract more concessions on the battlefield." | "45, and here is why: our demand of 130 gold a turn costs **−24** (a demand this early in a war); their hatred −10; the field +10. **A peace without demands would be accepted (75).** Bavaria's war bars the send; the table with Austria alone carries. The send costs 3 DP." "Another victory adds nothing — the battle score is full (15/15); only Vienna or time moves this court." | `context.acceptance_score`, `largest_obstacle`, `steps_to_goal` are in the payload (`diplomatic_dialogue.py:2086-2095`) and unread (`proposal_confirm_popup.gd:1791-1810`); the components and caps exist in `calculate_acceptance` and `calculate_war_score(return_components=True)` | F40 (amended), F10, F34 (amended: one chokepoint before the `match`, plus the re-open road), F43 |
| **The settlement table** (Part IV M4, M6) | "France vs Britain + Austria + Russia"; "Blocker: Settlement legitimacy — … not every court consents"; "Austria will not sign … until that court is eased"; "Press Austria alone … 3 DP"; "Every covered court has been beaten"; "White Peace — no terms" over "Vienna stays ours"; "Consulted ally: Bavaria"; "More generous" | "**The whole coalition's peace** — the table reads the three courts' mean (17); every court must reach 50." "A white peace is charged −10 while the mean is under 20; **Britain and Russia sit at 0 because France has not fought them.** Three roads carry: drop them (Austria alone), pay one court ~975, or return Vienna (+35 to every court)." "**Status quo as held**: Bohemia, Tyrol and Vienna stay French by this treaty." "Bavaria — her war with Austria ends in this instrument; consulted, not rewarded." "More generous pays every court 100; one court paid ~975 carries the same." | Every per-court component is in `component_breakdown` (`settlement_baseline.py:2085-2087`; built at `:1845`), rendered only on PROPOSE focus; the status-quo list already walks Bavaria's pair (`settlement_staging.py:4040-4078`) under a heading that names no pair; `legitimacy_sentence` is unstamped by `can_sign` | F37, F26, F33, F35, F36, F43 (amended: "Consulted ally" is standing, not the war's fate) |
| | the offer rows: "Offer Bohemia"; the demand rows: "Take Carniola" | "**Offer Vienna** (returns the capital: +35 on every court)"; "Tyrol **to Bavaria**" | The rows skip capitals (`settlement_baseline.py:534-535`); the payee is hardwired (`settlement_actions.py:1240`) | **F54 (new)**, **F53 (new)** |
| | per-court "White peace" on a carve, a forced alliance, a CS entry | "Prussia cedes Posen to the Duchy of Warsaw" / "Prussia enters the Continental System" | `direction_summary` reads only cessions and gold (`settlement_baseline.py:1791-1830`) | **F72 (new)** |
| **The armistice letter** (Part IV M7) | Above the fold: "Proposes: Armistice … Assessment: GENEROUS … War score: 52 (Territory +10, Battle +15, Decisive +10, Ticking −4)"; below: the −60 rule, −65 projected; envoy list "Austria — Armistice Losing" | Lead with the cost: "**A five-turn truce.** It strikes our war score (+52 → 0), titles nothing, and ends in peace only if relations reach −60 — they will reach −65. Bavaria stays at war. **Austria would accept a peace now (75).**" The envoy list: "Austria — proposes a truce (she is losing)." The breakdown adds Campaign +6 and Blood +15 so it sums. | `armistice_mechanics.display_lines` and `clients_following` exist in the snapshot; the breakdown's five keys are the **backend's** (`build_war_context_snapshot`, `diplomacy.py:4888-4894`), not the client's; the raw key is `dispatch.py:4621-4631` | F38, F39 (amended: backend-first), F44, F45, F46 (layout, UXR-4) |
| **The truce** (Part IV M8) | "Austria 5t — on course to collapse back to war unless relations heal"; the wizard sells Improve Relations two rows away | "Unless relations reach −60 — **one turn of Improve Relations (+8) does it** (−65 → −57). The score is struck: a peace signed now would be judged at 0. A truce that lapses into peace **titles nothing you hold**." | `armistice_projected_relation` rides the row unread (`war_status.py:662`); the mission's +8 and the −60 line are on the same page; the signed/unsigned rule is `game_end.py:110-117` | F44 (amended), F17 → D |
| | "The armistice with Austria holds for 3 more turns" — after a ratified PEACE | "Our peace with Austria is fresh: no war may be declared on her for 3 turns." | The fresh-peace floor is written to `armistice_cooldowns` (`settlement_ratify.py:40-66`) and worded as an armistice (`diplomatic_executor.py:2630`) | **F73 (new)** |
| **The AI's settlement letter** (M4, M5, M6) | Rail: "Britain has offered terms to settle France vs Britain. Asking 2,980 gold."; the letter names the leader; a carve rides unannounced | "Britain, **for Britain and Prussia**, offers terms: France pays 2,980 to Britain; **Prussia's war ends with it**." "… and erects the **Duchy of Normandy** out of France." The letter shows each covered court's own score and whether it signs on its own account or because the leader is paid. | The covered list is on the offer; the rail builds from `amount` alone (`turn_manager.py:951-979`); the popup's `_terms` register routes the carve (`settlement_offers.py:2762-2790`) | **F78 (new)**, **F65 (new)**, F76 (new: "Peace Treaty" for a harsh peace) |
| **The Congress** (M7) | Britain "SHUT OUT", no price; the Imperial Peace proclaimed with Britain at war | "Shut out of the Continent — and still at war. Her letter comes on her own clock (exhaustion N of 80); Request Terms asks for it now." | `price()` returns no lever for a SATISFIED stance (`congress.py:1426-1427`); `request_terms_state` is on the war row and no Congress surface reads it | **F79 (new)** |

**One rule for all of them.** Where a mean decides, say it is a mean and show the three
numbers. Where a road is refused, say which clause and name a road that carries. Where a
clock decides, print the turn. Where a peace titles or does not title, say so at the button.

## 42. What is still unmeasured

| Behaviour | Why it matters | Status |
|---|---|---|
| **A skilled France** — a script that keeps attacking through Austerlitz and takes Vienna by turn 5–6, on five seeds and five policies | Every "per seed" result in Parts II–III about France's own peace was read on a France that stops attacking at turn 13 (`commanded_full40.json`); D, G, E and F9 were invisible to it | **Unmeasured.** The first instrument S13e's balance rows need. |
| **The lever probe, re-run with the recalculation** | `calculate_acceptance` reads the stored score (`diplomacy.py:8007`); Part II §11's zeros for victories may be the probe's, not the game's | **Unmeasured.** |
| **France's own cost of war per turn** (the Charges, manpower, the marshals' temper) and the turn a stalemate starts to hurt a middling player | Without a measured cost there is no pressure to sign and every peace is a default | **Unmeasured.** |
| **The AI declaring the second war** (Prussia on France while Austria fights) and how it ends | The player's declaration folds into the live war (**F66**); only an AI declaration opens the 1806 shape | **Unmeasured** (Prussia never attacked in 50 turns on M6's arms). |
| **Peace durability against the terms signed** — how long a harsh peace holds against a mild one | Pressburg bred 1809, Tilsit held five years; the game's Tilsit lasted five turns (M2) | **Unmeasured** beyond one board. |
| **A client whose lord is at peace with its enemy** (the F30 road) | The one case with no exit on any road | **Unmeasured** (read only). |
| **Peace between AI courts with France as broker** (the AI-5c offer) | Part III §23's AI–AI exits never run inside France's instance | **Unmeasured.** |
| **The Congress with Britain beaten at sea** | M7 shows the Congress has nothing to say to a Britain that is SHUT OUT and at war | **Unmeasured** (needs a fleet arm). |
| **The Continental System at the notch** (closure 10 → 11 of 26 on the user's board) | The one fleetless lever on Britain; it cancels itself under the Royal Navy's blockade (**F64**) | Read, not driven. |
| **France losing badly** (the 1814 mirror) | Part III's "losing is cheap and quick" | **Measured — M5, below.** |
| **The two-front coalition** (Prussia's war beside Austria's) | The Tilsit sequence | **Measured — M6, below.** |
| Peace after the Congress; client and vassal peace; the Tilsit clause | — | Measured lightly — M7, M8, below. |

**M5 — France losing badly** (seeds ulm and jena passive, historical under the world-burns
script; every letter refused; per seed, not a law). Paris fell to Britain at turn 15 (ulm)
and 27 (jena); the Emperor was taken at turn 34 and 30; the Fall came at turn 38 (ulm, "reduced
to Corsica alone"), 35 (jena) and 23 (historical, by the captivity clock). P8 fired 5–7 times
per seed once a court passed +40 — Britain first at turn 20 on ulm (five turns after Paris
fell), Austria only once it held the Emperor (the captive −15 is what crosses 40). Every
harsh letter was **one gold lump**: 349 to 1,818 gold, and the settlement letter's ask fell
2,543 (t11) → 363 (t32) on the rail as France fell 26 → 1 provinces (872 at t37, rising again), because both channels price to the payer's
purse. The settlement letter carved the Duchy of Normandy from the turn Normandy fell, and the
rail announced it as "Asking N gold" (**F65**). Nothing resembled Paris 1814 or Tilsit on
Prussia. The coalition **dissolved for low threat while its members held Paris** (ulm t24,
threat 15; jena t23, threat 19; **F77**). The AI's score stalled at 23–49 while holding 10–13
French home provinces because France's own `defense` ticking gave France +25 against each
occupier and the territory cap bites at eight provinces — the loser's shield (§36 row 8).

**M6 — the two-front coalition** (seed historical, the Jena road: France declares on Prussia
at turn 1 while at war with Austria, Britain and Russia; two arms, 25 loops each). France's
declaration **joined war_1** — the coalition's instance, led by Britain, labelled "France vs
Britain" — while the same pair declared by Prussia would open war_2 (`settlement_helpers.py:704-733`;
4 of 4 French declarations reused, 3 of 3 AI declarations created; **F66**). Prussia was in
the coalition's war and **excluded from the coalition** (`coalition.py:1587`), so ungated by
every break-ranks arm. On the accept arm Britain's letter at turn 13 covered Britain and
Prussia, had France pay Britain 2,980 gold, and **signed away Prussia's war while Prussia was
winning** (France −37, Lannes a prisoner): Prussia's row read 59/50 only through the credit
for gold paid to Britain (**F50**). Britain then left the war and the instance's
`defender_leader` stayed "Britain" for twelve turns (t14–t25): the settlement producer refused the
war ("opposing_leader_side_mismatch" at t14, t16 and t18) while Austria and Russia were both at war, t16–t20 (**F51**).
There was no paradox on the Prussian front (the paradox reads ALLIANCE partners; France's
co-belligerents against Prussia were clients, and Spain and Bavaria were asked and declined) —
Part I's F1 is the boot's Bavaria–Austria war, not a general rule. On a synthetic Berlin-held
board Prussia's own letter was **silent below about −72 at every war age** (the honest peace's
fixed band of terms never scales with the score; the send floor recovers 0.35 a point against
the 0.65 the war-score term loses) — F9's band is permanent, not young-war (F9 amended).

**M7 — peace after the Congress** (`fixture_ge3_pressburg.json`, turn 28, France at war with
Britain alone). Britain's letter — a bare peace — arrived at the end of turn 28 on every arm,
Congress or no Congress (the no-summons control received the identical letter on the identical
turn): the Congress had **no part** in Britain's peace. The France–Britain pair read 0 in every
component, blockade included, with 20 of 26 continental ports closed, because the Royal Navy's
posture and France's closure credit both sides one turn every turn (**F64**). The paradox
refusal's own way out — "propose an armistice" — was refused by Britain (15; **F67**). The
Imperial Peace was proclaimed with Britain SHUT OUT and at war, and in the same end turn a new
coalition declared (**F79**, **F80**).

**M8 — clients and the Continental System.** A client's pair follows the lord on six roads
(bilateral, table, the exhausted-pair exit, vassalization, truce expiry both ways, the vassal
entry) — Part III's F29 is overstated and is amended to the one real hole, the defected client
(F30). The Tilsit clause on a Prussia whose capital France holds closes **11 → 11 ports**, is
charged −6 harshness and +10 alarm, and costs a member at peace with Britain nothing
(**F68**); the bilateral peace writes **no fresh-peace floor** where the table writes five, and
Prussia re-declared six turns after signing (**F69**).

## 43. New findings

Severity: **D** defect, **I** inconsistency, **L** legibility, **G** design gap, as before.
Rows F49 … F88 are filed with this part in `BUG_FIXES.md` §PC, OPEN, owned by S13e. Design gaps are rulings
(§40), not rows.

| # | Kind | Finding | Evidence |
|---|---|---|---|
| **F49** | D (P1) | **A player pulled into an ally's defensive war has no road to peace.** The table refuses ("Only the war leader can settle this side" — the origin target leads, `settlement_validation.py:1105-1111`), the bilateral is paradox-blocked by the very ally whose war France joined, Austria's letter is silent above her threshold; only a truce remains. France entered with no letter asked. | M3 austerlitz t20–27 |
| **F50** | D (P1) | **The league leader's letter covers and signs away a winning co-belligerent, and pays its indemnity to the leader.** Britain's letter at t13 ended France's war with Prussia (France −37, Lannes a prisoner) for 2,980 gold paid to Britain; Prussia consented through the credit for gold paid to someone else. | M6 accept; `ai_diplomacy.py:4645-4660`, `:4420-4440`; `settlement_scoring.py:1528-1536` |
| **F51** | D (P1) | **After the side leader leaves by a separate peace the instance's leader is never re-seated, and the producer refuses the war for good** (`defender_leader` stale for twelve turns, t14–t25; "opposing_leader_side_mismatch" at t14, t16 and t18 while Austria and Russia were both at war). The elimination path re-seats; the exit path does not. | M6 accept t14–25; `settlement_helpers.py:1095-1135` vs `:1869-1871`; `ai_diplomacy.py:4557-4562` |
| **F52** | D | **The ratifier silently drops a cession whose ceder no longer holds the province** — after the scorer priced it (Austria 73, −10 own losses, −42 harshness) and the review promised it ("Tyrol from Austria to Bavaria"); the confirm then says "Tyrol stays ours". The validator has no controller check. | M1 probe b′; `settlement_ratify.py:352-353`; `settlement_validation.py:1380-1412` |
| **F53** | D | **The guided demand verb hardwires the payee to France**; no allied beneficiary can be named, though the validator (V2) and the ratifier accept and execute Austria → Bavaria. Pressburg's "to Bavaria" is unauthorable. | M1; `settlement_actions.py:1240`, `:1265`, `:1314-1317`, `:1345-1348` |
| **F54** | L | **The offer rows exclude capitals**: "Offer Vienna" never appears, though returning the capital is the largest lever on the board (Austria alone 50 → 100; the full Pressburg trade carries at 73). | M1 probes a2, c′; `settlement_baseline.py:534-535` |
| **F55** | D | **The bilateral harshness is direction-blind**: France *returning* Vienna and Bohemia reads harsher (35 COUNTER) than France *taking* Carniola (61). Even with the paradox lifted the wizard could not price a Pressburg trade. | M1 probe c′; `diplomatic_templates.py:4533-4541`; `diplomacy.py:8261-8268` |
| **F56** | D | **The preview never validates what it scores**: a same-side transfer (France → Bavaria) previews "Will sign 87" and dies at submit with the generic "the terms we staged no longer hold"; a carve of soil France does not hold previews 51/50. Only the guided verbs gate; ratification drops silently. | M1 probe b′ T9b; M2 raw fixture; `settlement_staging.py:2035-2360` (no `validate_settlement_terms` call); `settlement_validation.py:843-913`, `:1398-1412` |
| **F57** | D | **A carve writes no punitive record**: `collect_cessions_from_clauses` counts only `territory_cede`, so Posen carved + Silesia ceded leaves Prussia "beaten, not humiliated" and volte-face-eligible, against the module's own note that a client's partition is the hegemon's act (Tilsit's carves the model). | M2 probe a2; `emergent_designs.py:246`, `:132-141`, `:180-227`, `:72` |
| **F58** | D | **The coalition's declarations are welded into an AI design war's instance**: the instance leader (Austria, "Primacy in Germany") is not the coalition leader (Britain); the league gate reads Austria's exhaustion and score; the war carries Austria's stated reason for a seven-court war. Mirror on historical. | M3; `settlement_helpers.py:685-745`; `ai_diplomacy.py:1602-1643`, `:4377-4390` |
| **F59** | D | **Each truce collapse makes the war new**: `war_start_turns` is re-stamped (the −65 war-age penalty returns for eight turns; the young-war band re-opens) and exhaustion ticks down in the truce (54 → 16), so a war under −60 relations cycles truce → collapse → truce (three in 26 turns) and the league gate reads "at most 9 turns" after 23. | M3 austerlitz; `diplomacy.py:2932-2945`; `coalition.py:246-270` |
| **F60** | I | **Four exchange rates for gold against land.** The scorer's credit prices a province at 35 points = 875 gold; its harshness at 0.3 = 375 gold; the bilateral refuses 500 gold at +80 (27/50) and the table 1,500 gold alone at total victory (21/50) — while Austria's own P1 letter offers 300 gold a turn as a sweetener. | M3 probes; `diplomatic_templates.py:4500-4571`; `settlement_scoring.py:545-550`, `:479-480`; `diplomacy.py:343-356`, `:8268` |
| **F61** | D | **A dictated peace of Schönbrunn's shape cannot carry at any score**: three provinces + an indemnity + the Continental System has raw harshness 2.3 against a total-victory ceiling of 1.0; the penalty caps at −45, own losses at −25; +2/50 with the stored score forced to +80. The tier ladder promises what the scorer cannot pay for. | M3 lever probes; `settlement_scoring.py:479-497`, `:507-514`, `:778-815` |
| **F62** | D | **The gold concession credit is capped per line**: 1,100 gold in one line → Britain alone 46/50 (never carries); 1,000 + 100 in two lines → 50/50, ratified ("3 pairs resolved"); three lines of 1,000 → 100. | M4 driven; `settlement_scoring.py:545-550`, `:1485-1487`; `settlement_validation.py:1318` |
| **F63** | I | **Two aggregations for one war**: the letter's direction and price read the stored side **sum** (47 ≥ 20 → "France decisively winning → Britain pays" 2,819, 40 % of its chest, for Austria's defeat) while the table's tier reads the power-weighted **mean** (17 → white peace, −10). Part I's four war scores are five. | M4 drive c; `ai_diplomacy.py:4685`, `:4424-4431`, `:4229-4249`; `diplomacy.py:3731-3746`; `settlement_scoring.py:337-420` |
| **F64** | D | **The Silver Blockade cancels itself for France against Britain**: the Royal Navy's posture credits Britain and France's ≥ 40 % closure credits France one turn every turn; the differenced component is 0 for ever (8 / 8 after eight turns at 77 % closure). Britain can never reach P1 or the Congress's −40 at sea. | M7, M8; `naval.py:2954-2990`; `diplomacy.py:3598-3610` |
| **F65** | L | **The rail announces a letter that carves the Duchy of Normandy as "Asking N gold"** and nothing else; the popup's register routes the carve, the rail does not. | M5 arms 1–3; `turn_manager.py:951-979`; `settlement_offers.py:2762-2790` |
| **F66** | I | **The fold asymmetry**: a war the player declares on a neutral is attached to France's live war (led, labelled and settled by the coalition's leader) while the same pair declared by the AI opens a fresh instance. The 1806 second war cannot be the player's. | M6 probe; `settlement_helpers.py:704-733`; `diplomacy.py:9299-9306`; `coalition.py:1587` |
| **F67** | D | **The paradox refusal names an armistice way out that the court refuses**: "propose an armistice (a truce carries no contradiction)" — Britain's armistice scores 15 REJECT on the post-Congress board; the redirect is unconditional on the truce's odds. PC-X2's class. | M7a5; `diplomacy.py:5440-5442`; `:3821-3835`; compare `diplomatic_dialogue.py:1312` |
| **F68** | D | **The Tilsit clause is offered, priced and ratified with zero effect** when the joiner's port already counts (Berlin held: "closes 11 → 11 of 26 ports"), still charged −6 harshness and +10 alarm; and its economic arm is void for any member at peace with Britain (a court at PEACE earns no trade), so Prussia's six turns in the System cost Prussia and Britain nothing. | M8; `naval.py:1362-1377`; `diplomacy.py:12176-12188`, `:12344-12368`, `:11142-11148` |
| **F69** | D | **Two floors**: the bilateral peace (including `seek_bilateral_peace`) writes no fresh-peace floor; the table writes five turns. Prussia re-declared war six turns after signing, "shattering the Peace Treaty", with no gate to stop it. | M8 cs_bare2; `world_state.py:12705-12706`; `settlement_ratify.py:48-80`, `:944` |
| **F70** | D | **The hand-off from the table to the bilateral road re-routes an ally's cession and gold to France silently**: Tyrol Austria → Bavaria and 300 gold → Bavaria seed France's demands; only the forced alliance is reported dropped. | table reading; `settlement_staging.py:2490-2590` (`:2548-2551`); `treaty.treaty_clauses_of` |
| **F71** | D | **France's own peace is judged on the stored score of the last advance** (`calculate_acceptance` reads `world.war_scores` raw) while PC-F5 moved the AI's reading to the live field — Golden Rule 5 asks one reading for both chairs; Part II §11's lever table may have read it. | truce reading; `diplomacy.py:8007`; `turn_manager.py:269-280` |
| **F72** | L | **The per-court direction says "White peace" for a package that carves a client, forces an alliance or enrols the court in the Continental System**; it reads only cessions and gold. | M2; `settlement_baseline.py:1791-1830` |
| **F73** | L | **"The armistice with Austria holds for N more turns"** is shown two turns after a ratified PEACE: the settlement writes its fresh-peace floor into `armistice_cooldowns` and the executor words every entry as a truce. | M3 historical t13; `diplomatic_executor.py:2630`; `settlement_ratify.py:40-66` |
| **F74** | D | **The Pressburg break-ranks arm reads "design satisfied" on a court whose active design is unmet**: `_court_design_satisfied` tests `deck[0]` (Redeem Italy), and a dormant acquire entry reads satisfied, so Austria at austerlitz t20–34 (Primacy in Germany active) may break at −30. *To verify the dormancy branch first.* | M3 probe; `agendas.py:610-618`, `:426-441`; `ai_diplomacy.py:1558-1560` |
| **F75** | D | **An ally-held homeland province is not returned at the peace**: Carniola, taken by Austria's ally Britain from Bavaria, stayed British through the t46 peace while Russia's Carniola and Hungary returned on historical — DDB-12's `homeland_returns` skips a home nation inside the holder's bloc and runs on the retention path only. *Which of the two kept Carniola British is to verify.* | M3; `game_end.py:860-880`, `:964-970` |
| **F76** | L | **A P8 harsh peace reaches the mailbox labelled "Peace Treaty"**: the builder maps `harsh_peace` to type `peace` and the display map renders the type. The captor's ransom likewise. | M5; `ai_diplomacy.py:992`; `display_names.py:329` (the `harsh_peace` entry at `:340` is never reached) |
| **F77** | L | **The coalition dissolves for low threat while its members hold Paris** ("Coalition against France has dissolved — Austria, Britain and Russia remain at war with us", France at 7 provinces): the alarm reads France's remaining power, not the war's state. | M5 ulm t24, jena t23; `coalition.py:2444-2447`, `:53` |
| **F78** | L | **The settlement letter's label and rail hide the covered courts**: "Britain has offered terms to settle France vs Britain" for a letter that ends France's own war with Prussia; the petition's refusal text and request-open / warn-sellout claims still carry the leader pair "France vs Britain" on an Austria-only table (SF7-X30 named the petition's own header by coverage). | M6; table reading; `settlement_routes.py:100-105`; `turn_manager.py:977-979`; `treaty.py:535`; `settlement_offers.py:592-607`, `:731`, `:771` |
| **F79** | L | **The Congress offers no lever for the Britain war once Britain is SHUT OUT**: `price()` returns no lever for a SATISFIED stance; the Imperial Peace proclaims "Europe accepts the order" with Britain at war; the working road (accept her letter, Request Terms) is named nowhere on the Congress. | M7; `congress.py:1426-1427`, `:1983-1987`; `war_status.py:1247-1300` |
| **F80** | D | **The Imperial Peace is proclaimed the end turn a new coalition declares war on France**: `hold_conditions` reads only the summoner's own declarations and the alarm; `process_coalition_turn` runs before the Congress tick. | M7a4 t36; `congress.py:1696-1753`; `world_state.py:11716`; `turn_manager.py:663` |
| **F81** | D | **A carried ally gets no reaction and no record of assent**: its contribution episode closes before the reactions run, so it reads `no_standing` and the gratitude / shut-out pass skips it (Bavaria 60 → 60, "Seat at settlement; 75 %" on the review, empty reactions after). | table reading, measured; `settlement_ratify.py:1555-1565` vs `:1660-1690`; `settlement_reactions.py:505-508` |
| **F82** | D | **Breaking an armistice ends the war as an unsigned PEACE** rather than resuming it (`post_break_map` ARMISTICE → PEACE, `cleanup_war_end` with objectives concluded) — a fifth road for the separate peace, with no verdict. *To verify the typed road.* | truce reading; `diplomacy.py:11946-11962` |
| **F83** | D | **Britain's "Continental System lifted" desire has no producer** anywhere in `backend/`, and its template reads backwards ("{from_nation} closes ports to Britain" for a clause named *lifted*) — dead content, or the missing France-to-Britain sweetener. | clients reading; `diplomacy.py:210`; `diplomatic_templates.py:4753`, `:4967` |
| **F84** | L | **The war score's trend is computed on every row and drawn by no surface**: the card has no glyph; the popup assigns `trend` and never prints it. Part I's "71 · rising" was the JSON. | client reading; `war_status.py:289-298`; `war_detail_popup.gd:441` |
| **F85** | D (instrument) | **The staged fixtures carry unplayable state**: `gen_agd_fixture` plants a stored +100 and a six-turn war age (the live board computes 30–37; the first advance stores 34) and pre-resolves the allies' pairs, so the SF-AGD-1 "measured pair" was measured at a score the game cannot produce; `gen_ge3_congress_fixtures` leaves Austria and Russia in war_1's roster at PEACE, so the HUD reads "no score" and the default coverage hard-stops. | M2, M7; `tools/gen_agd_fixture.py:98`, `:111`; `tools/gen_ge3_congress_fixtures.py:98-176` |
| **F86** | D (instrument) | **The driver's `--diplomacy decline` answers the player's own settlement confirms** (`keep_joint_settlement`, `back_out_settlement`), so a scripted `seek_bilateral_peace` never sends under decline; `PLAYTESTING.md`'s "the player's own confirms are never touched" holds for `--decline-from` only. | M8 cs_bare; `tools/playtest_driver.py` answer policy |
| **F87** | D | **AI–AI treaties grant +10 relations at ratification; the player's grant none** — if the +10 lands on an AI–AI armistice the identical −80 truce ends in peace between two AI courts (−70 → −55) and in war for France (−65). *To verify with one driven AI–AI truce.* | truce reading; `world_state.py:13615-13620` |
| **F88** | L | **The war card never says what the beaten court itself would do**: its own threshold, its break-ranks reason and the −70 split are not on the row, so the player cannot read that Austria would sue alone at −50 and is silent in a young war. | client reading; §41 |

**Amendments to filed rows** (recorded on the rows): F9 (the band is permanent below about
−72 on a Berlin-held board, not young-war; two fixes with opposite effects — the armistice
fallback truces the court out of coverage and whitens the leader's letter; a force-sent honest
peace keeps it covered); F12 (`recommendation` **is** rendered; `confidence_level`,
`action_hints` and `war_context_snapshots` are not); F20 (`get_coalition_loyalty_penalty`'s
sign makes a fresh member harder to peace — delete or redefine, do not connect); F27 (confirmed,
narrowed: the −20 fires only for France's **starting** provinces; returning a conquered one is
+35 on every court); F29 (narrowed to the defected client); F32 (a clause on PC-F9's row: the exclusion is
`compute_direct_scores_by_enemy`'s WAR-only scoring, not coverage); F34 (one read before the
`match` covers all fourteen builders; the pending-envoy re-open road never attaches the error);
F37 (the coalition popup draws per-court bars; the card and the table do not); F39 (the five
keys are the backend snapshot's); F40 (`context.acceptance_score` exists, unread); F43 ("Consulted
ally" is standing, not the war's fate; the recommendation is structural); F44 (an expiry peace
titles nothing — say it).

## 44. What this means for the rulings — the recommended order

1. **C, with B folded in** — the leader's peace is common to its side; the ally is a named beneficiary with a bill; one carry-in set, one consent read, one verdict. Build it on the table's chassis; the wizard reads it.
2. **D** — the truce freezes the ledger and the war's age, titles when signed, and ends in a dictated peace when the loser's hope has died, a courted one otherwise.
3. **I (new)** — the AI may dictate what the player may; refusals ratchet; indemnities are priced to the war; refusing a peace costs France something on screen.
4. **E, with F23** — each court on its own war, a stake floor instead of a veto, a payment to the court paid, the AI's letter scored as the player's.
5. **H** — keep the clock; make it of finance, occupation and subsidy; never reset it by a truce; show it with a forecast.
6. **G** — keep the caps; decay then cap; a ticking that can fall; decide the loser's shield; show the fill.
7. **J (new)** — the war named by its stake; a compensation clause for the moderate peace; declared and composed terms; the coalition's bond priced.
8. **F** — unchanged; measure reactivity, not variance.

**For S13e.** The three P1s (F49, F50, F51) go in after PC-F9. Then the client's lies at the
peace moment (F48, F34, F67, F78, F65, F73, F76), the table's authoring holes (F53, F54, F56,
F52, F70, F62), the two scores (F63, F71, F60, F55, F61), the truce's clocks (F59, F69, F82), the sea (F64,
F68), the coalition's shape (F58, F66, F77, F79, F80), the AI's memory (F57, F81, F74, F75,
F83), the small lies (F72, F84, F88) and the instruments (F85, F86, F87). S13e is now three
parts, sized at its head; nothing moves ahead of it.

## 45. Evidence for Part V

| Claim | Source |
|---|---|
| The five histories: dates, signatories, allies, terms, motives | the historians' structured accounts and their fact-checks (scratch `pv/results/history_*.json`, `check_*.json`); primary texts: Pressburg (napoleon.org French text), Tilsit (Wikisource; napoleon.org armistice text), Schönbrunn (Wikisource; De Clercq via the Napoleon Series), Lunéville and Amiens (napoleon.org; Wikisource), the 1814 convention and treaty (Wikisource; Hertslet 1875); secondary: Webster 1919 for Chaumont's secret articles, Petre 1912 for Pläswitz |
| The five games | wikis, defines and patch notes: eu4/ck3/hoi4/vic3.paradoxwikis.com, wiki.totalwar.com; dev diaries where reachable; player threads named by id in `pv/results/game_*.json` and corrected in `check_*.json` |
| Every code claim | read at master `ae9ba8df`; the P1 and P2 lines re-read by hand before filing (`settlement_helpers.py:704-733`, `:1095-1135`; `ai_diplomacy.py:4555-4565`, `:4377-4392`, `:4640-4665`; `settlement_validation.py:1105-1111`; `settlement_baseline.py:534-535`; `settlement_scoring.py:1478-1495`; `settlement_ratify.py:345-358`; `turn_manager.py:948-982`; `settlement_actions.py:1236-1244`; `settlement_staging.py:2545-2556`; `diplomacy.py:11940-11965`, `:2930-2946`, `:8003-8016`, `:12170-12190`; `naval.py:2954-2990`; `coalition.py:2440-2450`; `world_state.py:12700-12710`, `:13455-13470`; `emergent_designs.py:244-250`; `agendas.py:606-620`) |
| M1 Pressburg | `pv/m1_pressburg/`: `probe_a_table.json`, `probe_a2_trade_shapes_vienna_held.json`, `probe_b_ratify_pressburg.json`, `probe_c_suggestions_review.json`; drives `runs/m1_d1_white_austria_alone/`, `runs/m1_d2_trade_shape/` (digests, saves t1–t13) |
| M2 Tilsit | `pv/m2_tilsit/`: `probe_a_*`, `probe_a2_real_score.txt`, `probe_c_russia.txt`, `probe_d_after_peace.txt`; drives `runs/tilsit_base*`, `v1b_table_carve_only`, `v2_bilateral_cs`, `v3_bilateral_fa`, `v4_table_fa_only` |
| M3 Schönbrunn | `pv/m3_schoenbrunn/`: `runs/m3_austerlitz*`, `m3_historical*` (40 loops + 24-loop continuations; saves every two turns from 20); `probe_wars*.json`, `probe_table*.json`, `probe_bilateral_austerlitz_t34.json` |
| M4 Amiens / Lunéville | `pv/m4_amiens/`: `probe_ab_*`, `probe_b2_output.txt`, `probe_twoclause_output.txt`; drives `c_britain_letter_decline_settle`, `b_britain_alone_*`, `b_austria_alone_white_copy`, `seq_luneville_then_amiens`, `d_vienna_held_blockade_accrual` |
| M5 France losing | `pv/m5_france_losing/`: `runs/arm1_ulm_passive`, `arm2_world_burns`, `arm3_jena_passive` (saves every five turns to the Fall); `probe_arm*.json`, `probe_emit.json`, `summary_*.txt` |
| M6 two fronts | `pv/m6_two_fronts/`: `runs/m6_decline`, `m6_accept` (saves t1–t25); `probe_saves_*.txt`, `probe_instances.txt`, `probe_peace.txt`, `probe_table2.txt`, `probe3.txt`, `M6_SUMMARY.md` |
| M7 post-Congress | `pv/m7_post_congress/`: `runs/m7a_congress`, `m7a2_nosummon_accept`, `m7a3_congress_decline`, `m7a4_congress_refuse_britain`, `m7a5_request_terms`; `probe_b_out.json` … `probe_f_out.json` |
| M8 clients and the System | `pv/m8_clients_cs/`: `runs/tilsit_a`, `truce_austria`, `cs_bare2`, `cs_gold2`; `probe_states_*.txt`, `probe_cs_*.txt`, `probe_bilateral.txt` |
| The code readings and the challenges | `pv/results/code_*.json`, `challenge_*.json` |

Scratch is not committed. To re-derive a measurement: copy the two turn-6 saves and the
fixtures into a scratch folder; run `tools/playtest_driver.py --from-save <copy> --script
<json> --turns N --diplomacy … --settlement … --save-at 1,2,…` with `--out` under the scratch
folder (the driver sandboxes `INK_IRON_SAVE_DIR` there); the table's own clicks are `@`
lines (`settlement_cover_drop`, `settlement_demand_add`, `submit_settlement_for_review`,
`confirm_settlement`, `seek_bilateral_peace`). For a read-only probe set `LLM_MODE=mock`,
`SOVEREIGN_SEED=historical` and `INK_IRON_SAVE_DIR` before any backend import, load a save
with `backend.save_manager.load_game`, and read `calculate_war_score`, `get_war_score_for`,
`calculate_acceptance`, `treaty.can_sign(at_send=True)`, `effective_peace_threshold`,
`coalition_break_ranks_reason`, `process_diplomatic_phase` (on a fresh load) and
`settlement_staging.build_settlement_preview(covered_enemy_participants=[…])`. Never import
`backend.main` in a probe.

## 46. The rulings, decided (October 16, 2026, under the user's delegation)

> The user's words after Part V landed: *"make all decisions and make this work next before rest of
> work commit and push doc"*, and *"we want to make sure tallyrand recs work better of course and
> arent just set in stone and boring etc"*. So every ruling below is **decided**, not recommended;
> **S13e is the next work ahead of everything else** (S13c parts 2–4 and S13b part 4 follow it); and
> a ninth ruling, **K**, makes Talleyrand's counsel alive. Where §40 left a choice open, the rule
> applied is the user's standing one — the historically fuller option with its real cost named —
> under Golden Rules 5 (one executor for both chairs), 6 (the LLM never touches mechanics), 9 (no
> open-ended deferral) and 10 (the sibling sweep). Nothing is left hanging: each ruling has a build
> row (`BUG_FIXES.md` §PC, PC-R1 … R8), a part of S13e, and a behaviour test.

| Ruling | Decided | The cost accepted | Lands in | Row |
|---|---|---|---|---|
| **B** | **Folded into C.** One verdict for France's separate peace on every road: *allowed, priced, and the leader's peace is common to its side.* The HARD_STOP at `diplomacy.py:5550` becomes the WARNING its two siblings already are (`:5514`, `:5524`), priced by `apply_separate_peace_penalties` (`:5122-5141`). **The owning spec is `COALITION_SPEC.md` §6a** (the separate peace as the primary coalition-breaking verb, priced); `BILATERAL_PEACE_HARDENING_SPEC.md` §10.1's borrowed `commitment_paradox` stop is retired for peace-making and stays for the alliance it was written for. | The DD-1 sign-ability sweep and the fuzzer re-run (A = 0, B = 0); PC-F1's word pins re-seated; the copy of F35, F36 and F43 falls out of the predicate. | S13e part 1 | PC-R1 |
| **C** | **The leader stipulates for its allies; the ally is a beneficiary with a bill** (§40 C, items 1–5). *The beneficiary's rate, decided:* a cession to an allied beneficiary is priced to the ceding court at the **same** harshness as a cession to France — Austria lost Tyrol either way — and its credit goes to the beneficiary's standing and satisfies its petition. The moderate Pressburg (Salzburg for Tyrol) is J's compensation clause, not a discount here; until J lands, the Pressburg that carries is the harsh one, as in 1805. | 1.5–2 sessions; `BASELINE_SERIES` moves wherever the AI's P1 letter gains coverage — attributed, never re-pinned blind. | S13e part 1 (the predicate, the carry-in, the consent read, the words, F53's `to`); part 2 (the bill and the two Pressburgs' line) | PC-R1 |
| **D** | **The truce freezes the ledger and the war's age, and ends in a dictated peace when the loser's hope has died** (§40 D, items 1–4). *The −70 split, decided:* P1 keeps the peace below −70 (F9's fallback keeps the court covered); between −50 and −70 the AI asks a truce **only while hope is alive**, otherwise it sends the peace letter at I's terms. *Hope is a three-term predicate* read from stores that exist: another league member not yet spent (`coalition.war_exhaustion`), a subsidy flowing to the court (`_process_british_subsidy`'s recipients), the victor's exhaustion past the loser's. The truce's letter says what it keeps ("the ledger stands"). | One session plus the words (F44, `armistice_mechanics.display_lines`); the series moves on every AI truce (attributed). The surrender-in-waiting risk is met by the hope test, not by moving the split. | S13e part 2 | PC-R2 |
| **I** | **The AI may dictate what the player may** (§40 I, items 1–5): the player's clause types priced by the player's scorer (GR5); the ratchet on refusal; the indemnity priced to the war (a lump plus a stream, provinces held until paid); refusal costs France; the regime arm. *The balance pin, decided:* the ulm arm (France loses) is the acceptance test — the first dictated letter after Paris falls carries a province or a client, never a gold lump alone, and its ask does not fall as France falls. | 1.5 sessions; the losing campaigns' series move (attributed); the Normandy rail line (F65). | S13e part 2 | PC-R3 |
| **E** | **Each court on its own war, a stake floor, a payment to the court paid** (§40 E, items 1–5). *Decided:* the tier legitimacy reads the court's **own** tier, so the −10 white-peace charge stops biting a victor in Vienna; the stake floor is the existing `CONSULT_MATERIAL_SHARE_THRESHOLD` (0.10, `war_contribution.py:88`) — one ladder for both sides; the gold cap binds per package (F62). | One session; seven test files reference the concession credit. | S13e part 3 | PC-R4 |
| **H** | **Keep the +8 clock; make it of finance, occupation and subsidy; never reset by a truce; show it** (§40 H). *The numbers, decided:* occupation **+1** a turn per own home province the enemy holds (the defender's ticking already counts them); subsidy **−2** a turn to the recipient and **+2** to the paymaster while it flows; finance **+2** a turn while the chest is under one turn of upkeep. The league gate reads the live rate, not the constant (`ai_diplomacy.py:1637-1638`); the components ride the war popup (F42). | One session; the series moves (attributed). | S13e part 3 | PC-R5 |
| **G** | **Keep the caps; decay then cap; a ticking that can fall; the fill shown** (§40 G). *The shield, decided:* the `defense` ticking **stops accruing for a court whose capital the enemy holds** — a court without its capital is not "still fighting" its own ground; it resumes when the capital is regained. The fill is shown per component ("Battle 15/15 — full"). | Half a session; every ±100 literal re-read (P1 −40/−70, P8 40, break-ranks −50, the Congress −40, the exhausted-pair band 15). | S13e part 3 | PC-R6 |
| **J** | **Built, in two halves.** *(i) The stake named:* the war's purpose is its title on every surface (F41's class) and the thing the table titles. *(ii) The compensation clause* (`territory_compensate`: the loser paid in a third party's province, or its design pointed elsewhere — Salzburg at Pressburg; Austria's authored Eastern Question) and composed terms at the table (declared goals plus composable articles); the ally's bond priced. The moderate Pressburg exists only with (ii). | Two sessions; a clause type, a title, a subsidy term; touches every settlement spec. | S13e part 4 — (i) first; (ii) sized at the part's head and, if it does not fit, it **heads S14** (named here, not deferred: PC-R7 stays OPEN until (ii) lands) | PC-R7 |
| **F** | **Unchanged**: historical by default, the opt-in roll as today. What the earlier parts wanted was **reactivity** — a court's answer moving when a lever moves — and E, G, H and I each add a lever; §44's reactivity measure (six of ten levers moving nothing) is re-run as part 4's closing read. | None. | the re-read rides part 4 | — |
| **K (new)** | **Talleyrand's counsel is alive** — a reading of the live board, ranked over the roads that actually carry, explaining itself in one line, varied in his register, with his own mind said honestly and scored afterwards. Design below. | One session; the wizard's fixed strings become composed lines (their pins re-seated); GR6 holds — text from numbers, never numbers from text. | S13e part 1 | PC-R8 |

### K — Talleyrand's counsel, alive

**What it is today.** `_base_recommendation_and_mission` (`diplomacy.py:14098-14175`) picks the best
*available* `propose_*` row by `likelihood_score` at or above 40 and prints one fixed sentence,
"Talleyrand recommends: {display name}"; below 40 it prints one of four fixed strings. It never says
why, never names the number, and can name a road whose own button is refused (F35); the armistice on
Austria's page is recommended because the paradox shut the peace row, not because a truce serves
France (F43). The per-action acceptance snapshots it could read (`war_context_snapshots`, computed on
every wizard open, `:13757-13780`) are read by nothing; `confidence_level` and `action_hints` are
never rendered (F12); the feasibility card carries `acceptance_score`, `largest_obstacle` and
`steps_to_goal` unread (`diplomatic_dialogue.py:2086-2095`, F40). The client prints the one string in
gold (`diplomacy_wizard.gd:717`, `:766-767`). The only variety is IQ-6's volte-face sentence appended
after it (`:14077-14097`). The counsel is set in stone because it is a lookup, not a reading.

**Decided.**

1. **A reading, not a lookup.** The counsel ranks every road open on the page by what it would do
   today, from the game's own dry-runs: the bilateral send (`calculate_acceptance` with its
   components), the table with this court alone and the table whole (`build_settlement_preview` —
   the Austria-alone preview §41 asks for), a truce (what it strikes, after D), a mission (IQ-4's
   pricing, which exists), and a battle — only where the battle component is not full
   (`calculate_war_score(return_components=True)`). It names the best road's number, the one term
   that would flip the verdict (the largest obstacle among the components), and the trade the road
   costs: standing for a separate peace, the ledger for a truce, DP for a mission.
2. **Never a road its button refuses.** The ranked set is the rows with `available=True` whose
   dry-run carries or names its cure; a shut row is named as shut with the predicate's own reason.
   After C there is no shut peace row, only a priced one, and the price is said.
3. **Varied, in his register.** Lines are composed from authored pools keyed by situation —
   winning, losing, stalemate; the court's statecraft; a league in being; a truce running; a clock
   near its end — in the Voice Bible's Talleyrand register (urbane, ironic, arithmetic with manners,
   "Sire", never enthusiastic, never a battlefield metaphor), and every line carries its figures. A
   per-court memory of the last line sent forbids a repeat while the situation is unchanged; a
   changed situation changes the line. The pools are content in the `TALLEYRAND_COMMENTARY` shape
   (`diplomatic_templates.py:3352`), reviewed under the Bible's process.
4. **His own mind, honestly.** Talleyrand already has preferences the game enacts — the
   pre-proposal objection, the drafting pushback, the pen-nudge personality
   (`diplomatic_defiance.py:519`, `:791`, `:986`). The counsel says them: he may prefer the moderate
   road and say why ("I would not take Tyrol, Sire; it buys a second war in four years") while the
   numbers stay the scorer's. The preference is derived from the stores his objection reads
   (harshness, the volte-face door, the Revanche seam), so it is character, not chance. When the
   Emperor overrides him, the dispatch's override note (`get_override_dispatch_note`, `:755-790`)
   already says who was right; it gains a running count ("twice right, once wrong this campaign") so
   the player learns how far to trust him. GR6: no LLM in the loop; every sentence is deterministic
   text from deterministic numbers; `SOVEREIGN_SEED=historical` reproduces it byte for byte.
5. **One builder, every surface.** The wizard's recommendation, the feasibility card's verdict and
   the table's counsel ("Press Austria alone", F35) read one ranked set, so they cannot disagree.

**Done when** (`tests/test_pc_rulings.py::TestPCR8`): (a) on the two turn-6 boards the recommended
road's button is enabled and its dry-run carries, or the line says none carries and names the flip
term; (b) where the paradox is priced the line names the price and never "propose an armistice" as
the way out when the truce itself is refused (F67); (c) variety — across the boot's courts and 20
driven turns the same situation never yields the same line twice in a row, and every line carries at
least one figure from the dry-run; (d) GR6 — the line is a pure function of the dry-run dict (a
property test over shuffled inputs); (e) the Part IV M3 and M5 frames re-shot read the new counsel.

### S13e, re-sized: four parts, one session each, in this order

| Part | Builds | Rows | Done when |
|---|---|---|---|
| **1 — the one verdict and the counsel** | PC-R1 (i)–(iv): the predicate, the carry-in, the consent read, the words, F53's `to`; PC-R8 (K) | the P1s PC-F9, F49, F50, F51; the client's lies F48, F34, F67, F78, F65, F73, F76, F37; the counsel's rows F12, F35, F40, F43, F10, F25, F88 | Austria alone signs from the wizard on the Vienna-held board with the price said; no screen says the opposite of the button beside it; K's five pins |
| **2 — the truce and the dictated peace** | PC-R2 (D); PC-R3 (I); PC-R1 (v) the bill and the two Pressburgs | F59, F69, F82, F44 and F17/F18's class; the table's authoring holes F53, F54, F56, F52, F70, F62; F13, F22 | a truce keeps the ledger and the war's age on austerlitz; the Pressburg trade is authorable from the rows (Tyrol **to Bavaria**; Offer Vienna) and ratifies; the AI's first dictated letter on ulm carries a province |
| **3 — the scores and the clock** | PC-R4 (E); PC-R5 (H); PC-R6 (G) | F23, F63, F71, F60, F55, F61, F20; F42, F31; F27, F26, F38, F39, F84; the coalition's shape F58, F66, F77, F79, F80; the sea F64, F68 | Britain alone reads 6/50 beside Austria's 79 on one table; the clock's components on the war popup; the shield down with Vienna held; the blockade credits France |
| **4 — the stake, the memory, the instruments** | PC-R7 (J, (i) then (ii)); F's reactivity re-read | F41, F72; the AI's memory F57, F81, F74, F75, F83; F28, F29, F30, F33; F11, F14, F45; the instruments F85, F86, F87 | "War for Bohemia" on every surface; a carve writes the punitive record; the staged fixtures regenerated by a drive; the reactivity read — ten levers, each moving at least one court's answer |

**S13e's done-when as a whole:** 0 OPEN §PC rows; the Part IV frames re-shot on the two turn-6
boards read so that every peace moment names the road that carries and its price; the three Part V
replays pass as tests — the Pressburg trade authorable and ratified with Tyrol to Bavaria, a truce
that keeps the ledger, a dictated peace carrying a province on ulm. Each part ends with its sibling
sweep and a series attribution where a fix reaches the AI. **Then** S13c part 2 (CC-3), S13c parts
3–4, S13b part 4, S14 — unchanged in order.

**Not decided here, because it is not this report's:** UXR-4 (the user's eyes at 5120×1440, S15,
with PC-F46 and F47) and the code-signing certificate before S15.
