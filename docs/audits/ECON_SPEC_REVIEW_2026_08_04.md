# SPEC REVIEW — ECONOMY (ROADMAP position 3.5)

**Date:** August 4, 2026 · **Prompted by:** *"review the spec, see if this is truly the
best way to fix economy or if it needs retuned or if we have better solutions."*

**Reviews:** `docs/audits/PEACETIME_ECONOMY_RESEARCH_2026_08_03.md` (the decision memo),
`docs/ECONOMY_REVISIT_SPEC.md` (§0.6 gate record, Track 3, Appendix A), and the EC-W
war-coupling record. Every ⊕ figure below was re-measured against master today from the
production functions; nothing is quoted from the memo without checking it.

---

## 0. Verdict

**Half of the recommendation is right and should ship close to as written. The other half
should not be built at all, because the engine already contains it — with four times the
range — and the memo's case for it rests on two claims that are false.**

| | Memo's proposal | Verdict |
|---|---|---|
| **#1(a)** | "The Levy is open" — surface force-limit headroom, announce the flip | ✅ **BUILD IT.** Verified defect, verified numbers, no new fields, no balance change. This is the memo's real finding and it is correct. |
| **#1(b)** | "The Camp of Boulogne" — new `Marshal.readiness`, decays 3/turn, ±10% combat | ❌ **DO NOT BUILD AS SPECIFIED.** It is a second condition stat duplicating morale, which already does the same job at 0.90×–1.50×. |
| **replacement** | **"Let drill restore morale"** | ✅ **BUILD THIS INSTEAD.** Same fantasy, same historical anchor, **zero new serialized fields**, zero new UI, GR5 free, and it closes the loop that is actually broken. |
| **Q2 threat term** | strength-share contributor beside the territorial one | ✅ **BUILD IT**, and it matters more under the replacement, not less. |
| **#2 / #3 / #4** | ES-7b · supply legibility · ES-4 | Agree with the memo: #3 yes (and it should absorb EC-7/ES-6), #2 later, #4 at its own gate post-position-7. |

---

## 1. What verified exactly

The memo's measurements are good. I re-derived the load-bearing ones and they are right
to the digit:

| Claim | Measured today |
|---|---|
| France boots **+59,000 over** its own force limit | ⊕ **exact** — `calculate_turn_upkeep("France")` gives force_limit 130,000 vs total_strength 189,000 |
| France holds **13 building slots**, total, forever | ⊕ **exact** — 1 capital ×2 + 4 major_city ×1 + 7 city ×1 |
| **49 of 126** provinces can never hold a building | ⊕ **exact** — `BUILDING_SLOT_LIMITS` gives town and rural 0 |
| A market on a `city` is **−3/turn permanently** | ⊕ **exact** — Artois, income_value 150 → +37 gross against the 40g `EUROPE_INFRASTRUCTURE_UPKEEP` |
| The ledger already carries the force limit | ⊕ confirmed — `force_limit`, `over_limit`, `total_strength` all present in `ledger.py` |
| Passive threat is **100% territorial** | ⊕ confirmed — `coalition.py` has `region_control_60/70/80` and `_calculate_hegemony_pressure`; there is **no** military or strength-share term anywhere in the module |

**So #1(a) is a real defect with a verified shape**: the game computes the number, already
ships it to the ledger, and never says the gate re-opened. Build it.

One refinement to the memo's arithmetic, below.

---

## 2. Why #1(b) should not be built

### 2.1 The mechanic it proposes already exists, at four times the range

`Marshal.morale` is a serialized 0–100 per-marshal condition stat that already feeds combat
through `get_combat_effectiveness()`:

```
⊕ morale 100 -> 1.50x     morale 60 -> 1.10x
⊕ morale  70 -> 1.20x     morale 40 -> 0.90x
```

`readiness` would be a **second** serialized 0–100 per-marshal condition stat feeding combat
at **0.90×–1.00×**. Two condition bars on the same object, the new one a sixth of the range
of the old one — on the pillar (combat legibility) that this whole ROADMAP position exists
to protect.

