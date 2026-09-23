# The Recruit-Arm UX Bug — investigation and fix plan

> **Status: INVESTIGATION + RECOMMENDATION. Nothing here is built, gated or
> approved.** Produced September 20, 2026 by a 53-agent read-only fleet
> (18 recon -> 18 adversarial refuters -> 7 competing plans -> 6 judges ->
> 4 syntheses), driving the real `POST /command` and the real
> `CommandParser.parse` against an unmodified `europe_1805.json` boot world at
> HEAD `15c498cb`, `LLM_MODE=mock`, seed `historical`. No repo file was modified
> during the investigation.
>
> **User report: "you can click recruit cavalry etc for every general — the generals and units are mutually exclusive correct?"**
>
> Every claim below carries a confidence marker. **measured** = the agent ran it
> and is reporting output. **read** = the code path was read end to end.
> **inferred** = judgement. Claims that could not be reproduced are recorded as
> such rather than deleted. Line numbers were current at measurement time; this
> repo's own records say ~80% of filed line numbers go stale, so **navigate by
> symbol**.

---

## Verdict in one paragraph

Yes — arms and generals are mutually exclusive, enforced by a constructor that raises; a marshal IS a corps and his arm is immutable. And yes, it is a real bug: the arm word on the chip is discarded entirely, so Infantry/Cavalry/Artillery are three buttons with one outcome, charged in full. Measured on the real endpoint: all three chips at Rhineland deliver 3,000 infantry for 741 gold (92.6% of France's 800-gold turn-1 treasury); all three at Franche-Comte deliver 3,000 cavalry for 1,504 gold while an infantry marshal stands in that province and would have cost 872.


## Key numbers (all measured unless noted)

- Chips rendered board-wide: 30 provinces x 3 = 90; 63 dead (French, no marshal in range, incl. PARIS) + 6 dead (ally soil) + 21 acting
- Wrong-arm chips among those that act: 14 of 21 (each acting province is locked to exactly one arm)
- Rhineland, all three chips: 741 gold, 1 of 2 admin AP, 3,000 INFANTRY via Davout - identical, every time
- Franche-Comte, all three chips: 1,504 gold, 3,000 CAVALRY via Murat - vs 872 gold for infantry when Lannes is named explicitly (+72.5%)
- France turn-1 treasury: 800 gold. One Rhineland click leaves 59.
- Provinces where the requested arm was in range and not delivered: 5 of 7 acting French provinces
- Artillery marshals on the entire 1805 board: 0 (so no chip can ever deliver artillery until Marmont or Senarmont is commissioned)
- Cavalry marshals on the entire board: 1 (Murat). France's commission bench: 5 infantry + 2 artillery + 0 cavalry
- AI recruit producers that pass an explicit marshal: 2 of 2 (enemy_ai.py:6046, :6257) - so an arm-keyed selector never reaches the AI


## Open questions that need your ruling

- Which surface did you actually click? There is NO per-general recruit chip anywhere in the client - a repo-wide grep for `do:recruit` over godot-client/**/*.gd returns exactly one producer, region_panel.gd:272, the province row. It sits directly above the per-marshal order chips (Fortify/Drill/Scout/Attack), which is almost certainly why it reads as per-general. If you meant the Generals screen, the defect you saw is a different one (the commission bench renders artillery candidates untagged under an 'Infantry pool' header) and the slice order changes. Either way the typed per-general form `Murat, recruit infantry` has the identical bug, so the fix is owed regardless.
- Should recruiting be legal on ally/vassal soil? Six chips at Franconia (Bavaria) and Milan (Kingdom of Italy) render enabled and refuse permanently - the row is gated on a SUBSTITUTE-market signal while the executor gates on control. This is IQ-10's H1 finding one verb over. I recommend deciding it in the same slice but not resolving it silently.
- Should the 1805 board have any artillery marshal at all? There are zero, for any nation, so the 10,000-man artillery pool is unreachable by recruit and the 3-arm combined-arms tier (+20% attack/+10% defence) is reached by nobody. The fix makes this visible as an honest refusal on all 126 provinces, which reads like a bug unless the copy names the remedy (commission Marmont or Senarmont - I verified that works and also un-deadens Paris).


---

# The Chip Names the Man

*Everything below marked **measured** was driven against the real `POST /command` endpoint on an unmodified 1805 boot world, one fresh world per cell. Where I funded the treasury to reach a case, I say so.*

---

## 1. Direct answer: yes, and more strongly than "mutually exclusive"

Arms are mutually exclusive **by construction** — the constructor refuses the illegal combination:

```python
# backend/models/marshal.py:240-242, Marshal.__init__
# Mutual exclusivity: a marshal can be infantry, cavalry, OR artillery
if cavalry and artillery:
    raise ValueError("A marshal cannot be both cavalry and artillery")
```

But your instinct is sharper than the word "exclusive". **There is no unit entity at all.** The marshal *is* the corps: his `strength` integer is its size, and his flag is its arm.

```python
# backend/models/marshal.py:505,509
self.cavalry: bool = cavalry      # True for cavalry commanders (Ney), False for infantry
self.artillery: bool = artillery  # True for artillery commanders (Drouot)
```

A census of every write to either flag across `backend/` finds exactly **one** site, and it is a debug cheat (`meta_executor.py:1395`). So a marshal's arm **cannot change in ordinary play**.

Which means: *"which arm"* and *"which general"* are the same decision. The panel asks for it twice.

**Measured roster, 1805 boot:**

| Marshal | Arm | Location | Strength | Range |
|---|---|---|---|---|
| Ney | infantry | Rhineland | 24,000 | 1 |
| Davout | infantry | Rhineland | 26,000 | 1 |
| Soult | infantry | Lorraine | 30,000 | 1 |
| Lannes | infantry | Franche-Comte | 18,000 | 1 |
| **Murat** | **cavalry** | Franche-Comte | 22,000 | **2** |
| Bernadotte | infantry | Franconia | 17,000 | 1 |
| Massena | infantry | Milan | 42,000 | 1 |
| Napoleon | infantry | Lorraine | 10,000 | 1 |

Murat is the **only cavalry marshal on the entire board, for any nation**. There are **zero artillery marshals anywhere**.

---

## 2. Is it a bug? Yes — a wrong purchase, charged in full

### What the code does

`_execute_recruit` derives the arm from the **recipient marshal** and never reads the player's choice:

```python
# backend/commands/economy_executor.py:783-788, _execute_recruit
recruit_marshal = world.get_marshal(recipient)
...
if getattr(recruit_marshal, 'artillery', False):
    recruit_type = "artillery"
elif getattr(recruit_marshal, 'cavalry', False):
    recruit_type = "cavalry"
else:
    recruit_type = "infantry"
```

`requested_type` — the word on the button — is consulted **exactly once in the whole function**, and only to build a string:

```python
# backend/commands/economy_executor.py:862-864
# Soft correction: player asked for wrong type
soft_correction = ""
if requested_type and requested_type != recruit_type:
    soft_correction = f"Berthier notes: 'Marshal {recruit_marshal.name} commands {recruit_type}, Sire.' "
```

The client sends the arm verbatim and does nothing with it:

```gdscript
# godot-client/project-sovereign/scripts/region_panel.gd:270-272
for arm in ["infantry", "cavalry", "artillery"]:
    recruit_chips += Utils.bb_button_chip("do:recruit " + arm + " in " + _region, arm.capitalize(), ...)
```

### What actually happens when you click — measured

**Rhineland** (Davout, infantry, is nearest). On an unmodified turn-1 boot, France holds **800 gold**:

| Chip clicked | Result | Gold | Admin AP | Pool moved |
|---|---|---|---|---|
| **Infantry** | 3,000 infantry via Davout | 800 → 59 | 2 → 1 | infantry −3,000 |
| **Cavalry** | 3,000 infantry via Davout | 800 → 59 | 2 → 1 | infantry −3,000 |
| **Artillery** | 3,000 infantry via Davout | 800 → 59 | 2 → 1 | infantry −3,000 |

Byte-identical. The only difference is one sentence of prose. This is what the player is told after clicking **Cavalry**:

> *"Berthier notes: 'Marshal Davout commands infantry, Sire.' Davout recruits 3,000 infantry for Rhineland (0 regions away) (field levy — no depot; capped at 3,000) - Cost: 741 gold (Davout's intendance: -15%). Morale: 100% → 93% Infantry pool: 80,000 → 77,000"*

Note what that sentence never says: that a request was **refused**. It arrives after the gold is gone, reads as a footnote, and 741 of 800 gold — **92.6% of the turn-1 treasury** — plus **1 of 2 admin actions** are already spent.

**Franche-Comte** is the inverted and costlier case. Murat (cavalry, 22,000) and Lannes (infantry, 18,000) stand in the same province. Measured on a funded world (this case needs 1,504 gold; France reaches that on turn 2 — at boot all three chips refuse for free):

| Chip clicked | Result | Gold | Pool moved |
|---|---|---|---|
| **Infantry** | 3,000 **CAVALRY** via Murat | −1,504 | cavalry −3,000 |
| **Cavalry** | 3,000 cavalry via Murat | −1,504 | cavalry −3,000 |
| **Artillery** | 3,000 **CAVALRY** via Murat | −1,504 | cavalry −3,000 |

The counterfactual, same province, arm named explicitly — **measured**:

```
Lannes, recruit infantry  →  3,000 infantry for 872 gold
```

So clicking **Infantry** costs **+632 gold (+72.5%)**, delivers the wrong arm, and drains the **15,000**-man cavalry pool instead of the **80,000**-man infantry pool. The panel quotes **872** beside all three chips.

### Why: the selector has no arm term

```python
# backend/models/world_state.py:5548, find_nearest_marshal_to_region
ready_marshals.sort(key=lambda x: (x[1], -x[0].strength))
```

Distance, then **strength**. The requested arm is not a sort key, so at Franche-Comte the stronger Murat (22,000) beats Lannes (18,000) and the Infantry chip buys horse.

### The arm was usually available and was refused anyway

I enumerated every in-range French marshal at each acting province:

| Province | Delivers | Arms actually in range | Refused though reachable |
|---|---|---|---|
| Burgundy | cavalry | cavalry only | — |
| Savoy | cavalry | cavalry only | — |
| **Franche-Comte** | cavalry | infantry (Lannes d0, Soult d1, Napoleon d1), cavalry (Murat d0) | **infantry** |
| **Lorraine** | infantry | infantry ×5, cavalry (Murat d1) | **cavalry** |
| **Nivernais** | infantry | infantry ×3, cavalry (Murat d1) | **cavalry** |
| **Orleanais** | infantry | infantry ×2, cavalry (Murat d2) | **cavalry** |
| **Rhineland** | infantry | infantry ×4, cavalry (Murat d2) | **cavalry** |

**On 5 of the 7 acting French provinces, the arm the player clicked was standing in range and was not delivered.** Burgundy and Savoy are not selector losses — only one arm is reachable there at all.

### Severity

**Wrong purchase, charged in full, irreversible, at the scarcest resource on the board.** Not cosmetic; not merely wasted AP; not working-as-intended.

Three qualifications, stated honestly:

- At **Rhineland on turn 1** the delivered arm is what an infantry marshal would have given you anyway. The harm there is that you asked for cavalry, paid 92.6% of your treasury and half your admin budget, and were told about it in a subordinate clause. The *materially* costly case (wrong arm **and** +72.5% price) is Franche-Comte, reachable from **turn 2**.
- **A refused chip is free** — I confirmed gold and both AP counters are byte-identical on every refusal family. So the 69 dead chips are noise, not damage. The whole cost is concentrated in the 21 acting chips and the typed form.
- The **general AP pool is untouched** — `actions_remaining` stays 4. Only `admin_actions_remaining` moves. You keep all four ordinary orders after a wasted levy.

### Your actual words: "for every general"

There is **no per-general recruit chip anywhere in the client**. A repo-wide grep for `do:recruit` over `godot-client/**/*.gd` returns exactly one producer — `region_panel.gd:272`, the province row. `marshal_management.gd`'s "recruitment" is the **commission bench** (hiring a new marshal), not arm recruitment.

But the bug is not confined to the chip. **The typed per-general form has the identical defect, with the player having named both the general and the arm** — measured:

| Typed | Asked | Delivered | Gold |
|---|---|---|---|
| `Murat, recruit infantry` | infantry | **cavalry** | 1,504 |
| `Murat, recruit artillery` | artillery | **cavalry** | 1,504 |
| `Davout, recruit cavalry` | cavalry | **infantry** | 741 |
| `Davout, recruit artillery` | artillery | **infantry** | 741 |
| `Lannes, recruit cavalry` | cavalry | **infantry** | 872 |
| `Napoleon, recruit cavalry` | cavalry | **infantry** | 741 |

This is the worse surface — an explicit two-part order, both parts honoured except the one that decides what you buy. **A fix that only re-keys the province chip leaves it untouched.**

### The rest of the surface, censused

I reproduced `region_panel.gd:265-268`'s own `feeds_us` gate byte-for-byte against the real fogged client payload (`get_filtered_game_state_summary()['map_data']`):

```gdscript
var feeds_us := controller == _PLAYER_NATION \
    or int(data.get("recruit_price_here", 0)) > 0 \
    or int(data.get("substitute_price_here", 0)) > 0
```

**30 provinces render the three-chip row = 90 chips:**

- **63 dead** — French soil, no marshal within his own `movement_range`. Refusal: *"Berthier scans the dispatches. 'No marshal is available to receive reinforcements at Berry, Sire.'"* **Paris, the capital, is among them.**
- **6 dead** — Franconia (Bavaria) and Milan (Kingdom of Italy), admitted by `substitute_price_here > 0`. Refusal: *"Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'"* The row is gated on a **substitute-market** signal while the executor gates on **control**.
- **21 acting** — of which **14 deliver an arm the label did not name**.

So **three-quarters of the chips this surface renders cannot do anything**, and two-thirds of the rest do the wrong thing.

---

## 3. Sibling instances of the same bug class

The class is: *a chip composes a command naming a parameter the executor discards.* This repo has fixed it twice already, by two different remedies — which is the argument for a rule rather than a third patch.

**Precedent A — fix the executor.** The two Repair chips had exactly this defect ("Repair works" fell through to the war-damage arm); WO slice 8 closed it in `_execute_repair`. I drove it: the fix holds, the two chips are genuinely distinct.

**Precedent B — disclose at the chip.** `region_panel.gd:434-441`'s `build ships`, whose own comment reads:

> *"NV-12 (recon gap 11): the chip is region-scoped in appearance but NATION-scoped in effect — the keel lands in the first yard, which may not be this one. Say where."*

The remedy there was a `yard_note`, not an executor change.

**Still live — measured:**

| Sibling | Measured behaviour |
|---|---|
| `propose white peace with <N>` (`diplomacy_wizard.gd:767`) | Printed to the terminal **and pushed into up-arrow history** while the real action routes structurally. Re-typing the game's own sentence: *"Sire, regarding the **Peace Treaty** proposal to Austria…"* — the white peace is gone. |
| `cede territory to <N>` (`diplomacy_wizard.gd:796`) | The echo drops the province the player picked. **And the typed form reads a province perfectly well** — `cede Rhineland to Holland` → *"Cannot cede Rhineland: Rhineland is France's own homeland"*. So this is a **lossy paraphrase**, not display copy for a form the parser cannot read. The honest echo is one interpolation away. |
| `buy substitutes for <M>` | Quotes `levy.substitutes.amount` = **10,000** and delivers **3,000** in the field. Enabled on a **national** `subs.open` flag while the executor refuses **per-province**. |
| `Attack ArchdukeCharles` (`region_panel.gd:557`) | Raw camelCase roster key on a player-facing surface — `grep -c humanize_entity_name region_panel.gd` is **0**. Golden Rule 7 forbids it. |

**And the chip's lie is recorded in the player's own log.** `main.gd:6577-6579` does `_add_to_history(command)` then `add_output('> ' + command)` — so clicking Cavalry prints `> recruit cavalry in Rhineland` into the transcript and parks it on the up-arrow while 3,000 infantry arrive. **A fix that only changes the chip label leaves the transcript wrong.**

---

## 4. The fix

### The ruling

**The requested arm is illegitimate as an *override* on a named marshal, and entirely legitimate as a *selection key* on a province.**

That distinction is the whole design. You cannot order a cavalryman to raise guns — `Murat, recruit infantry` correctly raises horse and says so, and `test_pf7_recruit_arm_amount_bombard.py`'s docstring pins that in writing:

> *"Three silent drops, made non-silent (surface or reject — **never honor an arbitrary arm/count, which is an escalated balance change**)"*

But `recruit cavalry in Rhineland` names **no marshal**. The game is already choosing one for you, *freely*, by `(distance, -strength)`, with the arm not a sort key at all. That selection is not a balance decision the player made; it is an arbitrary tiebreak. Making the arm a key on that tiebreak takes nothing away from anyone.

### Why not the obvious alternatives

**(a) "Render only the arms available at that province."** Rejected as a standalone. "Available" is exactly what the selector is blind to — at Franche-Comte both arms are in range, so (a) renders both chips and Infantry still buys cavalry. Worse, a pure-client (a) is **measurably wrong on the majority of the live surface**: on 4 of the 7 acting provinces (Burgundy, Nivernais, Orleanais, Savoy) the recipient stands in an **adjacent** province and does not appear in that region's payload marshal list at all. A `.gd` reading `marshals[].arm` would render "no arms available" where a recruit succeeds today. Anyone proposing a client-only fix should be shown that measurement first.

**(b) "Keep all three, dimmed with the reason."** Mandatory, but not sufficient. It is this project's stated honest-availability idiom and `Utils.bb_chip_disabled` is **already used twice in this same file** (`:341`, `:475`) and never on this row — so it is the right treatment for the 69 dead chips and for artillery. But (b) applied to the *arm* produces a worse lie than the bug: it would grey out **[Cavalry]** at Franche-Comte while Murat is standing in Franche-Comte. **(b) is how the fix is presented, not an alternative to it.**

**(c) "Make the executor honour the requested arm."** Rejected *in that form* — PF-7 is right about the marshal-named branch, which this does not touch.

**(d) "Delete the three chips, render one chip per eligible marshal."** The fallback, not the recommendation — it is what R1+R3 alone give. Rejected as primary because the client cannot enumerate adjacent recipients, so it loses 4 of the 7 provinces that work today. It **is** the kill-criteria fallback.

### The recorded dissent

A reviewer may read PF-7 as covering the province form too, and demand a user gate. **The counter-argument belongs at the seam in code, not only in a landing record:** PF-7's three cases are all marshal-named, its two tests both pass `marshal=`, and the one pin that exercises the province form —

```python
# tests/test_manpower_pools.py:586-600
def test_recruit_at_region_with_cavalry_marshal(self):
    """'recruit at Paris' with cavalry marshal nearest -> cavalry."""
    ...
    for m in world.marshals.values():          # moves every other marshal away
        if m.nation == "France" and m.name != "Ney":
            m.location = "Bordeaux"
    result = recruit_result(world, executor, target="Paris")   # no requested_type
```

— passes **no `requested_type` at all** and deliberately isolates a single marshal. It pins *"no request, one arm reachable"*. It has never pinned *"a request, two arms reachable"*.

**Second dissent, recorded and not acted on:** the fix makes cavalry genuinely buyable from the panel, at 60g per 1,000 men from a 15,000-man pool against infantry's 20g from 80,000. No blessed constant moves, but the player's reachable choice set widens. That is the point of the fix, and it is why R2 carries a measured series arm rather than an assertion.

### Kill criteria — do not ship R2 if either holds

1. The `arm=None` default of `find_nearest_marshal_to_region` is not byte-identical to today across a 126-province × 8-marshal drift pin. **The selector has five call sites, two of them in `combat_executor.py` (`:9977`, `:9997`)**, and a selection change that reaches combat is a different slice with a different gate.
2. An AST census over `backend/ai/**` finds any `{"action": "recruit"}` producer without an explicit `marshal` key. **Today it is 2 of 2** — `enemy_ai.py:6046-6047` and `:6257-6258` both pass `"marshal": <name>` — so the AI never enters the changed branch and GR5 is free. If that stops being true, R2 needs a measured `BASELINE_SERIES` re-record with flip-arm attribution, not a stated reason.

Either way, fall back to **R1+R3 alone** (name the recipient, dim the unreachable arms), which closes the lie without touching selection, and file R2 to a gate.

**Do not let this slice silently answer two design questions it stands beside** — whether an artillery marshal should exist on the 1805 board at all, and whether recruiting should be legal on ally soil as substitutes already are. Both must be refused honestly and filed, not resolved inside the slice.

### The slices

---

**R0 — Confirm the surface (15 minutes, blocking).** Ask which surface was clicked. `grep -rn 'do:recruit' godot-client/` returns **1** producer; if it ever returns more, the census in R4 starts there.

> **done_when:** the user has named the surface in writing, on the row.

---

**R1 — The recipient is named (backend payload).** `_region_recruit_price` (`world_state.py:9356`) prices the infantry base with no `marshal=`, no arm, no controller gate and no field cap — while its sibling thirteen lines below, `_region_substitute_price`, already does all four correctly, and its own comment says why. Replace the bare int with a `recruit_here` block derived from the **same selector and same pricer the executor runs**: recipient name, his arm, the gold **he** will be charged, the men who will actually arrive after the CO-4 field cap, the arms that have a recipient in range, and — on refusal — the verdict plus the finished sentence `closed_reason` already writes.

⚠ `_region_substitute_price` looks up "the marshal standing in it" by **exact location**, while the recruit executor uses `find_nearest_marshal_to_region`, which reaches **one province out**. Copying the substitute lookup verbatim quotes the wrong man on 4 of 7 acting provinces. **Use the executor's own selector.**

> **done_when:** a drift pin over all 126 provinces, driving the real `/command` on a fresh funded world per cell, asserts three equalities with **zero** mismatches — `recruit_here.recipient` == the selector's answer; `recruit_here.price` == gold actually charged; `recruit_here.amount` == troops actually delivered. **Measured RED today on all three:** Franche-Comte quotes 872 / charges 1,504; Rhineland quotes 872 / charges 741; every province quotes `infantry_amount` 10,000 while delivering 3,000.

---

**R2 — The arm is a selection key (the one mechanics change).** Add an optional `arm=None` to `find_nearest_marshal_to_region`. With `arm=None` the sort key is exactly today's `(distance, -strength)`, byte-identical. When `_execute_recruit` has **no `marshal`** and **has a `requested_type`**, pass the arm: candidates of that arm sort first, then distance, then strength. If no candidate of the requested arm is in range, **refuse** — naming who *is* in range and what he commands, spending nothing — never silently substitute. The marshal-named branch (`economy_executor.py:783-788`) is untouched. **Write the argument for the distinction at the seam in code**, or the next reader reverts it.

> **done_when:** all eight measured on funded fresh 1805 worlds through `POST /command` —
> 1. `recruit cavalry in Rhineland` → `{'cavalry': -3000}` via Murat *(today: `{'infantry': -3000}` via Davout, 741g)*
> 2. `recruit infantry in Franche-Comte` → `{'infantry': -3000}` via Lannes at 872g *(today: `{'cavalry': -3000}` via Murat at 1,504g)*
> 3. `recruit artillery in <each of the 7 acting provinces>` refused, gold and both AP byte-identical *(today: silently delivers infantry or cavalry at full price on all 7)*
> 4. `Davout, recruit cavalry` still delivers infantry with the Berthier note; `test_pf7_recruit_arm_amount_bombard.py` and `test_manpower_pools.py` pass **unedited**
> 5. 126×8 drift pin: `find_nearest_marshal_to_region(r)` with no `arm` returns identical `(name, distance)` vs pre-slice HEAD
> 6. AST census over `backend/ai/**`: every `{"action": "recruit"}` literal carries an explicit `marshal` — **with a sensitivity arm** that deletes the key in a copied tree and shows the census red
> 7. `BASELINE_SERIES` and M1–M7 byte-identical **without re-record**, and the landing record **states the reason** (the AI never enters the province branch) rather than presenting byte-identity as proof
> 8. negative control: with `requested_type=None`, the delivered arm on all 30 chip provinces is unchanged from HEAD
> 9. **the positive artillery case (added September 22, 2026 after the user asked whether recruit would work for a gun marshal):** on a funded fresh world, `commission Marmont` (he arrives at Paris as an artillery commander with a 3,000 corps — measured), then `recruit artillery in Paris` → `{'artillery': -3000}` **via Marmont** at the capital price, and `Marmont, recruit artillery` the same. The artillery chip on Paris is ENABLED naming Marmont and his price; on every other province it stays a refusal whose remedy is DERIVED from the board, never hard-coded — `commission Marmont (4500g)` while no gun marshal stands, `march Marmont there` / `Marmont, recruit artillery` once one does. Senarmont is the second gun marshal on the bench; the same pin runs on him.

---

**R3 — The chip tells the truth (client).** Three edits in `region_panel.gd`:

1. **Gate the recruit row on the recruit gate, not the substitute gate.** `feeds_us` at `:265-268` opens the row on `substitute_price_here > 0`, which is why Franconia and Milan render six permanently-dead chips.
2. **One chip per arm, enabled only where `recruit_here` names a recipient of that arm** — so the artillery chip lights up on Marmont's or Senarmont's province the moment he is commissioned (R2 item 9), otherwise `Utils.bb_chip_disabled` with the stated reason — the idiom already used twice in this file and never on this row.
3. **The enabled chip states its terms** — the man, his arm, the gold he will be charged, the men who will arrive. This is exactly the discipline the Substitutes chip eleven lines below already applies, with its own comment explaining why:

```gdscript
# region_panel.gd:310-312
# The marshal standing here is the one the substitutes join, and the
# one the backend priced (Intendance is per-marshal), so the chip
# names him rather than sending a bare verb the parser must guess at.
```

Every reason string comes from the payload; nothing is re-derived in GDScript.

> **done_when:** reproducing the panel's own gate against the boot payload — **zero** chips enabled-and-refusing *(today 69 of 90)* and **zero** enabled-and-wrong-arm *(today 14 of 21)*. Milan and Franconia render disabled carrying the backend's own sentence. Godot import+parse harness exits 0; boot smoke shows 0 `SCRIPT ERROR`. The terminal transcript and up-arrow history record a command that does what it says.

---

**R4 — The chip-honesty census (the generalised class).** For every `do:` template across the 7 chip-producing `.gd` files, extract the command string, drive it at the real `/command`, and assert every parameter named in the template is honoured. Dispose the four live siblings in §3 — each either fixed or carrying a written disclosure at its own chip, in the NV-12 idiom.

> **done_when:** every `do:` template enumerated with **0 unreviewed rows**; the census is a **pin that drives the composed strings, not a grep**; a mutation sweep kills every new pin with **0 INERT**.

---

**R6 — The pins: driven, not censused.** One new file, `tests/test_recruit_chip_names_the_man.py`. Every pin asserts the **effect** — the `manpower_pools` delta key, the gold delta, the AP delta — never a message substring. (`test_cx3_the_predictor.py`'s executor census asserts on message substrings and would pass green through every refusal family it exists to catch.) The chip string is **extracted by regex from `region_panel.gd`**, so an edit to the template cannot leave the pin green.

Add one golden-corpus row for the chip's **own** string form `recruit cavalry in Rhineland`. Today the corpus has 5 recruit rows and **none uses the `in <region>` chip form** — all use `at` or `for`. The existing row `recruit cavalry at Lyon` pins only the **parse**, never the delivered arm. **Nothing in the suite pins the current behaviour as intended**, so the fix is not fighting a pin, and that corpus row is already the right shape to extend.

> **done_when:** six pins, each shown **RED against pre-slice HEAD** before it goes green; mutation sweep kills every mutant with **0 INERT** — and any pin returning INERT is treated as a real weakness in the pin until proven otherwise.

---

## 5. Legibility riders worth folding in

All six are cheap and sit on surfaces the row already touches.

**1. The marshal row never names the arm.** `region_panel.gd:_format_marshal_row` has **zero** occurrences of `arm` — the only `arm` in the file is the loop variable for the three chips. Yet the payload already carries it for every marshal — measured:

```
{'name': 'Lannes', 'nation': 'France', 'arm': 'infantry', 'strength': 18000}
```

So the player cannot see that Murat is the cavalryman and Lannes the infantryman standing in the same province. *(Handle the fourth value: Napoleon's `arm` reads `emperor`.)*

**2. The commission bench is arm-blind.** `marshal_management.gd:342` branches only on `cavalry`:

```gdscript
if c.get("cavalry", false):
    bbcode += "  " + _unit_icon("Cavalry", ...) + " [Cavalry]"
```

France's bench is **5 infantry + 2 artillery + 0 cavalry** (Marmont and Senarmont are the gun marshals) — and both render untagged, under an "Infantry pool" header promising a 5,000 corps. The payload ships per-candidate `arm`, per-candidate `corps` and all three `pools`. **This is a client-only fix with no backend change.**

**3. State the pool beside each arm chip.** Cavalry **15,000** against infantry **80,000** is the decision actually being made. With the cavalry pool empty, the **Infantry** chip is refused *for want of cavalry* while 80,000 infantry sit unspent.

**4. The over-the-ordinance line is a warning that reads as a gate.** Measured at boot: `over_by = 59000`, so the panel renders *"59,000 over the ordinance"* in warning colour with **no verb, no price and no arm** — and the chips work anyway, at ×1.45. The block's own comment says the played campaign *"spent ten turns +59,000 over the limit, learned that recruiting was forbidden, and was never told when it stopped being true."* **Say the multiplier.**

**5. The result message hides the two multipliers that dominate the price.** It names the capital discount, the unstable premium and the Intendance, and omits the **×3 war** and **×1.45 ordinance** terms — together **4.36×** of the 741-gold charge.

**6. `levy.open` is a capital fact read on a province surface.** Measured at boot:

```
open                 = False
closed_reason        = No corps stands within reach of the depot at Paris to receive the recruits.
recipient_in_range   = False
```

`open` is **False** while seven provinces' chips succeed — and `closed_reason` is a **finished, honest sentence in Berthier's voice, already on the wire**, which is precisely the reason 63 chips are dead, and the panel reads six keys from that dict and not this one. Either scope these per-province or rename them so the panel cannot read a capital fact as a local one.

**7. When the price does render, its quantity is wrong by 3.3×.** The sentence reads *"872g per 10,000 foot here"* while every measured delivery is **3,000** (*"field levy — no depot; capped at 3,000"*). Any fix that only re-bases the **price** leaves the player reading a number of men they will not get.

---

### One closing measurement, for the artillery refusal's copy

Making the artillery chip an honest refusal on all 126 provinces reads like a new bug unless the copy names the remedy. It does have one, and I verified it:

```
commission Marmont  →  "Marshal Marmont accepts his commission and raises a corps of 3,000 at Paris — 4500g."
   Marmont arm = artillery   loc = Paris
   selector at Paris -> Marmont (artillery)
   pools: artillery 10,000 → 7,000
```

So commissioning Marmont both unlocks artillery **and** un-deadens **Paris** — which was dead only because no French marshal boots within range of the capital.

---

## §CN-1 + CN-2 LANDING RECORD — the backend half (September 22, 2026)

**Status: LANDED on master** (built on `9871fa12`). Row **CQ-3** → FIXED in
`docs/BUG_FIXES.md` §Command-Road Queue. **CN-3 (the chip, client) and CN-4 (the
chip-honesty census) are NEXT** — this commit changes no `.gd`. Pins =
`tests/test_cn_the_chip_names_the_man.py` (32). Sweep = `tools/_sweep_cn_1_2.json`
(**19/19 killed, 0 INERT** on the first run).

### Reproduced first (HEAD `9871fa12`)

The memo's census reproduced to the digit: **30 provinces render the row, 90 chips —
69 refuse, 21 act, 14 of the 21 deliver an arm the label did not name.** `recruit
cavalry in Rhineland` → 3,000 infantry via Davout, 741g; `recruit infantry in
Franche-Comte` (funded) → 3,000 cavalry via Murat, 1,504g, with Lannes (infantry,
872g) standing in the province; `recruit artillery in <any>` → infantry or cavalry at
full price; every province quoted `recruit_price_here` 872 (the infantry base, no
marshal, no arm, no field cap); Paris dead. The positive artillery case already
worked once a gun marshal stood there (`commission Marmont` → `recruit artillery in
Paris` → 3,000 guns via Marmont, 1,329g) — but nothing told the player so, and Paris
quoted 675.

### Decisions (taken under the delegated grant, each with its reason)

1. **CN-2 — the arm is a SELECTION KEY where the game chooses the man, never an
   override on a man the player named.** `find_nearest_marshal_to_region(region,
   arm=None)`: with an arm, only a marshal of that arm is chosen, nearest first; none
   in range → a refusal that names who IS in range and what he commands, the remedy,
   and "Nothing was spent." `arm=None` is the pre-slice rule, pinned byte-identical
   against the old algorithm on 126 provinces × 9 boards. Both no-marshal branches
   (`in <province>` and the capital) take the key. Lever
   `economy_executor.THE_ARM_CHOOSES_THE_MAN`.
2. **The named road stays PF-7's surfaced correction** (this memo's R2 item 4):
   `Davout, recruit cavalry` raises his infantry and says so first;
   `test_pf7_recruit_arm_amount_bombard.py` passes unedited. ⚠ **Correction to
   STATUS ruling D1**, which said CN-1/CN-2 "close both roads": they close the
   province road (the chip and its typed twin); the NAMED road is PF-7's deliberate
   design and is not a wrong purchase in the same sense — the player named the man,
   whose corps IS his arm. **Re-open condition:** if the user would rather the named
   mismatch refuse (spending nothing) than surface, that is one branch in
   `_execute_recruit` plus a conscious flip of PF-7's
   `test_arm_mismatch_soft_correction_fires_for_artillery`.
3. **CN-1 — one quote, the executor's own steps.** `economy_executor.recruit_quote`
   runs the executor's selector (the new PURE `WorldState.ready_marshals_near`, which
   `find_nearest_marshal_to_region` is now built on, so the two cannot disagree and
   the payload never disturbs the refusal reason the selector stashes), gates, CO-4
   field cap, pool check, pricer (with the recipient's Intendance) and treasury check,
   in the executor's order; the executor refuses through the SAME message builders.
   **The drift pin drives the real `/command` on all 126 provinces × (no arm + three
   arms)**: every refusal reads the quote's sentence byte-for-byte and changes nothing;
   every acting cell matches recipient, gold, men and arm.
4. **The payload.** `map_data[p]["recruit_here"]` = the three arm quotes, built ONLY
   where the row renders (own soil, and friendly soil that feeds a French corps —
   where it carries the executor's refusal, ruling D5); `{}` elsewhere (GR8: 96
   provinces cost nothing). `recruit_price_here` is kept but made TRUE — what a bare
   `recruit in <province>` charges (the nearest marshal's own arm), 0 where it would
   refuse (Rhineland 741, Franche-Comte 0 at the boot treasury, Paris 0). Both ride
   the existing fog gate. Measured cost: the filtered summary 4.5 → 6.5 ms.
5. **The remedy is derived from the board, never written in** (R2 item 9): the
   NEAREST serving commander of the arm, with the order that reaches him (`'Marmont,
   recruit artillery'`); failing that the cheapest bench candidate of that arm with
   his price (`commission Marmont (4500g)`); failing that the plain fact. After
   `commission Marmont`, the Rhineland artillery refusal names Marmont and never the
   commission; the Paris artillery quote is `ok` via Marmont.
6. **One arm rule.** `world_state.recruit_arm_of` is the arm the levy raises; the
   executor reads it instead of its own if-chain.
7. **Kill criteria both hold.** (1) The no-arm selector is byte-identical (above). (2)
   An AST census over `backend/ai/**` finds every `{"action": "recruit"}` producer
   carrying `marshal` (2 of 2, `enemy_ai.py`) — `prompt_builder`'s few-shot dicts are
   examples, not producers — with a sensitivity arm that deletes the key in a copy and
   goes red. So the AI never enters the arm-keyed branch: GR5 is free and
   **`BASELINE_SERIES` and M1–M7 are byte-identical because the AI never reaches it**,
   not merely because they measured so.
8. **Corpus**: two rows for the chip's own `recruit <arm> in <province>` form (no row
   had used `in`); corpus 711/711 — which pins the PARSE only; the endpoint pins are
   the evidence.

### Measured after

Re-running the census: **0 of 90 chips deliver the wrong arm (was 14)**; the acting
chips are exactly the arms a marshal in range commands (12 — Franche-Comte, Lorraine,
Nivernais, Orleanais, Rhineland infantry+cavalry; Burgundy and Savoy cavalry); every
artillery chip refuses free and names `commission Marmont (4500g)`. 2,161 existing
recruit-family tests pass unedited, including PF-7, the Aug-30 review's price pins and
IQ-10's.

## §CN-3 LANDING RECORD — the chip tells the truth (September 22, 2026)

**Status: LANDED on master** (built on `608c094b`). The client half of row **CQ-3**;
rows **CQ-18** and **CQ-19** found and closed in the build. **CN-4 (the census of every
`do:` template, and the four §3 siblings) is NEXT.** Pins =
`tests/test_cn3_the_chip_tells_the_truth.py` (26 — seven of them DRIVEN: the new
headless harness `tools/cn3_region_panel_harness.gd` runs the real `region_panel.gd` and
`marshal_management.gd` on the live payload, and the pytest sends every `do:recruit` url
the panel rendered through POST /command; they skip without the engine, and a skip is not
a pass). **22 of the 26 fail on the pre-slice tree** — the four that pass are the harness
check and three controls. Sweep = `tools/_sweep_cn_3.json` (**30/30 killed, 0 INERT, 0
BROKEN** — 14 of the mutations are in the two `.gd` files and are killed only by the
driven pins). Evidence frames = `docs/audits/IQ10_REGION_{PARIS,RHINELAND,AMSTERDAM,MILAN}{,_X2}_2026_09_22.png`
(the IQ-10 instrument re-shot at both Interface Scales, 0 `SCRIPT ERROR`; the
`_2026_09_19` frames are the before, where Paris shows three identical chips).

### Reproduced first (HEAD `608c094b`)

CN-1 had made the backend quote every chip, and the client did not read the quote: on
the funded boot payload the row still rendered on `feeds_us` as **90 identical enabled
chips while the quote refused 78 of them** (69 on the 800-gold boot treasury, the memo's
figure). Reading the quotes the chips were about to print then found two defects in CN-2's
own refusals:

- **CQ-18 — the man was asked before the ground.** The arm refusal ran ahead of the
  province's own gates, so `recruit artillery in Milan` — Kingdom of Italy's soil, where no
  French levy is raised (ruling D5) — answered *"No marshal of artillery can reach Milan …
  commission Marmont (4500g)"*, a 4,500-gold remedy for a refusal no commission lifts, while
  the infantry chip beside it said the truth. The order was older than CN on the no-arm road:
  `recruit infantry in Vienna` told the player to march a corps within range of Austria's
  capital, and an own province in unrest with nobody in reach said *"No marshal is available
  … March a corps within range"* — marching one there would not have helped.
- **CQ-19 — a remedy named an order the game refuses.** The "give him the order yourself"
  clause was unconditional: at boot, Paris's infantry refusal told the player *"give him the
  order yourself: 'Massena, recruit infantry'"* — Massena stands on Milan, and that order is
  refused (*"We do not control Milan"*).

### Decisions (taken under the delegated grant, each with its reason)

1. **The row renders where the backend QUOTED it** (`recruit_here` non-empty), not on
   `feeds_us` — the quote is built only on own soil and friendly soil feeding a French corps,
   which is IQ-10's H1 ground, so the row appears exactly where it did and ally soil keeps its
   honest refusal (D5). `feeds_us` now gates the substitute market only. One chip per arm,
   ENABLED iff the quote is `ok` and stating the quote's `terms` (*"Davout · 3,000 foot · 741g
   · field levy (pool 80,000)"*), otherwise `Utils.bb_chip_disabled` beside the quote's
   `short`. **Both strings are the backend's** (`economy_executor._recruit_quote_display`,
   from the quote's own fields); the panel re-derives nothing (the memo's R3). When every arm
   is refused for ONE reason (ally soil, no administrative action, unrest) the reason is said
   once beside three dimmed chips. The chip carries the `short`, not the executor's full
   sentence: the long form is in Berthier's voice and is what the terminal prints if the order
   is typed; the short is the same reason from the same quote.
2. **The ground speaks first (CQ-18).** Where the game chooses the man — a province named, or
   the bare levy at the capital — the province's own gates refuse BEFORE a man is chosen,
   because no marshal can remedy them: ONE source `economy_executor.recruit_ground_refusal`,
   called by the executor's two no-marshal branches and by the quote (whose later gate is
   deleted — a quote has no named road). The NAMED road keeps its order: there the ground is
   the named man's own. **No lever**, deliberately: the drift pin binds the executor and the
   quote together, and a lever would need a second quote path — the thing CN-1 exists to
   prevent. `recruit in Atlantis` now says *"Unknown region: Atlantis"* on both.
