# PLAYTEST — "Try to win the game" (August 16, 2026)

> **Memo of record.** A played France/1805 campaign driven to WIN, 23 world
> turns across four scripted phases on the Mode-A harness. Routing:
> correctness rows → `docs/BUG_FIXES.md` §Win-Attempt Campaign (WIN);
> design questions → `docs/DESIGN_REFINEMENT.md` §Win-Attempt Campaign.
> Digests: `tools/playtest_runs/win-p{1,2,3,4}-*/digest.md` (dev machine).
> Scripts committed: `tools/playtest_scripts/win_campaign_p{1,2,3,4}.json`.
>
> **Brief:** *"DO PLAYTEST TRY TO WIN THE GAME. use new playtest items that
> make it easier, report any bugs and do a review, see if any features are
> bad or missing."*

> **▶ FIX PASS, same day (§7).** The user directed *"make any fixes
> needed including [WIN-D2]"*. **All seven bug rows are FIXED and the
> WIN-D2 design question was RULED and BUILT** as "The Spoils of War".
> ⚠ One routed fix (WIN-H1's production half) was tried and REVERTED
> as a client regression — §7.2 records why, and amends NPC-16.
> Gate record: `DESIGN_REFINEMENT.md` §Win-Attempt Campaign. Suite
> 18,095/3.

---

## 0. The one-paragraph answer

I destroyed the Austrian army at Ulm in a single turn, knocked Austria out
of the war by turn 13, fought Russia to a standstill and took her peace by
turn 21. **France finished with two more provinces than it started with,
a negative income, and no acknowledgement from the game that anything had
been won** — because the 1805 campaign has no victory condition at all, and
because the provinces my victories emptied were walked into by **Bavaria,
my own ally, who finished with six more than she started with — three times
my gain, from my battles.** The war system is excellent. The reward system
it feeds is the gap.

---

## 1. What was run

| Phase | Turns | Script | Outcome |
|---|---|---|---|
| P1 Ulm | 1–6 | `win_campaign_p1.json` | Mack annihilated turn 1; Tyrol taken |
| P2 Vienna | 6–11 | `win_campaign_p2.json` | Vienna unreachable — the ally already held it |
| P3 Settle | 11–16 | `win_campaign_p3.json` | **Austria knocked out (t13)**, peace signed |
| P4 Russia | 16–23 | `win_campaign_p4.json` | 5 battles at Podolia; **Russia peace (t21)**; Ukraine taken |

Seed `historical`, `LLM_MODE=mock`, in-process TestClient, saves sandboxed.
Policies are printed in each digest header; P3/P4 ran `objection=insist`,
`diplomacy=accept` so the campaign could actually press attacks and sign
treaties.

## 2. The scoreboard

| | boot | turn 23 |
|---|---|---|
| **France provinces** | 28 | **30** (+2: Tyrol, Ukraine) |
| **Bavaria provinces** (ally) | 3 | **9** (+6: incl. Vienna, Bohemia, Moravia, Hungary) |
| Austria provinces | 7 | 2, then PEACE |
| France net income | +2,456/turn | **−215/turn** |
| French field strength | 189,000 | 85,806 |
| Wars | 3 (Austria, Russia, Britain) | 1 (Britain, unreachable) |

Ulm, turn 1, three battles in one turn:

```
Ney    lost   878  vs Mack lost 14,334
Davout lost   340  vs Mack lost 17,664
Murat  lost    60  vs Mack lost 18,802
```

Mack lost 50,800 of 52,000 men. France lost 1,278.

---

## 3. What is GOOD (this is not a complaint memo)

These are the things that made the campaign worth playing, and they should
be protected by whatever fixes follow:

1. **The muster/interrupt surface is the best thing in the game.** It names
   who will not march *and the exact order that would fix it*:
   > `WILL NOT — Soult: awaits explicit orders and will NOT march — order
   > 'Soult, support Davout' and he will march`
   > `Kutuzov does not stand alone: at least 1 enemy corps within reach of
   > Podolia would march to him.`
   That is honest availability done properly, and it is what let me lose a
   battle *knowing why*.
2. **The literal doctrine reads beautifully in play.** Soult failed to
   reinforce three consecutive battles — *"Soult, however, was conspicuously
   absent" / "Where was Soult? Lannes held the field alone" / "Davout stood
   alone, Sire. Soult never came."* — and each time the muster had told me
   in advance. Character expressed as mechanics.
3. **The economy bites legibly.** Supply attrition (892 / 874 / 1,112 men a
   turn at Bohemia), occupation cost, Charges of Empire, Rentes and Blockade
   all appear as named ledger lines, and the collapse from +2,456 to −215 is
   fully explained by them.
4. **Battle narration names reinforcements and no-shows**, so a battle is a
   story about which marshals came.
5. **The AI commissions marshals unprompted** — Bagration, Bennigsen (Russia),
   Paget, Shrapnel (Britain) all appeared mid-campaign.
6. Austria's court **sued for peace on its own** while losing, repeatedly.

---

## 4. Bugs found (detail in `BUG_FIXES.md` §WIN)

Four are **harness** defects that had silently degraded every prior
unattended evaluation; three are **game** defects.

> **Status after the §7 fix pass: ALL SEVEN ARE FIXED.** The findings
> below are kept in the words they were found in — including "routed
> OPEN" and "the production half remains open", both of which §7 closed
> — so the record shows what was measured before it shows what was done.

### 4.1 Harness — FIXED this session

- **WIN-H1 (P1) — NPC-16 confirmed, harness half fixed.** An interrupt
  raised during end-turn rides only `strategic_reports[i].requires_input`.
  The driver read only the top-level `pending_interrupt`, so it answered
  nothing and the marshal — then the turn loop — froze. Measured on the
  exact input NPC-16 names: before, `current_turn` stalled at 7; after, the
  run reached 10 and **Napoleon's pursuit resolved and took Swabia on turn
  6**. The Godot client already reads the report list (`main.gd:4218`), so
  the **production half remains open** and a human player is unaffected.
- **WIN-H2 (P1) — the enemy-phase attack counter has always read 0.** The
  verb lives at `row["ai_action"]["action"]` (built at
  `turn_manager.py:964`). PC15-H "fixed" the under-read by reading
  `row["action"]` — a key that does not exist — so **every digest ever
  produced reported "0 attacks" regardless of what happened.** After the
  fix the very next turn read `3 actions, 3 attacks`. ⚠ **Any prior
  conclusion about how often the AI attacks, drawn from a digest, is
  unsupported** — including this campaign's own first two phases.
- **WIN-H3 (P2) — an answer cycle reported a healthy engine as `blocked`.**
  `settlement_confirm` option 1 stages a pair substitute; the chooser's
  `keep_joint_settlement` is *documented* to restore the prior dialogue. Each
  step is correct; together they loop. The run spun **97 popups** and
  finished `blocked`, which reads exactly like an engine hard-lock and is
  not one. I nearly filed it as a P1 against the game. Now: answering one
  surface the same way twice in a post stops the chain and names it.
- **WIN-H4 (P2) — the province scoreboard read `None`** (GET /ledger wraps
  its body under `"ledger"`). Without it a campaign can annihilate an empire
  and never notice its own map did not grow — which is exactly what
  happened here for 16 turns.

### 4.2 Game — routed OPEN

- **WIN-1 (P2) — a peace option is offered that can never succeed.**
  `Talleyrand, propose peace with Austria` drafts terms and offers *"Send as
  suggested"* as the primary option; sending is then refused at execution:
  > *"Making peace with Austria while allied with Bavaria (who is still at
  > war with Austria) creates a diplomatic contradiction."*

  The dialogue is re-presented **identically and indefinitely** — reproduced
  6/6 times in a probe and organically across two courts (Austria t8–t11,
  Britain t15). Non-blocking with a `Reconsider` exit, so it is not a lock,
  but it violates this project's own honest-availability discipline: the
  option should arrive **disabled with its reason stated**, the way the
  vassal-wizard gate rows and the NV-6 naval chips do.