### 2.2 The veteran/conscript axis it wants is already shipped, end to end

The memo's fantasy is "an army you stopped drilling loses a battle it should have won."
Measured, the engine already models the *other* half of Boulogne — raw conscripts are worse
than veterans, and you can train them:

- ⊕ `economy_executor.py:327` — `RECRUIT_MORALE = 40`, *"Green conscripts base morale."*
- ⊕ `:568` — new troops **dilute the receiving corps by weighted average**.
- ⊕ `:528` — **`training_ground` raises recruit morale 40 → 70.**
- ⊕ `:538` — Moore's *Shorncliffe System* floors it at 60. The historical light-infantry
  training school is in the game, by name.

Worked, on the memo's own example — the five recruits that would have saved the campaign:

```
⊕ 25,000 veterans @ morale 100 + 50,000 levies @ 40  ->  morale 60   (1.50x -> 1.10x)
⊕ ... with a training_ground in the recruiting province ->  morale 80   (1.50x -> 1.30x)
```

**The training ground is worth 18% of that army's combat power for 250 gold.** The memo
says it is *"today a 250g building… with no measurable peacetime effect"* and proposes to
make it halve a readiness decay so that "it finally does something." **That is false, and
the building it dismisses is the Camp of Boulogne.**

The econ spec knew this. `ECONOMY_REVISIT_SPEC.md` Appendix A, **ES-9**: *"Green quality via
the **existing** green-conscript morale dilution (**no new field**)."* The spec had already
found this mechanic and already ruled that it needs no new field.

### 2.3 The second premise is also false, and it is the one the design is derived from

> *"drill and fortify buy permanent, non-decaying state, so the tenth turn of drill is worth
> exactly zero. Decay is what converts a menu into a budget."*

⊕ Drill's bonus is **not permanent state**. It is a **one-shot** +20% attack (`shock_bonus`)
consumed by the first attack — `combat.py:436-440` clears `shock_bonus`, `drilling`,
`drilling_locked` and `drill_complete_turn` together, with a comment explaining why.

The *conclusion* is right — the tenth drill is worth zero — but for the opposite reason: the
bonus is a **consumable a passive player never spends**, and it does not stack. Since the
whole of #1(b) is derived from the stated mechanism rather than the conclusion, the design
does not follow from the evidence.

---

## 3. The better solution: let drill restore morale

⊕ **Measured: morale never moves in peacetime.** `_process_tactical_states` does not touch
it across any number of ticks; `_execute_drill` does not mention it; there is no regen tick
anywhere. Morale changes through **combat only**.

So the veteran/conscript axis is **one-way**. You can debase a corps — by rebuilding it,
which is precisely what the memo wants the player to do — and you can never train it back.
That is the actual hole, it is exactly what the Camp of Boulogne historically *was* (two
years turning conscripts into the Grande Armée), and closing it costs nothing:

**`drill` completion raises the corps' morale toward 100, amplified by a `training_ground`
in the province.**

| | new `readiness` | drill → morale |
|---|---|---|
| New serialized fields | 1 | **0** |
| New numbers on the marshal card | 1 | **0** |
| New per-turn tick | yes | **no** |
| GR5 cost | needs an AI rung to maintain it | **free — the AI already drills** |
| Combat seam | new read in `get_attack_modifier`/`get_defense_modifier` | **the existing `get_combat_effectiveness` chokepoint** |
| Range | 0.90×–1.00× | 0.90×–1.50×, already tuned and shipped |
| Shape | **a tax** — pay every turn to stand still | **a want** — repair what you chose to break |

That last row is the argument in the spec's own vocabulary. **ES-4's written standard is
*"Drop any per-turn maintenance… A want, not a tax."*** A decay clock on 5–7 marshals against
4 military AP means you can never keep them all sharp, so the steady state *is* the floor and
drilling only buys you back to par — a chore with a number attached, which is the shape the
memo itself rejects for roads, canals, education and stability-repair. Morale restoration
inverts that: your army is debased only if you *chose* to rebuild it.