3. **A remedy is an order the game takes (CQ-19).** The "give him the order yourself"
   clause is offered only where the named man's own ground would levy; the man named is still
   the NEAREST (CN-2's pinned rule). Considered and rejected: preferring the nearest man on
   levying ground — it would name a farther man for the march half, and "nearest" is pinned.
   The pin collects every order any refusal on the board quotes and drives each one: all act.
4. **Rider 1 — the marshal row names the arm** — `Ney (24,000 foot)`, `Murat (22,000
   horse)`, and Napoleon's fourth value `emperor` as `(10,000 Guard)`. It reads the payload's
   `arm`, which rides an enemy marshal only at FULL visibility.
5. **Rider 2 — the commission bench tags every arm** with the serving card's own idiom
   (icon + colour for horse and guns, label for foot), states the corps each candidate raises
   (*"a corps of 3,000 guns"*), and the header names all three pools (*"Pools: 80,000 foot ·
   15,000 horse · 10,000 guns"*) instead of the infantry pool alone. The payload always
   carried `arm`, `corps` and `pools`; client-only.
6. **Riders 3, 4 and 7** — the pool rides each enabled chip's terms; the ordinance line says
   its multiplier (*"59,000 over the ordinance — every levy costs ×1.45"*) from the new
   `get_levy_status["ordinance_mult_pct"]`, pinned against the pricer's actual ratio rather
   than its formula (100 on the legacy world, where the pricer does not apply it); the old
   *"872g per 10,000 foot here"* is gone — a field levy delivers 3,000.
7. **Rider 5 — the result names every term.** `_recruit_cost_terms` returns the price AND
   the named terms in the order they compose; `_calculate_recruit_cost` is its price, so every
   caller (the AI's three included) gets the identical number. The result now reads *"Cost:
   741 gold (×3 at war) (×1.45 over the ordinance) (Davout's intendance: -15%)"* — the note
   had named the capital discount and the Intendance and never the two terms that make 4.36×
   of the charge. The legacy world names no war price (N1: it boots at war and is never priced
   for it — pinned).
8. **Rider 6 — disposed, not built.** `levy.open` / `closed_reason` are the capital's facts
   and are named as such where they are read (*"No corps stands within reach of the depot at
   Paris…"*, the headline, the ledger's Manpower tab). The region panel reads no capital fact
   for the recruit row any more — it reads the province's own quotes — so the rider's hazard
   is gone for this surface by construction, and no rename was needed.
9. **The instrument.** `tools/cn3_region_panel_harness.gd` (headless, the real scenes, a
   map-node stand-in copied from IQ-10's MapStub) is added to the committed parse-check list
   (`tools/godot_parse_check.gd` `TOOL_SCRIPTS`), whose stated rule is now *every harness a
   pytest drives* — so CX-7's `cx7_predictor_harness.gd`, driven by
   `test_cx7_predictor_driven.py` and missing from the list, is added too (49 scripts, all
   clean); IQ-10's runner gains a Rhineland shot and CN-3's must-show lines. ⚠ Found in
   passing, not in scope: **twelve older one-off tool harnesses** (`tools/*_screenshot.gd`,
   `wo7_matcher_smoke.gd`, `audio_envelope_probe.gd`, `ux23_r9_audition_render.gd`) are
   driven by no pytest and are not in that list, so a parse error in one surfaces only when
   somebody runs it; recorded here, not fixed.
10. **Two pins flipped consciously**: IQ-10's
    `test_the_panel_branches_on_the_ground_that_feeds_us` (the levy no longer rides
    `feeds_us`) and the Aug-30 review's `test_the_panel_reads_it` (the price rides each arm's
    terms). The second's first cut failed on its own retirement comment — a census must count
    the code, not the prose — and is scoped to code lines. The dead
    `economy_executor.recruit_here` (no caller) is deleted.

### Measured after

On the funded boot payload, through the REAL panel: **12 chips enabled — each acts at POST
/command and raises the arm its label names; 78 dimmed, each beside the backend's reason;
0 enabled-and-refusing (was 78 funded / 69 at the boot treasury); 0 enabled-and-wrong-arm**
(was 14 before CN-2). Milan and Franconia: three dimmed chips and one reason. Every order a
refusal quotes acts. Parse harness EXIT=0 (49 scripts); boot smoke 0 `SCRIPT ERROR`;
the capture harness 0 `SCRIPT ERROR` at both scales; the recruit family (1,672) green;
**`BASELINE_SERIES` and M1–M7 byte-identical without re-record, because the AI never enters
the no-marshal branches** (CN-2's census) and rider 5's pricer returns the same arithmetic.