- **WIN-2 (P2) — Talleyrand's commentary contradicts the terms he drafted.**
  The same payload carries `demands: [{gold_per_turn: 187}]` and
  `talleyrand_commentary: "Border territory provides strategic depth. A
  prudent demand."` No territory is demanded. This is the CA9 through-line
  (compute one thing, say another) alive in the peace generator.
- **WIN-3 (P3) — out-of-range refusals name a distance but never a place.**
  *"Lannes cannot reach Mack from Swabia! Range: 1, Distance: 8"* — it never
  says where Mack is, so the player cannot act on it. The project already
  fixed this class for regions (*"Region 'Venetia' not found. Nearby: …"*).

**Not a bug, checked and cleared:** Napoleon's Paris→Artois first step
toward Swabia (Artois and Champagne are both 5 provinces out — a legal
tie, not a pathfinding fault), and the `keep_joint_settlement` no-op above.

---

## 5. The review — features bad or missing

### 5.1 ⛔ There is no victory condition (missing)

`turn_manager._check_victory_conditions` returns
`{"game_over": False}` unconditionally on any Europe world — the
`sandbox_mode` guard is the method's first statement. This is a known,
owned roadmap item (positions 12–13, the Victory & Objectives Pass), so it
is not news; what this campaign adds is **evidence of how it feels**. I
knocked a great power out of the war and signed two peaces, and no surface
anywhere — dispatch, ledger, gazette — treated it as progress toward
anything. There is no score, no objective list, no "what would winning look
like" screen. **This is the single largest missing feature and everything in
§5.2 is downstream of it.**