**And it makes the memo's own headline finding land properly.** The memo says five recruits
for 2,250 gold would have saved that campaign. It never modelled what the levy does to the
corps: ⊕ combat power goes ×3 in men but ×0.73 in effectiveness — a real gain of ~×2.2, not
×3, followed by a permanent, unadvertised debasement with no path back. Under this fix the
purchase becomes an honest bet: **cheap men now, military AP to make them soldiers** — which
is the peacetime decision the memo went looking for, and it is one the engine can already
almost express.

**The full loop, three of whose four mechanics already ship:**

1. `(a)` the levy re-opens, visibly, with headroom and price on screen. *(new — legibility)*
2. The levy debases the corps. *(shipped)*
3. A `training_ground` in the recruiting province pre-empts most of the debasement — which
   is what makes it worth one of France's 13 slots, and worth building **at the moment the
   levy re-opens** rather than never. *(shipped)*
4. Drill repairs the rest, over turns, using the idle military AP. *(new — one behaviour)*

### 3.1 What I am NOT claiming

This replacement creates **no peacetime pressure by itself** — a passive France with idle AP
can hold a max-morale army indefinitely. That is deliberate: the memo already proved
punishment is not the missing ingredient (⊕ 189,000 → 60,183 men, nine provinces lost, the
War Effort tax at 2,319g/turn, and it *still* ended rich). Pressure is **Q2's job**, and the
replacement makes Q2 more necessary, not less: it removes the one hidden cost that was
quietly discouraging a rebuild.

It must also be measured against M1–M7 before landing — a marshal who drills now enters
combat at a different effectiveness. I expect no movement (harness marshals do not drill),
but that is a prediction, not a result.

---

## 4. The six open questions

**Q1 — Does readiness touch combat, or only display?** *Moot as asked — readiness should not
exist.* Reframed for the replacement: **yes, through the existing chokepoint**, and it can
only ever move a corps **up** toward a cap the game already enforces. Strictly bounded, no
new modifier, no new label.

**Q2 — Does Europe see a re-arming France?** **Yes — build the strength-share threat term.**
Confirmed: there is no military term in `coalition.py` at all, so a France that gets stronger
without getting bigger is currently invisible, and that is a genuine dominant strategy
(stop conquering → re-arm → let threat decay → strike). ⊕ Boot-safe with more headroom than
the memo claimed: France is **31.5%** of Europe's 600,000 standing men (the memo said ~35% of
~540,000), comfortably under a ~40% trigger. Symmetric across all nations. **Do not ship
#1(a) without it** — that part of the memo is right.

**Q3 — The standing GR5 ruling for peacetime verbs.** Accept the memo's default: *reachable
by the AI through the same executor, with a measured firing rate that may be zero on the
1805 board*, and the acceptance test **records** the rate rather than requiring it non-zero.
Note that under the replacement this is free rather than nominal — the AI already has drill
rungs, so the mechanic fires for it with no new decision code and no enemy-phase cost. That
is a straight improvement on a pillar that just re-scored 6.0.

**Q4 — Is an admin AP still worth 25 gold?** Agree: **leave 25 alone.** ⊕ It is 50g/turn
against a 29,000g treasury. Removing it silently re-prices every admin action. Record it as
the project's declared AP↔gold rate and price new actions against it deliberately.

**Q5 — Where does ES-4 (province development) go?** Agree: **EC-2 pass 2's own gate, after
position 7.** The memo's argument here is its strongest and I could not break it: the War
Effort tax takes `treasury × WE // 2500`, so at the WE cap the treasury is a **fixed point at
12.5 × free cash flow**, not a runaway. ⊕ 1,938 net × 12.5 ≈ the 29,000 it sat at. **A stock
sink cannot move a self-limiting stock** — which means *no* gold sink fixes this, and ES-4
would absorb money without changing the equilibrium. That insight deserves to survive this
review even though nothing is built on it.

**Q6 — the EC-7 / ES-6 GR9 debt.** Below.

---

## 5. EC-7 / ES-6 — recommend an explicit CUT, with its intent re-homed

