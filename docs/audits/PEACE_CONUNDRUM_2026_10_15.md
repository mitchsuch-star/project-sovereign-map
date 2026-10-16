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
> AI courts; findings F23 … F33.

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

The client study (what the screens show at the peace moments) was not run: it needs the
Godot client driven against a spare backend, and is proposed as its own session.

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