### 5.2 ⛔ Winning is not rewarded — the ally collects the empire (design)

France annihilated Austria's field army and gained **Tyrol**. Bavaria, who
fought alongside and did none of the decisive fighting, took **Vienna,
Bohemia, Moravia and Hungary**. The mechanism is not a bug: my battles
emptied those provinces of defenders, and the Bavarian AI walked into the
vacuum. But the consequence is that **the player's decisive victories are
converted into an ally's territory**, and there is no lever to prevent it —
no way to claim a province before an ally reaches it, no war-aim reservation,
no post-war partition in the player's favour. Compare the ES-7/estate economy,
which assumes conquest produces spoils to distribute.

### 5.3 Peace freezes your armies where they stand (design)

The moment Russia accepted peace, every eastward move refused:
> *"Cannot enter Podolia — it is controlled by Russia (diplomatic state:
> PEACE). Open borders or higher required."*

Four corps were left deep in the east, bleeding supply attrition, with no
route home but a multi-turn march back through territory that is now
somebody's sovereign soil. Winning the war stranded the army that won it.

### 5.4 The reward economy makes victory unaffordable (balance)

Two rentes cost **1,260 g/turn**. Combined with occupation costs, Charges of
Empire and 30 provinces of infrastructure, net income fell from **+2,456 to
−215** across the campaign. The marshals demanded rewards *because* they
kept winning (the jealousy/expectation systems working as designed), and
paying them is what made France insolvent. The loop currently reads:
win → marshals demand → pay → go broke.

### 5.5 The Emperor cannot reach his own war (design, row NP)

Paris is five provinces from the German front and marshals move one province
a turn. Napoleon left Paris on turn 2 and had still not reached the fighting
by turn 11; **in 23 turns he fought in zero battles.** Row NP's whole kit —
the Presence aura, the Shadow, the Peril — is gated behind a march the map
makes impractical. Worth a design answer (a sovereign movement allowance, a
capital-to-front posting, or starting him forward).

### 5.6 The petition firehose (balance, already known)

Jealousy confrontations fired roughly **once per turn** through phases 1–2
(Murat, Davout, Lannes, Bernadotte, Murat, Soult, Ney…). The tutorial world
was made jealousy-dormant for exactly this reason (TUT-F5 measured five
Soult confrontations in three lesson turns); the main campaign still gets
the full rate. CA9-D3 owns this — this is one more measurement for it.

### 5.7 Casualty exchange ratios are extreme (balance)

Murat lost **60** men while inflicting **18,802** — a 313:1 exchange. Across
Ulm the ratio was 40:1. A concentrated multi-marshal attack against a
weakened defender is currently close to free, which is why the Ulm
envelopment ended the Austrian army in a single turn. Legible and dramatic;
possibly too cheap.

---

## 6. Method notes and honesty

- **Nothing was hand-set.** Every order went through `POST /command`; every
  popup answer is logged in the digest beside the policy that made it.
- **Two of my own findings were wrong and are recorded as such**: the
  Napoleon pathfinding "detour" (a legal tie) and the settlement "hard-lock"
  (my harness oscillating, not the engine). Both were killed by checking
  before filing — the settlement one only after I had already written it up
  as a P1.
- **The AI-attack figures in phases 1–2 are unusable** (WIN-H2). Phase 4's
  are sound, being post-fix.
- No visual pass was taken; the user's own backend was live on 8005
  throughout and the whole campaign ran in-process, touching none of it.
- Harness fixes are pinned by
  `tests/test_playtest_harness_win_campaign_2026_08_16.py` (15 tests).

---