The row (`ECONOMY_REVISIT_SPEC.md` Track 3) is distance-from-capital supply attrition, owning
the **manpower** half while ES-2 owns the gold half. Its dated trigger — *"opens immediately
after the EC-2 pair lands and its AI-solvency band test is green"* — fired **July 9, 2026**
and it was never opened. GR9 requires a landing or a cut. **I recommend the cut, recorded
with its reason**, for three:

1. **It adds a second attrition term before the first one is legible.** The played campaign
   starved three corps to death through the *existing* supply attrition, which is capped at
   6%/turn — slow enough that no single turn alarms and thirty turns are fatal — and which
   ⊕ **is not in `HEADLINE_WEIGHTS` at all**, so it can never lead a dispatch. Making the
   game harsher before making it clearer is the wrong order.
2. **Its purpose has largely been served by systems that postdate it.** ES-6 was scored to
   make deep offensives costly. Since then: EC-W1 *Contributions of War* suspends income on
   disrupted provinces, ES-2 charges occupation on non-homeland soil, EC-U3's Grande Armée
   surcharge prices a supermassive army, and the naval crossing gate closed the walk-to-
   London class of overreach outright.
3. **The map changed underneath it.** It was specified against a 19-region world. A
   per-hop distance penalty on 126 provinces with a naval layer is a different mechanic than
   the one that was scored 7/10.

**Re-home the intent, don't just delete it:** memo **#3 ("Supply becomes a decision you can
see", ~½ session)** is the honest successor — a `supply_strain` headline class that names the
stack, the capacity, the cumulative loss and **whichever remedy is legal**, given ⊕
`supply_depot` is illegal in 16 of France's 28 provinces so the obvious advice is often the
wrong advice. That is the same concern — deep armies starve — delivered as legibility
instead of a second tax. **It is a defect fix, and it should ride with #1(a).**

---

## 6. Recommended slice

**One session, and it is smaller than the memo's:**

- **(a) The Levy is Open** — force-limit headroom as a first-class number; a once-per-flip
  dispatch beat on `over_limit → under_limit`; the live price and headroom on the region-panel
  recruit chip. *(no new fields; the figures already exist and already reach the ledger)*
- **(a2) The strength-share threat term** — Q2, symmetric, boot-zero-checked at 31.5%.
- **(b′) Drill restores morale**, amplified by a `training_ground`. *(zero new fields; the
  existing `get_combat_effectiveness` chokepoint; GR5 free)*
- **(c) The supply-strain headline** — memo #3, absorbing EC-7/ES-6's intent.

**Not in it:** `Marshal.readiness` · ES-4 · ES-7b · anything with a per-turn decay clock.

### 6.1 BUILT — August 4, 2026 (user approved the §6 slice and the Q6 cut)

All four landed, plus the EC-7 / ES-6 cut. **Zero new serialized fields across the
whole slice.** Tests `tests/test_ec_levy_and_camp.py` (33); **16-mutation sweep, one
inert pin found and replaced**; suite 16,136 → **16,171 / 3**; ruff clean; corpus
514/514; Godot parse harness EXIT=0 (4 `.gd` touched); live-verified over HTTP on a
fresh backend.

- **(a) The Levy is Open.** One source, `economy_executor.get_levy_status`, read by
  the ledger, the map summary and the region panel. ⊕ Boot: 189,000 / 130,000, **over
  by 59,000**, gate shut, price **654** (the over-limit multiplier, shown = applied).
  ⊕ At the played campaign's turn-12 state: headroom 58,180, gate **open**, price
  **450g per 10,000 foot at Paris** — the memo's own figure, quoted from the function
  that charges it. **The defect was worse than filed:** `strategic_ledger.gd` rendered
  the force limit only inside `if over_limit_surcharge > 0`, so the number appeared
  exactly while the gate was shut and vanished the moment it opened. Now a standing
  Establishment line.
