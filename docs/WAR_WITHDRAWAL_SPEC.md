# WAR WITHDRAWAL SPEC — "The Road Home"

> **Design document. ⚠ USER GATE PENDING at §7 — nothing is built.**
> Authored August 16, 2026 from two rulings taken on the win-attempt
> campaign's design rows: **WIN-D3** (*"ending war should send troops back
> to borders with free march orders"*) and **WIN-D5** (*"he can reach from
> Paris, right — we can start him closer"*).
>
> Evidence: `docs/audits/PLAYTEST_WIN_CAMPAIGN_2026_08_16.md` §5.3 and
> §5.5. Rows: `docs/DESIGN_REFINEMENT.md` §Win-Attempt Campaign.

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