## 7. The fix pass (same day)

User direction: *"make any fixes needed including [WIN-D2 …] Bugs"*.

### 7.1 WIN-D2 — "The Spoils of War" (the design ruling, BUILT)

**Ruled and built at the recommended default under the delegated grant.
Gate record: `DESIGN_REFINEMENT.md` §Win-Attempt Campaign (authoritative).**

The measured moment was not a bug — it was a single allied corps walking
into provinces a French victory had emptied, *while French armies stood
next to them*, with the player holding no lever of any kind. The rule:

> An AI will not take an undefended enemy province out from under a
> **co-belligerent better placed to take it** — a nation allied to it,
> itself at war with that province's owner, with strictly more strength
> adjacent.

`enemy_ai._defers_spoils_to_ally`, one predicate at one call site
(`_find_undefended_capture`), **zero new serialized fields**, behind the
flip lever `SPOILS_DEFERENCE_ACTIVE`. Strictly-greater so it cannot
deadlock; adjacency-scoped so distant allies never block;
co-belligerent-scoped so an enemy massing next door is never a reason to
hold back; symmetric by construction, so an AI defers to another AI
exactly as it defers to France.

**Measured on the campaign's own phase 1, replayed:** allied Bavaria went
from **7 provinces at turn 6 → 3, its boot count**, with Austria's 7 still
on the table. Rejected alternatives (war-aim reservation at declaration;
contribution-weighted post-war partition) are recorded in the gate record
with reasons — each needs new serialized state, new UI and its own gate,
and neither addresses the measured moment.

**Honest limits.** An ally still takes what the player is not placed to
take — Bavaria took Tyrol in the verification run with no French corps
adjacent, and that is the rule working, not failing. And because campaign
runs carry combat RNG that the campaign seed does not pin, a single
before/after pair is **not** proof on its own; the behaviour is pinned by
tests instead, including a both-directions case on the real rung with a
real `WorldState`.

### 7.2 The bug rows

| Row | Fix |
|---|---|
| WIN-H1 | ⚠ **The production half was TRIED AND REVERTED — NPC-16's routed fix is unsafe as written.** `pending_interrupt` is a registered `_post_hud_response_routes` matcher (`main.gd:1360`), and that router runs at `main.gd:1909`, BEFORE the strategic-reports branch at `:2000`, in the same function, and returns. Promoting the key makes the client fire the interrupt popup and **skip the report summary that narrates what every marshal did that turn** — a regression to a working path, in service of an issue that is explicitly P3 for players (the client already derives the interrupt at `main.gd:4218`). The harness half stands and fixes the measured problem. A future one-contract fix must re-order the client's routes or use a key `main.gd` does not match; both options are recorded at the seam |
| WIN-1 | The `execute_proposal` arm arrives `enabled: False` **with its reason**, at the mount seam that already computed the block; modify/adjust/Reconsider stay live so the player is never dead-ended |
| WIN-2 | The commentary tag is re-checked against the FINAL demands after the easing ladder drops territory. Verified live: the same draft now reads *"They have little choice but to accept…"* instead of *"Border territory provides strategic depth."* |
| WIN-3 | The refusal names the place it resolved to — which also makes the NPC-7 misresolution visible instead of silent |

### 7.3 A defect in this session's own first fix

The WIN-H3 cycle guard, as first written, keyed on `(surface, choice)`.
Every dialogue family rides the key `diplomatic_dialogue`, so **"decline a
settlement offer, then decline a proposal" tripped it** and stopped a
chain that was making progress — visible in the very next run as a
spurious `⚠ ANSWER CYCLE` in win-p1 turn 4. The signature now carries the
summary, and non-answers (`(left standing)`, `display-only`) never count.
Pinned by `test_same_answer_to_DIFFERENT_dialogues_is_not_a_cycle`.

### 7.4 Verification

- Suite **18,095 / 3**, ruff clean.
- `BASELINE_SERIES` and M1–M7 **byte-identical without re-record** — a
  fact about the ambient harness (it never places a stronger
  co-belligerent beside an undefended province), *not* proof of safety.
  Stated plainly rather than presented as a green light.
- Pins: `tests/test_win_campaign_fixes_2026_08_16.py` (21) and
  `tests/test_playtest_harness_win_campaign_2026_08_16.py` (17).
- Live-verified over the real `/command` surface: the peace draft's
  disabled arm and corrected commentary (probe), and the phase-1
  province counts (driver).
