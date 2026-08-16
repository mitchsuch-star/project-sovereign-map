# WAR WITHDRAWAL SPEC — "The Road Home"

> **✅ GATE TAKEN AND BUILT August 16, 2026. Gate record + landing record =
> §7a, authoritative where it amends the body.**
> Authored August 16, 2026 from two rulings taken on the win-attempt
> campaign's design rows: **WIN-D3** (*"ending war should send troops back
> to borders with free march orders"*) and **WIN-D5** (*"he can reach from
> Paris, right — we can start him closer"*).
>
> Evidence: `docs/audits/PLAYTEST_WIN_CAMPAIGN_2026_08_16.md` §5.3 and
> §5.5. Rows: `docs/DESIGN_REFINEMENT.md` §Win-Attempt Campaign.
> Code: `backend/game_logic/withdrawal.py`; tests
> `tests/test_win_d3_road_home.py`.

---

## §1 The problem, measured

The turn Russia accepted peace, every eastward order refused:

> *"Cannot enter Podolia — it is controlled by Russia (diplomatic state:
> PEACE). Open borders or higher required."*

Four French corps — Massena, Soult, Davout, Murat — stood deep in the
east on soil that had become sovereign the instant the ink dried. They
could not advance, could not stay supplied (foreign soil feeds nobody
under the D2 "Ally's Table" ruling), and had no route home that did not
cross the same closed frontier. Supply attrition billed them every turn.

**Winning the war stranded the army that won it.** The rule that produced
it is correct — `can_enter_territory` returns False for PEACE and
ARMISTICE, and it should. What is missing is the clause every real peace
treaty carried: *the evacuation corridor*.

## §2 The design in one sentence

When a war ends, the peace grants a **temporary right of transit** home,
and every stranded marshal is handed a **free march order** to take it.

Two halves, deliberately coupled: the right without the orders is a
mechanic nobody notices; the orders without the right are orders that
cannot be obeyed.

---

## §3 Half one — the corridor

### §3.1 Trigger

At the **`set_diplomatic_state` chokepoint**, on any `WAR → non-WAR`
transition between A and B.

That seam and not `cleanup_war_end`: PT-J1 established that typed
conquest-vassalization and the forced-alliance ARMISTICE arm **never
reach** `cleanup_war_end`, and those are exactly the endings most likely
to leave armies parked abroad. One write, every ending.

### §3.2 State

ONE new serialized field, on the `armistice_cooldowns` idiom:

```
world.evacuation_grants: {diplo_key: expiry_turn}
```

Directed is unnecessary — the grant is mutual by construction (both
sides are walking home), and a shared key halves the state.

### §3.3 The predicate

`can_enter_territory` (diplomacy.py, the single movement chokepoint)
gains one arm: a standing evacuation grant for the pair returns True.

**Everything inherits it for free** — all ~25 movement seams, the AI's
18 threaded candidate sites, the strategic-march stall arms — exactly
the way the naval crossing gate propagated. No seam-by-seam threading.

### §3.4 What the corridor is NOT

Pins, each to be written as a falsifiable test:

- **It never permits an attack.** Attacking requires WAR; the pair is at
  peace. The corridor is consulted by the movement predicate only.
- **It never permits a capture.** Marching into a province of a nation
  you are not at war with does not flip it, and must not begin to.
- **It is not OPEN_BORDERS.** It expires, and it exists only because a
  war just ended.
- **It dies instantly if war resumes** — a peace instrument cannot
  outlive the peace.
- **It does not feed the army.** Supply attrition continues, and that is
  the point: the corridor is a road, not a billet. Marching home is
  urgent because standing still costs men.

### §3.5 Duration — derived, not guessed

At the grant, compute for each affected marshal the distance to his
nation's nearest controlled province, take the maximum, add 2 turns of
slack, clamp to 12.

**Then: the corridor stays open while you march, and closes if you
stop.** Each turn, a marshal whose distance-to-home *decreased* refreshes
the grant; an army that sits still lets it lapse.

This is the whole edge-case answer to "what if the timer expires with
troops still inside" — it cannot expire on anyone who is genuinely
walking home, so expiry means loitering, and loitering on foreign soil
after a peace has an obvious consequence (§6). No new player decision,
no arbitrary number doing load-bearing work.

---

## §4 Half two — the free march orders

### §4.1 What is issued