- **The flip beat needs no serialized memory.** `levy_open` is a STANDING headline
  class (weight 54) riding PC-7's existing cooldown and escalation ladder — better
  than the memo's once-per-flip design, because the offer keeps being reported while
  it stands, and it cannot become the next stuck record. The ladder was generalised to
  render each class's own template fields; that pin was widened consciously.
- **(a2) The strength-share threat term.** `military_establishment`, symmetric, ⊕
  boot-zero at 31.5% of Europe's 600,000. Europe-scoped (N1) after the first cut
  turned `test_audit_part2::test_r1_base_decay_of_1` red by exactly cancelling that
  test's −1 decay on the 19-region fixture.
- **(b′) Drill restores morale.** `+10`, `+15` with a `training_ground`, capped at
  the existing 100, through `get_combat_effectiveness`. Single source across both
  completion arms. The one-way axis is closed.
- **(c) The supply-strain headline.** Weight 72 — between a lost province and a war
  declaration. Two consecutive turns of loss; names the stack, the excess, the
  cumulative dead, and **whichever remedy is legal**. Also made STANDING, so the
  famine cannot simply replace the household nag as the sentence that repeats.

**A pre-existing defect found in passing, and it is the more serious finding.** The
AI-V assurance harness's seed pin was **escapable**: every fixture in
`test_ai_intent_assurance.py` is module-scoped, and pytest sets higher-scoped fixtures
up **before** function-scoped autouse ones — so all four sweep runs were built outside
conftest's `SOVEREIGN_SEED=historical` pin and inherited the developer's shell. The
symptom is the worst kind: `test_pair_peace_is_exhaustion_driven` flipped on this
slice while the full suite stayed green, because the *seed* differed between the two
runs, not the behaviour. `spawn_run` now writes the seed it was asked for into the
child environment, so `--seed` is authoritative; the file passes under a bare shell,
the intended pin, and a deliberately hostile `SOVEREIGN_SEED=austerlitz`. Pinned two
ways in `TestSweepSeedIsNotEscapable`, mutation-checked.

**M1–M7 and `BASELINE_SERIES` byte-identical, no re-record** — and, as with the
composition slice, that is a fact about the harness: the ambient trace never crosses
the 40% share gate and its marshals do not complete drills.

**Falsifiable acceptance test**, adapting the memo's: *in a 40-turn campaign where France goes
passive at turn 5 — (i) France's strength at turn 40 is ≥60% of its turn-5 strength, **or** the
transcript contains a turn on which the player declined a stated levy offer with headroom and
price on screen; (ii) ≥1.2 admin actions per turn on average go to `recruit`; (iii) **mean
French morale at turn 40 is below 100** — i.e. the levy really did debase the army and drill
did not fully cover it; (iv) treasury at turn 40 below 20,000.* Clause (iii) replaces the
memo's readiness clause and measures the same thing with a number that already exists.

---

## 7. Corrections to the record

Three claims in the August 3 memo are wrong and the memo should carry these, since it is
otherwise accurate and will be read again:

1. **`training_ground` has a large peacetime effect** (recruit morale 40 → 70, ⊕ worth ~18%
   of a rebuilt army's combat power for 250g). The memo's *"no measurable peacetime effect…
   it finally does something"* is false. Its 40g/turn-forever critique still lands — the
   effect is **lumpy**, paying only at the moment of a levy.
2. **Drill's bonus is a one-shot consumable, not permanent state** (`combat.py:436-440`). The
   conclusion the memo drew from it is right; the mechanism is not, and #1(b) was derived
   from the mechanism.
3. **The rebuild's cost was never modelled.** ⊕ Five levies into a 25,000-man corps take it
   from 1.50× to 1.10× effectiveness. The purchase remains correct — ~×2.2 real gain, not
   ×3 — but the memo presents "47,500 men back in the field" as though men were the whole
   quantity.

And one of my own, from the campaign report this all descends from: I wrote that a passive
France *"has nothing to buy."* The memo corrected that to *"the purchase existed and was
invisible."* This review sharpens it once more: **the purchase existed, was invisible, and
carried a hidden cost with no way to pay it off.** All three fixes above are that one
sentence.
