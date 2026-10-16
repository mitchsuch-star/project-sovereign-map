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
> findings F34 … F48.

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