Every marshal standing on soil he now has no right to occupy receives an
automatic strategic **MOVE_TO** order targeting the nearest province his
own nation controls (or an ally's, if that ally grants passage).

- **0 AP.** It is not the player's order; it is the treaty's.
- **It does not consume the order economy** — issuing it must not
  prevent the player from giving that marshal a different order.
- **It is an ordinary order once issued**: visible in the Orders ledger,
  cancellable, overridable. The player who wants to march somewhere else
  simply says so.

### §4.2 Symmetry (GR5)

The ex-enemy's marshals on *our* soil get the same corridor and the same
orders. This is not a player courtesy; it is what ending a war means.
The AI consumes the corridor free (its candidate sites already read
`can_enter_territory`), and the free order gives it the same road home.

### §4.3 What the player sees

One dispatch beat at the peace, naming names and the deadline:

> *"The war with Russia is over, Sire. Four corps stand on Russian soil.
> Berthier has given them the road home — Davout to Moravia, Soult to
> Vienna, Massena and Murat behind them. They have safe passage while
> they march."*

Plus the standing Orders rows, and — on the turn a corps stops moving —
a warning that its passage is lapsing.

---

## §5 Edge cases

| Case | Ruling |
|---|---|
| Marshal already home / on passable soil | No order, no mention. Untouched. |
| **No land route home at all** (cut off behind third-party soil) | No order is issued and the dispatch **says so plainly** — the corps is cut off and passage must be negotiated. v1 does not invent a rescue; it refuses to pretend. Named as the spec's one known gap (§8). |
| Coastal and cut off | The forced-retreat sea-escape (the Corunna arm) already exists; v1 does **not** wire it here. Same gap row. |
| Armistice rather than peace | Identical treatment — both block movement, both strand armies. |
| A new war declared during the corridor | Grant dies at once (§3.4). |
| Vassals / allies of a signatory | Out of scope for v1: the grant is per-pair. Recorded, not hidden. |
| Marshal is fortified / drilling when the peace lands | The order is issued; the existing "unfortify first" rules apply unchanged. He is not teleported out of his own state machine. |

---

## §6 The consequence of loitering

An army that stops marching lets its passage lapse and is once again
standing, illegally, on a sovereign power's soil.

**Recommended v1: it is interned** — removed from the field as a
diplomatic incident, on the seam PC15-1 already built
(`WorldState.destroy_marshal`, with its `fallen_marshals` tombstones and
its three-arm dispatch ladder), and reusing the **"Interned Column"**
concept already homed to the NP exit review by the PC15-D1 ruling.

This is the historically normal outcome and it makes the corridor matter.
It is also the single most severe thing in this design, so it is called
out here rather than buried: **it can lose the player an army if he
ignores three explicit warnings.** If that is judged too harsh at the
gate, the fallback is a stability/relation penalty and a permanently
attrited corps — but *something* must happen, or the corridor is
decorative.

---

## §7 Gate questions

1. **Internment on lapse (§6) — yes, or the softer penalty?**
   *Recommendation: yes, with the warnings.*
2. **Duration model — the self-refreshing corridor (§3.5), or a flat N
   turns?** *Recommendation: self-refreshing; it makes the number
   non-load-bearing.*
3. **Does the corridor also cover the signatory's ALLIES' soil?**
   *Recommendation: no in v1 (per-pair), recorded as a limit.*
4. **§5's cut-off corps: refuse honestly (recommended) or invent a
   rescue?**

---

## §7a GATE RECORD + LANDING RECORD (August 16, 2026) — AUTHORITATIVE

The four §7 questions were delegated to the builder ("yours to take at the
spec's recommended defaults unless you find a reason not to"). **All four
were taken at the recommended default.** No deviation on any gate question.

| Q | Ruling | Note |
|---|---|---|
| 1 | **Internment on lapse — YES**, with the warnings | Through `WorldState.destroy_marshal(cause="interned")`, the ONE PC15-1 removal seam, so it inherits the tombstone, the dispatch ladder and the gazette. Three explicit warnings first, counted by a test. |
| 2 | **Self-refreshing corridor** | And it needs no memory — see the amendment below. |
| 3 | **No — per-pair in v1** | Recorded as a limit, §8. |
| 4 | **Refuse honestly** | A cut-off corps gets no order, the beat says so plainly, and — the corollary the spec did not state — it is never interned either. Refusing to invent a rescue must not become punishing a corps for failing to walk a road that does not exist. |

### Amendments made during the build, each with its reason

1. **§4.1's predicate would have missed the measured case, and is
   replaced.** The spec sends orders to "every marshal standing on soil he
   now has no right to occupy". The four corps of §5.3 were standing on soil
   France had *captured* — their own colour on the map — with the closed
   Russian frontier between them and home. They occupied nothing they had no
   right to, and the spec's own predicate would have left every one of them
   exactly where the playtest found them. The built predicate is **"can he
   reach the body of his own realm at all"**: the home zone is the set of a
   nation's provinces connected to its capital through soil its army may
   legally cross, and a marshal outside it is stranded. This covers the
   spec's shape *and* the measured one.

2. **Slack 2 → 3 turns.** §6 promises "three explicit warnings"; two turns
   of slack only fits two. The number is not load-bearing (see 3), so it is
   sized to the promise the design makes.

3. **The self-refreshing corridor needs no memory of last turn's
   positions.** Expiry is set once to `turn + longest march + slack`, and
   each turn a marshal is checked for VIABILITY rather than against a
   deadline: `surplus = (expiry - turn) - (his distance home)`. A marshal
   who marches closes one province per turn while the clock ticks one turn,
   so his surplus is constant and the corridor cannot expire underneath him;
   a marshal who stands still keeps his distance while the clock runs. That
   is §3.5's behaviour with ONE serialized int and no second field, and
   `surplus` reads directly as "turns of dawdling still affordable".

4. **`_force_retreat_displaced_marshals` is RETIRED** (`diplomacy.py`). The
   March-2026 C1 fix already TELEPORTED marshals home from `cleanup_war_end`
   — the spec did not know it existed. Both cannot run: it intercepted
   precisely the corridor's flagship case, so the player would never once
   have seen the march this slice exists to give him; a silent free
   relocation with no attrition and no decision *is* the invented rescue
   gate Q4 declined; and it never covered the measured defect anyway (it
   keyed on `region.controller == the other signatory`). Its two C1 tests
   are flipped consciously in `tests/test_playtest_2026_03.py`, and a third
   was added showing the corridor covering the case it used to.

5. **The AI needed its own rung — GR5 was otherwise a fiction.** The free
   march order is a `strategic_order`, and `enemy_ai.py` had never read that
   field for anything. The AI would have been handed a road it could not see
   and then interned for not walking it: **measured at three AI corps
   destroyed in a 40-turn ambient run, one of them a single march from its
   own border.** New rung **P1.2 THE ROAD HOME**, below retreat recovery and
   above everything else. After the fix the same run interns nobody.

### Seven defects found by measurement during the build

Each was found by running the thing, not by reading it, and each is now
pinned. The first two are mechanism; the rest are what the player reads.

1. **The grant must be written BEFORE the distances are measured.**
   `distance_home` routes *with* the corridor — it has to — so measuring
   first asked every corps to walk a road that did not exist yet. Every
   corridor-dependent corps was misfiled as cut off, the duration was
   derived from whoever happened *not* to need the corridor, the beat
   announced "0 corps" and then named two, and a peace where every stranded
   corps needed the corridor **wrote no grant at all** — the corridor could
   not open in precisely the case it exists for. Fixed with a provisional
   grant, rolled back if nobody can use it.
2. **A marshal was judged against every grant his nation held**, not the one
   relevant to his road. France holding an older, shorter Austrian corridor
   and a fresh Russian one interned a corps mid-march under the Austrian
   clock. The tick is now organised by marshal, not by grant.
3. **"Stranded" swept up every corps standing legally abroad.** §5's first
   row says a marshal "already home / ON PASSABLE SOIL" is untouched, and
   the first predicate tested only "is he outside the home zone" — which is
   the nation's OWN provinces. The acceptance run had **the Emperor himself,
   at Munich in allied Bavaria, ordered home or interned.** `is_stranded`
   now requires that he has no right to stand where he is, or no road home
   without the treaty.
4. **The lapse warning claimed he had stood still.** *"Marshal Ney has not
   moved from Lithuania"* — about a corps that had marched all turn.
   Nothing tracks movement; the mechanic tracks whether he can still reach
   home in the time left, so that is what the sentence says now.
5. **A marshal was interned having never been warned on screen.** The
   dispatch shows ONE headline, so per-marshal beats meant only the luckiest
   corps was ever named — Davout was destroyed while Ney's warning held the
   slot. One aggregated beat now names every lapsing corps.
6. **…and once aggregated, it named them twice** ("Davout, Soult, Davout and
   Soult"), because the event window is two turns wide. Deduped per marshal,
   most urgent reading kept.
7. **Internment was reported as annihilation, by his own Emperor.** The
   briefing said *"corps has been DESTROYED"* — it was disarmed, not
   destroyed — and named the captor as `region.controller`, which in the
   measured case (a cut-off enclave France itself held) rendered *"interned
   at Volhynia by France"*. Both fixed; the captor now resolves to the power
   that actually has him surrounded.

### Two standing pins amended, both recorded rather than absorbed

WIN-D5 moves the ambient board, and two pins from the closed AI-Intent
phase read on it. Neither was quietly relaxed:

* **`test_mirror_drifts_down_for_a_passive_france`** required a passive
  France's perceived RUNG *and* weight to fall. Measured by three arms, the
  rung half is WIN-D5's doing (arm 0 `fight`→`ask`, arm A `fight`→
  `indifferent`, arm B `fight`→`fight`). An imperial army camped on the
  frontier is not read as a power winding down, so the wars do not wind down
  either. §3.5's substance — restraint being legible — is still asserted (the
  weight roughly halves), and the rung may still never RISE. **If that
  reduced signal is judged too weak, the lever is WIN-D5, not the test.**
* **`test_nonplayer_slots_live_and_bounded`** forbade any non-player threat
  slot reaching the brewing tier on the ambient run. It now fires (Austria
  83). **The first explanation I wrote for this was wrong and is recorded as
  wrong:** I assumed D3's eclipse clause, then measured — Austria ends with
  **8 provinces against France's 21**, having eclipsed nobody. Tracing the
  producer gave the real answer: **36 × `battle_win`, 3 × `region_capture`,
  2 × `capital_capture`.** With the Guard on the Rhine the German war
  becomes a grind, and a France issuing no orders for forty turns loses it
  repeatedly. A small power that has won thirty-six fights and stormed two
  capitals is genuinely menacing. The flat bound is replaced by the anti-LEAK
  invariant it was standing in for — coalition-tier threat must be EARNED by
  a belligerent — which catches misattribution onto a bystander, the actual
  failure mode, while allowing a small power to become dangerous.

### Verification

* Suite **18,147 passed / 3 skipped** (baseline 18,099/3); ruff clean; no
  `.gd` or `.tscn` touched, so XR-1's parse harness does not apply.
  `tests/test_win_d3_road_home.py` (43).
* **14-mutation sweep, 14 killed.** Four survivors across two passes were
  fixed rather than explained — one badly-chosen mutation, and three real
  coverage gaps: the "the clock simply ran out" retirement branch, and both
  of the fixes the acceptance run had forced (the Munich case and the AI
  rung). A pin that cannot fail is not a pin.
* **M1–M7 byte-identical without re-record** — recorded as a fact about that
  harness (no war in it ends with an army abroad, and it has no sovereign),
  not as independent proof of safety.
* **`BASELINE_SERIES` re-recorded ONCE**, attributed by a 4-arm flip
  experiment with the two changes as separate arms, per the build brief:
  arm 0 (neither) **reproduces the prior series byte-for-byte**, arm A
  (corridor) diverges at index 18, arm B (Lorraine) at index 5, arm AB at
  index 5. A ≠ AB, so both arms are live and neither masks the other. Full
  reasoning at the constant in `tests/test_ai_intent_threat_migration.py`.
  Reported rather than buried: an *earlier* draft measured byte-identical on
  arm A, and that was not a safety result — it was the corridor barely
  working, per defect 1 above.

### Acceptance evidence — and an honest note about it

The brief named `tools/playtest_scripts/win_campaign_p4.json` as the
acceptance digest. **It can no longer serve as one**, and that is a finding
rather than an omission: re-run at HEAD `b33a029` through the p1→p2→p3 chain,
the campaign no longer reaches the Russian peace at all (the §7 WIN fix pass
changed the board), and the run instead terminates at turn 22 on an unrelated
`settlement_confirm` dialogue the driver answers and that never clears —
**a pre-existing block, reproduced before any code in this slice was
written.** Recorded in `BUG_FIXES.md` §Win-Attempt Campaign as WIN-H2.

The stranding is therefore reproduced deterministically instead, which is
better evidence than a digest anyway: `TestTheMeasuredDefect` stages the
exact §5.3 shape (Volhynia — the one province whose four neighbours are ALL
Russian, so a peace shuts every road out of it at once) and carries a
control arm that reproduces the failure with the slice disabled, so it
cannot pass vacuously if the board drifts.

**A player-side run was still driven**, on the p3 save with five French
corps deep in Austria, and it earned its keep: defects 3–7 above were all
found by it and none by the suite. A second script,
`tools/playtest_scripts/win_d3_road_home.json`, reproduces the §5.3
SEQUENCE (peace with Austria, push east, peace with Russia) and is
committed — but it too runs into WIN-H5's `settlement_confirm` block, now
reproduced on two different scripts. The player-facing arc is therefore
pinned end to end through `build_morning_dispatch` instead, in
`TestWhatThePlayerReads`, which is deterministic:

```
T1  the war with Russia is over. 2 corps stand on the wrong side of the new
    frontier. Berthier has given them the road home — Davout to
    Franche-Comte, Soult to Franche-Comte. They have safe passage for 10
    turns while they march.
T2  Davout and Soult are no nearer home, and the safe passage runs out in
    2 turn(s). After that their corps will be interned where they stand.
T3  …in 1 turn(s)…
T4  …in 0 turn(s)…
T5  Marshal Davout's corps was interned at Volhynia by Russia — its safe
    passage had expired and it had not come home. The men are disarmed and
    the colours are lost.
```

And on the ambient 40-turn board, measured: one corridor opens, three
road-home orders stand at peak, the AI walks its corps home, **nobody is
interned** — against three AI corps destroyed before the P1.2 rung existed.

## §8 Known gaps, owned

| Gap | Owner |
|---|---|
| Cut-off corps with no land route gets no rescue | This spec §5; revisit with the naval sea-escape arm |
| Corridor does not extend to allies of the signatory | This spec §5 |
| Internment reuses the NP exit review's "Interned Column" | `NAPOLEON_SPEC.md` exit review / PC15-D1 |

---

## §9 WIN-D5 — the Emperor starts closer

**Ruled: Napoleon boots forward, not at Paris.**

The memo's framing was too strong and is corrected here: he **can** reach
the front from Paris — measured, he arrives — it simply costs about ten
turns, and in 23 turns of campaign he fought in none.

### §9.1 Where: Lorraine

Three reasons, and the third is the one that settles it:

1. **Geography** — Lorraine is adjacent to **Swabia**, where Mack stands.
   He is one march from the opening battle instead of five.
2. **History** — he left Paris on 24 September 1805 and the army crossed
   the Rhine at Strasbourg within the week. The scenario opens *"Late
   September 1805"*. Paris is the historically *wrong* place for him on
   turn 1.
3. **The Guard's own parent corps is already there.** Soult boots at
   Lorraine with 30,000 — the exact corps the Emperor's 10,000 Guard was
   carved from at NP-A. Putting them in the same province makes the carve
   read as an army detaching its Guard, rather than a subtraction
   performed at long distance.

### §9.2 What it costs, honestly

- **The Seat (§8 of `NAPOLEON_SPEC.md`) is not active at boot.** That is
  a real change to a deliberate design: the Seat's +1 DP was written as a
  tradeoff, and a tradeoff you start on the wrong side of is weaker.
  **The counter-argument, which I think wins:** the spec's own stated
  rhythm is *"winter in Paris banking DP, spring on the Rhine spending the
  army"* — and late September 1805 **is** the spring of that cycle. The
  Seat becomes a place he returns to, which is a better shape than a bonus
  he abandons on turn 2 and never sees again.
- **The authored biography must be re-written** — it currently reads *"at
  the Tuileries with the Guard"*.
- **Pins that flip, consciously:** any test reading the shipped
  scenario's Napoleon location, `_sovereign_locations`' boot expectation,
  and the NP-A comment in `test_ai_square_thrash.py`. Most Napoleon tests
  build their own fixture worlds at `location="Paris"` and are unaffected.
- **`BASELINE_SERIES` will very likely move** — the sovereign-fear read
  changes when the Emperor stands next to the front. Expect ONE
  re-record, attributed by the standing flip-experiment method.

### §9.3 Not recommended

A sovereign movement allowance (a faster Emperor) was considered and is
**rejected**: it adds a mechanic to solve a placement problem, it makes
him unlike every other marshal for no fictional reason, and it would let
him outrun the army he is supposed to lead.
