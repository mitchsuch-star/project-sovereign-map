# The Petition & Popup Revisit — row CA9-D3 / PC15-10

**v1.1 — authored August 15, 2026 (evaluation session; NOTHING BUILT).**
**✅ THE §6 GATE IS RULED — August 15, 2026, same day, under the user's
delegated grant (*"establish recommendation yourself and commit and push spec
updates"*): all five questions taken at the recommended defaults, ruling
record inline at §6 (authoritative). BUILD MAY PROCEED in the §9 order —
no gate stands between this spec and the build.** v1.0 → v1.1 changed the
gate status only; no fix design changed.

> **Authority chain, in order:**
> 1. `docs/BUG_FIXES.md` §Comprehensive Playtest row **PC15-10** — the measured
>    number this spec answers (19 petitions in 24 turns).
> 2. `docs/DESIGN_REFINEMENT.md` §CA9 Design Answers row **CA9-D3** — the owner
>    row. Its "Done when" is this spec's definition of done: *every producer has
>    a retirement path; nothing blocks a channel indefinitely; the queue order
>    is justified rather than accreted.*
> 3. `docs/audits/CA9_GATE_ANSWERS_2026_08_09.md` §3 — the user's ruling that
>    created the slice ("revisit grievances and popups in general") + the
>    starting list.
> 4. `docs/audits/GRIEVANCE_REVISIT_INVESTIGATION_2026_08_09.md` — the 27-agent
>    row-3 audit. Its Phase A **landed** (see §2); its §5 rulings were taken and
>    built; its §6 prohibitions are carried forward in §5 below, with ONE
>    narrowed on new evidence (§5.2).
> 5. `docs/STATUS.md` Aug-14 health-check entry — the **W7** report-only row
>    (`dialogue_manager.replace()` orphans a hybrid dialogue) homed here.
>
> **This spec extends those records; it does not replace them.** Where this
> file and an older doc disagree about *current code state*, this file is
> correct — every claim below was re-verified against master on August 15,
> 2026 (two read-only audit fleets; all `file:line` cites are from that pass).

---

## §0 What this session did, and what PC15-10 actually is

The user asked for PC15-10 to be evaluated and its fixes documented. PC15-10 is
not a new defect: it is **the measured number attached to the CA9-D3 revisit
slice** — the August-15 comprehensive playtest's flagship arm produced **19
marshal-petition modals in 24 turns** (13 jealousy confrontations, 4 rivalry
events, 2 Fontainebleau), a blocking interrupt on 79% of turns of a winning
multi-marshal campaign. This session:

- re-mined the flagship run's raw artifacts (`tools/playtest_runs/flagship-1805/`)
  for the per-turn / per-kind / per-marshal distribution (§1);
- ran two read-only audit fleets over the petition channel and the whole
  popup/dialogue plumbing (producers, gates, latches, queue slots, drains,
  stash-and-raise tails, load behavior);
- reconciled the results against everything already landed since the Aug-9
  investigation (§2 — much of the old starting list is DONE and must not be
  rebuilt);
- wrote the fix design (§4), the carried prohibitions (§5), the gate questions
  (§6), and the test/acceptance plan (§7–§8).

**Nothing was coded.** The §6 gate was ruled the same day under the user's
delegated grant; the next session builds §4 in the §9 order with no gate
outstanding.

---

## §1 The measured disease

### 1.1 The flagship timeline (re-mined from `digest.jsonl`, August 15)

A petition modal fired on **19 of 24 turns** — exactly one per turn, an
unbroken drip on turns 2–11, 13–18, 20–22. Only turns 1, 12, 19, 23, 24 were
petition-free. Total popups of all kinds: 54 in 24 turns (2.25/turn); the
petition is the largest single popup class (19 of 54).

| Turn | Kind | Petitioner / subject | Driver's answer |
|---|---|---|---|
| 2 | jealousy_confrontation | Murat | acknowledge |
| 3 | jealousy_confrontation | Bernadotte | acknowledge |
| 4 | jealousy_confrontation | Murat | acknowledge |
| 5 | jealousy_confrontation | Ney | acknowledge |
| 6 | jealousy_confrontation | Massena | acknowledge |
| 7 | fontainebleau | collective | concede |
| 8 | jealousy_confrontation | Lannes | acknowledge |
| 9 | jealousy_confrontation | Bernadotte | acknowledge |
| 10 | rivalry_confrontation | (@−2 breach) | accept_breach |
| 11 | jealousy_confrontation | Lannes | acknowledge |
| 13 | jealousy_confrontation | Soult | acknowledge |
| 14 | jealousy_confrontation | Lannes | acknowledge |
| 15 | rivalry_confrontation | (@−2 breach) | accept_breach |
| 16 | jealousy_confrontation | Davout | acknowledge |
| 17 | rivalry_confrontation | (@−2 breach) | accept_breach |
| 18 | fontainebleau | collective | concede |
| 20 | jealousy_confrontation | Davout | acknowledge |
| 21 | rivalry_confrontation | (@−1) | let_be |
| 22 | jealousy_confrontation | Bernadotte | acknowledge |

Per-marshal confrontation counts: Bernadotte ×3, Lannes ×3, Murat ×2,
Davout ×2, Ney, Massena, Soult ×1 — the CA8-D3 per-(pair, level) latch doing
exactly what it was blessed to do (each escalation level gets its audience),
multiplied across the authored web.

**Method caveat, carried honestly:** the driver's stated petition policy is
`"first_enabled"` (`tools/playtest_driver.py:96-98`) — it clicks the first
enabled arm, which is the free "Let it stand" on every confrontation. So the
13 identical `acknowledge` answers are policy, not judgment. But the CA9
played campaign (a human) reported the same lean ("acknowledge seems to do
nothing"), and the structural point survives the caveat: **17 of the 19
modals were answerable by a free arm whose dominant outcome is "nothing
changes."** A blocking interrupt whose default answer is a no-op fails the
modal test — modals are for decisions that must be made *now*.

### 1.2 The two-sided history — starvation and firehose are the same arithmetic

The Aug-9 investigation measured this channel on **passive** runs (nobody
answers): 1 petition served of 32 produced, the single slot permanently
occupied, everything behind it starving. Its §6.2 therefore ruled *"the
measured problem is starvation, not frequency."* The Aug-15 playtest measured
the same channel from the **engaged** side (the driver answers every card):
served at full rate, it is a modal on 4 turns of every 5.

Both are one fact: **supply ≈ 2.3 candidate petitions per turn against a
channel that serves exactly one card per player answer, with no budget
constant anywhere in the codebase** (verified: no `PETITION_BUDGET` /
`MAX_PETITIONS*` / per-turn counter exists; the only limiter is the single
slot plus four per-producer latches). A passive player sees a backlog; an
engaged player sees a drip that never ends. The Aug-9 content fixes (§2) made
the cards *worth answering* — which converted the starvation presentation of
the disease into the firehose presentation. The volume was never treated.

---

## §2 What already landed — do NOT rebuild (verified against master Aug 15)

The old starting list is more than half done. The build session must treat
these as fixed and pinned:

| Old row | Status on master | Evidence |
|---|---|---|
| **N4** "never expires, never re-validates, answered against live state" | **Half fixed.** A3 stale-answer guard re-validates `context["target"]` vs `marshal.jealous_of` for confrontations and retires stale cards unspent (`jealousy.py:2287-2294`); PT-A1 made retirement success-gated + identity-checked (`:2167-2172`) and a refusal re-attaches the refreshed card (`:2173-2180`); affordability is re-derived at every delivery (`refresh_petition_affordability` `:1662-1743`, called at `main.py:1473-1480`). **Residue = F2/F3/F10:** no expiry of any kind (the re-push at `:2743-2744` is unconditional and eternal), the guard covers ONE of four kinds, and the loaded petition is invisible until the next end-turn (§4-F10). |
| **N8** "Separate Them is a permanent un-cancellable subscription" | **Fixed** (A9): retirement when the stored pair mends (`jealousy.py:2999-3013`) + `SEPARATION_WARNING_COOLDOWN = 4` on the proximity nag (`:130`, `:3018-3021`). **Residue = F5c:** the *retirement* line is narration-exempt and uncooldowned — a bulk mend emits one bullet per pair. |
| **N21** "the drama channel has no dispatch budget" | **Half fixed** (A13): `JEALOUSY_DISPATCH_CAP = 3` + ranked overflow tail (`:2636`, `:2673-2710`). **Residue:** the cap governs a *minority* of volume — exempt classes (crowns, earned resolutions, separation lines, tier-2 escalations, autonomous warnings) can still stack ~19 lines on a hot 7-marshal turn, and one exemption is silently broken (§4-F5a). |
| **A4** war-weary producer clobbering a pending confrontation | **Fixed** — occupancy skip + stamp-after-push (`diplomatic_executor.py:2286-2295`). |
| **A10** the four unserialized dynamic latches | **Fixed** — `war_weary_petitions_seen` / `fontainebleau_armed` / `fontainebleau_last_turn` all declared, serialized, restored (`world_state.py:694/698/874`, `:6391-6393/6437`, `:6914-6917/7054-7055`); marshal-side `jealousy_rebuked_cycle` / `literal_intel_paused_turn` / `jealousy_escalation_hold` serialized (`marshal.py:1522-1526`, `:1711-1718`). |
| Q1(b)/Q2(a)/Q3(b)/Q4(a)/Q5(c) | **All built** — promise holds the escalation level (`CONFRONT_PROMISE_HOLD_TURNS = 6`), the command arm exists at 2 AP (1 literal) with honest availability re-derived at answer time, first grievance on a stored-Rival pair gets a first act (`ESCALATION_RIVAL_FIRES = 2`), mend arms clamp at the authored floor, the `modify_relationship` writer deliberately untouched pending a playtest re-open. |
| PT-G3 / A14 / PT-F3 | **Built** — rotated per-personality petition bodies, `speaker_line` on every kind, rivalry arms priced with authority-banded odds read off the resolver's own value. |
| **PC15-17** stale popups at load | **Fixed for ONE slot** — `vassal_rebellion_imminent` gets an on-load validity sweep (`world_state.py:7644-7671`). It is the **only** slot with one; F10 generalizes it. |
| "The objection layer carries per-turn state on the module-global executor" (added to the list Aug 9) | **REFUTED on current master.** `major_objections_this_turn` lives on the per-world `world.disobedience_system` (`world_state.py:841`), is reset on every turn advance (`disobedience.py:672-674` called from `world_state.py:9016`), and is serialized (`:6469`/`:7106`). The sibling `objection_popups_this_turn` likewise (`:886`, reset `:8574`). Every consumer reaches through `world.` — the module-global `executor` holds no objection state. The audit item RETIRES; pin the reset site so it cannot regress silently (§7). |

**Consequence:** the slice's remaining work is (1) the volume/cadence design
PC15-10 measured — the one thing no prior pass touched — and (2) the
structural queue items no prior pass owned (W7, drains, stash-and-raise,
order audit, load sweep), plus a short list of latent bugs both audit fleets
found this session (§4-F5).

---

## §3 Root cause — why 19-in-24 is the system working exactly as built

### 3.1 The supply side (why ~1 candidate per turn, forever)

- **Seven of France's 21 authored pairs are hair-trigger.** `THRESHOLDS = {2:
  None, 1: 4, 0: 2, -1: 1, -2: 1}` (`jealousy.py:62`) and the DR-3 ruling
  deliberately exempts `base == 1` pairs from the winning-calm `+1`
  (`:552-558`) — so 5 Rival + 2 Hostile pairs fire on a **one-point glory
  gap even at the height of empire.** That exemption is blessed design (it is
  what un-starved marshal drama in Phase 3); this spec does not touch it.
- **A hot pair cycles in ~3 turns**: duration `2 + (delta − threshold)` gives
  2 turns at delta 1 / threshold 1 (`:604-606`), plus one turn of same-pass
  refire suppression (`:2840-2842`). Seven pairs × 24 turns ÷ 3 ≈ **56 fire
  opportunities**, throttled to ≤2 fires/nation/turn (`:82`, `:2851`).
- **The CA8-D3 latch multiplies the per-pair petition budget ×4** — keys
  `pair@L0..L3` (`:829`), 26 reachable keys on the hot subset alone (the two
  hostile pairs skip L0 — §4-F5, S5). Rival memory (`:139`) concentrates
  fires on the same seven pairs, so fires land on *keys* rather than
  dispersing.
- Measured: the 13 flagship confrontations ≈ the first ~1.9 rungs of the
  26-key hot budget. **The campaign ran out of turns before the channel ran
  out of keys.** Rivalry adds ≤2 keys/pair on downward transitions;
  Fontainebleau adds `floor(24/8) = 3` maximum (2 fired); war-weary added 0
  (France already at war with everyone it would attack).

### 3.2 The service side (why every candidate becomes an interrupt)

One slot (`world.pending_marshal_petition`, `world_state.py:867`), freed only
by a successful answer (`jealousy.py:2167-2172`), re-pushed every turn forever
(`:2743-2744`), delivered as a blocking modal via PopupQueue slot 6 of 11
(`cooldown_manager.py:157`) → `marshal_petition_dialog.tscn` (layer 114,
registered modal). The ceiling is therefore **one modal per player answer** —
and an engaged player answers instantly, so the channel serves at exactly the
supply rate. There is no tier, no batching, no non-blocking route: a level-0
"he seems put out" and a level-3 "the feud is now mutual and the army knows
it" are delivered with identical interruption weight.

### 3.3 The classification error, stated once

The petition CONTENT is good (the Aug-9 investigation's fantasy lens scored
it highest; the arms now state real prices and one arm — the command — grants
what the man asks). The petition's **interrupt class** is wrong for its
routine tier. Sixteen of nineteen modals were "routine court friction whose
correct default is to let it stand"; three were genuine drama (the @−2
breaches; the collective Fontainebleau). The fix is not fewer audiences — the
CA8-D3 contract that *every escalation level gets its audience* stands — it
is that **routine audiences must stop being interrupts.**

### 3.4 The producers, condensed (full census in the session's audit record)

| Producer | Trigger | Latch (per campaign) | When channel occupied | Loss mode |
|---|---|---|---|---|
| §6 confrontation (`apply_jealousy:825-834` → `queue_confrontation_petition:1770`) | player pair fires, level's key unseen | `pair@L{level}`, ≤4/pair (hostile pairs 3 — L0 unreachable) | skip, key NOT stamped → retries on next fire of that pair at that level | **rung-skip**: if the level advances before the next fire, that rung's card never serves |
| §6b rivalry (`check_rivalry_transitions:1356-1412` → `queue_rivalry_petition:1910`) | stored (or derived — §4-F5b) value transitions down to −1/−2, player pair | `pair@{value}`, ≤2/pair | skip, key not stamped | **effectively lost** — a transition is an event, not a state; it recurs only if the pair mends and re-breaks |
| ESP-1 Fontainebleau (`check_fontainebleau:2025-2053`) | ≥3 player marshals eroding | armed-latch + 8-turn cooldown, both written AFTER the occupancy check | genuinely retries next turn | none (the only clean retry) |
| ESP-2 war-weary (`diplomatic_executor.py:2258-2301`) | player declares a NEW war while a satisfied ≥160-expectation marshal stands | `marshal\|nation`, stamp after push | skip; the war declares unopposed | **lost for that declaration** (state moves to WAR) |

Plus the re-pusher (`process_turn:2743-2744`) and the delivery-time
affordability refresh. All four producers are player-nation-gated — **the
whole petition channel is player-side**, which bounds the `BASELINE_SERIES`
risk of everything in §4 (see §7).

---

## §4 The fix design

Ten fixes. F1 is the centerpiece; its gate questions were **RULED at the
recommended defaults** (§6). F5–F8 and F10 are gate-free mechanical
corrections; F2/F3's sub-questions are likewise ruled; F9 is gate-free `.gd`
engineering. Mapping to the owner row's "Done when": *retirement paths* =
F2 + F10 · *nothing blocks indefinitely* = F1 + F3 + F4 · *order justified*
= F8.

### F1 — "The Antechamber": the tier split (✅ RULED — §6 Q1(a)/Q2(a))

**Rule:** every petition is classified at build time as **AUDIENCE** (routine)
or **CRISIS** (drama). Crisis petitions keep today's path unchanged — the
PopupQueue slot, the blocking modal, the stash-and-raise discipline. Audience
petitions stop interrupting: they are announced by a **persistent
notification + a Generals-screen chip** and the player opens the SAME card
from there at a moment of their choosing.

**The tier table (Q1 — RULED as tabled):**

| Kind | Tier | Why |
|---|---|---|
| jealousy_confrontation L0, L1 | **AUDIENCE** | routine court friction; the free "Let it stand" is its honest default |
| jealousy_confrontation L2 | **CRISIS** | the permanent-damage moment ("the wound will not close on its own") |
| jealousy_confrontation L3 | **CRISIS** | the mutual feud asks where the Emperor stands |
| rivalry @−1 | **AUDIENCE** | harsh words before the staff |
| rivalry @−2 | **CRISIS** | "the breach may be beyond repair" |
| fontainebleau | **CRISIS** | collective, rare (8-turn cooldown), treasury-scale stakes |
| war_weary | **CRISIS** (unchanged by nature) | synchronous with the player's own declare-war command — an interlock, not an ambient interrupt |

**Mechanics, exactly:**

1. `tier` is a new **key inside the already-serialized petition dict**
   (precedent: `jealousy_history["__levels__"]`) — zero new serialized
   fields. Derived at each `queue_*` builder from the table above; default
   `"crisis"` for any legacy in-flight card (a pre-spec save's pending card
   stays modal — no behavior surprise).
2. `_push_petition` (F4 makes it the single guard) routes by tier: crisis →
   `world.pending_marshal_petition` + PopupQueue push, exactly today;
   audience → `world.pending_marshal_petition` **without** a PopupQueue push,
   plus a notification via the two **already-declared, zero-emitter** types
   `JEALOUSY_CONFRONTATION` / `RIVALRY_CONFRONTATION`
   (`notifications.py:111-112`) — the original v3 design finally wired.
3. The client learns an audience is waiting from the notification rail + a
   chip on the petitioner's Generals card ("⚖ Seeks an audience") and a
   badge on the Generals top-bar button. Chip/notification click → `GET
   /marshal_petition` (new, trivial: returns
   `refresh_petition_affordability(world.pending_marshal_petition, world)` or
   `{"petition": null}`) → opens the **existing**
   `marshal_petition_dialog.tscn` with the existing payload shape. `POST
   /marshal_petition_response` is byte-identical for both tiers.
4. **Contention rule:** one card at a time remains the law. Audience-vs-
   audience: skip-unstamped (today's semantics — the next fire re-queues).
   Crisis-vs-audience: the crisis **evicts** the audience card AND un-stamps
   its latch key (removes `pair@Ln` from `jealousy_confrontations_seen` /
   the `@−1` key from `rivalry_transitions_seen`), so the evicted audience
   returns on the pair's next fire instead of being deleted — the CA8-D3
   "every level gets its audience" contract is *strengthened*, not weakened,
   by F1 (today an occupied channel can delete beats; see §3.4 loss column).
   Crisis-vs-crisis: skip-unstamped, as today.
5. **Supersede rule:** a newer petition for the same pair retires the older
   one silently (its content is subsumed — an L1 audience still unread when
   the pair reaches L2 yields to the L2 crisis card; serving L1 prose against
   L3 state is the S7 defect, closed here at the source).
6. Dormancy: audiences ride `_push_petition`, so the TUT-F5 belt
   (`jealousy.py:1654`) already covers them; the notification emitter sits
   inside `_push_petition` behind the same belt. The tutorial world never
   shows a chip.
7. The dispatch keeps announcing arrivals either way (`fontainebleau_petition`
   event today; audiences gain a capped routine line "X seeks an audience —
   the Generals screen has the particulars"), so a player who never opens the
   Generals screen still *hears* the court.

**Measured expectation (from §1.1 data):** crisis ≈ 3 rivalry @−2 + 2
Fontainebleau + the L2/L3 subset of the 13 confrontations (≈2–4 by rung
arithmetic; the digest does not record levels) ≈ **7–9 blocking modals in 24
turns — one every ~3 turns** — with the remaining ~10–12 audiences on the
chip at the player's pleasure. That is the acceptance band in §8.

**What F1 deliberately does NOT do:** no petition is dropped, no latch
budget shrinks, no trigger threshold moves, no fire cadence changes. The
supply arithmetic of §3.1 is untouched — only the interrupt class of the
routine tier changes. (This is what keeps `BASELINE_SERIES` byte-identical by
construction: fires, latches, and `jealous_of` writes are unchanged; only
delivery routing and player-side seen-list contents in the eviction edge case
move, and every producer is player-nation-gated. Verify, do not assume — §7.)

### F2 — Subject-linked retirement (the N4 "TTL" answer; Q3 ✅ CONFIRMED)

**No numeric TTL.** A petition expires when **its subject dies**, checked at
the one seam that already touches every unanswered card each turn — the
re-push (`process_turn:2743-2744`). Replace the unconditional re-push with
`if petition_still_stands(world, petition): re-push; else: retire + receipt`:

| Kind | `petition_still_stands` predicate (mirrors the A3 guard per kind) |
|---|---|
| jealousy_confrontation | marshal exists, standing, `jealous_of == context["target"]` |
| rivalry_confrontation | both exist + standing, stored value between them still ≤ `context["new_value"]` (a mended pair's card retires) |
| fontainebleau | ≥1 named petitioner still eroding (all provided for → retire) |
| war_weary | target nation still not at WAR (war started another way → retire; the stored declare-war command dies with it) |

Retirement clears the slot AND the queue copy (`queue.set(...)`, the
`:2168-2172` idiom) and emits ONE routine dispatch line — the receipt:
*"Berthier notes {name} no longer presses the matter."* Nothing retires
silently — that is the CA9 through-line applied to this channel (a surface
must never keep asserting what the state no longer supports, and a state
change must never eat a surface without a word).

Also close **S7** here: `context["escalation_level"]` is write-only today
(stamped `:1864`, never read at answer time) — under F1's supersede rule the
stale-rung card is retired instead of served, which is the fix; add the pin
that a card whose stamped level differs from the live level never serves.

### F3 — No silent losses (gate-free)

The two remaining loss modes (§3.4) get **narration fallbacks**, not new
queue machinery:

- **Rivalry blocked-when-occupied** (`:1383-1384` `continue`): the moment is
  lost as a *card* (a transition cannot recur without a mend-and-re-break —
  and re-deriving it from state is impossible because authored-hostile boot
  pairs never transitioned). Accept the card loss as WAD **and emit the
  dispatch line anyway** ("Harsh words between X and Y before the general
  staff") so the moment is never silent. Pin the WAD.
- **War-weary blocked-when-occupied** (`diplomatic_executor.py:2286-2288`):
  the war proceeds; add one dispatch line ("{name} bit back his counsel as
  the order went out") so the player learns the objection existed. Key
  deliberately NOT stamped (already the case) — he keeps it for the next war.

Under F1 both windows shrink to crisis-vs-crisis collisions (rare — the
flagship had zero), so these are honesty patches, not capacity fixes.

### F4 — Centralize the occupancy guard (gate-free)

`_push_petition` (`jealousy.py:1650-1659`) overwrites unconditionally; the
guard exists as **four divergent copies** at the call sites (`:831`,
`:1383`, `:2043`, `diplomatic_executor.py:2286-2288`) — and ESP-2 shipped
without one for a month (the A4 comment records the production bug). Move the
occupancy/tier/eviction decision INTO `_push_petition`; have it return an
enum (`queued` / `blocked` / `evicted_audience` / `superseded`) the producers
branch on for their latch stamps (stamp only on `queued` — which also closes
**S8**'s residual: the `_ww_seen` stamp can currently burn on a world where
the dormancy belt swallowed the push). Producers keep their own *trigger*
latches; they stop carrying channel policy.

### F5 — Latent bugs found by this session's audits (gate-free; fix-now)

1. **S1 — the mutual-spiral beat is silently cappable.** The level-3
   escalation event (`jealousy.py:989-999`) carries no `"level"` key, so the
   drama-cap exemption test `int(event.get("level") or 0) >=
   JEALOUSY_EXEMPT_ESCALATION_LEVEL` (`:2686-2690`) reads 0 and files the
   channel's single most dramatic sentence under *routine*, collapsible into
   the "…further matters" tail — directly contradicting the documented
   exemption at `:2648-2652`. One key + a never-collapsed pin.
2. **S4 — the two rivalry call chains disagree on what `new_value` means.**
   The battle path passes the **derived** value
   (`relationship.py:200` → `get_relationship`, which subtracts 1 for a live
   grievance) while the escalation path passes **stored**
   (`jealousy.py:967/:971`) — so a battle-path transition can queue the @−2
   card and stamp the @−2 latch key for a pair whose stored standing is −1.
   Normalize inside `check_rivalry_transitions` (re-read stored for the
   pair at `:1367`); the function is player-pair-gated (`:1376-1378`) so the
   fix cannot move AI behavior.
3. **S6 — the separation retirement line is exempt AND uncooldowned**
   (`:3004-3012`, type `jealousy_separation_warning` ∈ exempt tuple
   `:2643`). Bulk-mend turns emit one bullet per pair. Collapse same-turn
   retirements into one line naming ≤2 pairs + a count.
4. **S9/N4b — a loaded petition is invisible until the next end turn.**
   `pending_marshal_petition` is the only PRIORITY_ORDER member that is a
   plain attribute, not a queue-backed property (`world_state.py:867`); load
   restores the field (`:7049`) but never re-primes the queue, so the card
   cannot be delivered until `process_turn:2744` runs again. Re-prime in
   `from_dict` (crisis tier only, under F1). The existing round-trip pin
   (`test_jealousy_v32.py:800-805`) stays green; add the delivery pin. Also
   correct the false comment at `main.py:1448` — "Golden Rule 4: already
   cleared by pop" does not hold for slot 5, whose durable state is the
   world field.
5. **S5 — hostile pairs never see the mild register** (stored ≤ −2 escalates
   on the first fire, so `@L0` is unreachable and their first-ever card opens
   at "the staff now speak of the quarrel openly"). Under F1 this becomes
   *correct* (a boot-hostile pair's first card SHOULD be hotter); record it
   as design at the seam rather than fixing it.

### F6 — W7: `preempt()` for hybrid dialogues + `dialogue_id` on hybrid popups (gate-free)

The confirmed trace: a `vassal_rebellion_imminent` HYBRID dialogue
(`vassal.py:668`, hybrid per `dialogue_manager.py:123-126`) does not block
commands (`is_hard_stop` False → `executor.py:641` admits the order), so a
`declare war` can reach `diplomatic_executor.py:2325`, whose
`dialogue_manager.replace()` **destroys** the displaced dialogue
(`dialogue_manager.py:231-259` — never queued). The rebellion *popup* slot
survives and is answered against whatever dialogue is now current — the arms
read the ally-entry review's context, get `vassal_name == ""`, and
`pop()` destroys THAT dialogue too (`diplomatic_executor.py:5446-5450`).

- **Fix (a):** when the displaced current is a HYBRID type, call the
  queue-preserving **`preempt()`** (`dialogue_manager.py:261-284`) instead of
  `replace()`. It already has two production call sites
  (`clarification.py:452`, `settlement_staging.py:3584`) — the precedent is
  established; the hybrid-displacing `replace()` at
  `diplomatic_executor.py:2325` simply never adopted it. Audit the other
  `replace()` call sites for the same rule.
- **Fix (b), the aggravator:** the two hybrid popup answer paths send no
  `dialogue_id` (`main.gd:4535`, `:4550`; `api_client.gd:234-237` omits the
  default −1), so the W6-0 stale-dialogue binding
  (`diplomatic_executor.py:3312-3341`) can never protect them. Stamp the id
  on the popup payloads (the overflow dict at `vassal.py:657` is a *separate*
  dict from the dialogue — `_assign_dialogue_id`'s mirror at
  `dialogue_manager.py:208-210` never reaches it) and send it from both
  handlers.
- Note in the blocking-class table that `settlement_confirm` is a
  **conditional** hard stop (`is_hard_stop` returns False in PROPOSE mode,
  `dialogue_manager.py:330-334`) — documentation, not a change.

### F7 — Close the drain family, structurally (gate-free)

Three surviving IGR-X7-class defects (the Aug-14 health check fixed five;
these remain), then the pin that ends the class:

1. **`POST /load` destroys one restored popup per load.** The endpoint uses
   the draining builder (`main.py:3828`) while its client handler
   (`_apply_world_swap_response`, `main.gd:3912-3931`) reads no popup keys —
   the highest-priority popup restored by `from_dict` (`world_state.py:
   7633-7682`) is popped into a response nobody renders. → `drain_popups=
   False` + key fill.
2. **`POST /strategic_response` drains everything; the client stashes only
   the diorama** (`main.py:3507` default drain; `main.gd:4249-4266`). A
   Proclamation delivered on that response is **lost forever** — the
   formation latch means it never re-fires. → non-drain + fill (the popups
   then deliver on the next `/command`), or adopt the full stash quartet in
   `_on_interrupt_response`; prefer non-drain (smaller).
3. **`POST /mailbox/activate` writes into the queue without draining**
   (`main.py:4224` sets `world.incoming_proposal_popup = popup` AND `:4225`
   returns the payload the client shows immediately) — the queue copy is
   delivered AGAIN by the next `/command`. → return-only; do not write the
   world field (verify the PL-14 safety-valve at `main.py:1487-1494` reads
   `pending_diplomatic_dialogue`, not this field — it does).
4. **The structural pin:** a census test over `main.py`'s route table
   asserting every POST handler appears in an explicit
   `DRAINING_ROUTES` / `NON_DRAINING_ROUTES` allowlist (house pattern: the
   IGR-E call-site census). A new endpoint that forgets to declare itself
   fails the suite instead of shipping the fourth generation of this bug.

### F8 — The PopupQueue order, justified (Q5 ✅ RULED — both removals confirmed)

The audit found the ORDER itself defensible but the list dirty. The justified
table becomes a comment block at `PRIORITY_ORDER` (`cooldown_manager.py:
145-163`) and the spec's record:

| # | Slot | Justification (why above the next) |
|---|---|---|
| 1 | `diplomatic_sabotage_popup` | an active betrayal discovery outranks everything routine |
| 2 | `vassal_rebellion_imminent_popup` | a state about to leave the empire |
| 3 | `proclamation_popup` | a nation being born waits for a rebellion, not for mail (NA-6 §11.10-5, standing) |
| 4 | `diplomatic_objection_popup` | Talleyrand blocking a command the player just gave |
| 5 | `pending_marshal_petition` (crisis tier only, post-F1) | marshal drama outranks routine mail |
| 6 | `incoming_proposal_popup` | current-turn envoys (lapse at end of turn) |
| 7 | `incoming_settlement_offer_popup` | persistent mail — outwaits the envoys (SC-5, standing) |
| 8 | `proposal_result_popup` | receipts come last |
| 9 | `commitment_paradox_popup` | modal follow-up, self-ordering |

Two removals, both **conscious pin flips** (`len == 11` pinned at
`test_cooldown_popup_manager.py:452` + `test_igr_f_envoy_digest.py:818`;
order pinned at `test_nation_agendas_formables.py:951-956`):

- **`coalition_popup` (currently priority 0) is a dead slot** — no producer
  writes the world field (`coalition.py:1676` builds a local returned in the
  result; the client migrated to the notice rail per `main.gd:1865-1866`).
  Remove the slot; keep the game-over/load sweeps tolerant.
- **`alliance_paradox_popup` (index 10) is unreachable** — it canonicalizes
  to `commitment_paradox_popup` (`LEGACY_ALIASES:136-138`), which the `seen`
  set consumed at index 9 (`:201-206`). Remove the ORDER entry; **keep the
  alias map** (legacy saves still push under the old name).

**Verify-then-decide (not prescribed):** the `proposal_result` response key
appears to have **no `.gd` reader** (nine backend producers;
`dialog_manager.gd:30-31` documents the scene as an unregistered orphan; the
`_apply_command_popup_contract` bypass at `main.py:1250-1264` hand-delivers
it too). If proposal outcomes genuinely reach the player only via terminal
message text, either wire the key or retire it and its queue slot —
**measure in the client first**; the flagship digest shows the key delivered
3× (the driver reads keys; a human may be reading prose). Also fold the
bypass itself (`_apply_command_popup_contract` drains two slots outside
`pop_highest`) into the documented contract.

### F9 — Stash-and-raise becomes one chokepoint (gate-free, `.gd`)

The discipline is applied per-surface and diverges today: 4 stashers with 5
call sites; **only 2 of ~14 control-return tails run the full raise chain**
(`_return_control_to_player` `main.gd:1638-1658` and the `_on_command_result`
tail `:1994-2011`); four tails raise the diorama alone (`:3500`, `:3832`,
`:4086`, `:4338`); `_on_mailbox_panel_closed` (`:4859-4867`) and
`_apply_world_swap_response` (`:3912-3931`) raise nothing; and
`_on_interrupt_response` (`:4249-4266`) is an independent copy of the routing
contract that stashes one surface of four. This is the "list-wide contract
question" the Aug-9 investigation filed OUT with no owner — owned here:

- Extract `_stash_pending_surfaces(result)` (the quartet: diorama,
  proclamation, digest, redemption) and `_raise_pending_surfaces()` (the
  canonical chain in the canonical order), and call them from EVERY response
  ingest / control-return tail in a named list (`_on_command_result`,
  `_on_interrupt_response`, `_on_objection_response`,
  `_on_capture_choice_response`, `_on_glorious_charge_response`,
  `_on_redemption_response`, `_on_enemy_phase_dismissed`,
  `_on_strategic_report_dismissed`, `_on_mailbox_panel_closed`,
  `_on_battle_diorama_dismissed`, `_on_marshal_petition_deferred`,
  `_on_proclamation_dismissed`, `_process_next_interrupt`,
  `_apply_world_swap_response` — the last clears stashes instead of raising:
  a world swap invalidates them).
- Pin by source grep (house precedent `test_naval_ui_clarity.py`): every tail
  in the list calls the raiser or the clearer; the stale-report caveat from
  the Aug-9 audit applies — extend the parse harness's critical-scripts set
  to include `main.gd`'s petition/stash region if not already covered.

### F10 — Load-time validity, generalized (gate-free)

PC15-17 built the model for ONE slot (`_stale_rebellion_court`,
`world_state.py:7644-7671` — validity check + popup retire + DialogueManager
queue sweep). Generalize: on `from_dict`, after the queue restore, run a
per-slot validity pass — rebellion (exists), petition (F2's
`petition_still_stands` + the S9 re-prime), proposal/settlement offers
(court still exists / war still stands via the existing lapse predicates),
proclamation (formation record still unproclaimed). Each retired popup logs
one campaign-log line (the F2 receipt idiom). Also note `PopupQueue.
to_dict/from_dict` are dead code (persistence rides the nine world
properties) — delete or wire, don't leave the third serialization path
lying next to the two real ones.

---

## §5 What NOT to do — carried forward, and one ruling narrowed

### 5.1 Carried unchanged from the Aug-9 investigation §6 (reasons still hold)

- **No v3 Promise-Glory deadline** (§6.1 — the arithmetic still defeats it).
- **Do not delete "Let it stand"** (§6.4 — the coercion hazard stands; it is
  now priced honestly and that is its whole job).
- **No typed "reconcile X and Y" verb** (§6.7 / Q4 — the mend arms stay
  clamped at the authored floor; character is not launderable).
- **Do not touch the SUPPORT/hostile combat scaling** (§6.6 — the "grim
  Napoleonic tradeoff" reading stands; M1b's harness caveat noted there
  still applies).
- **Q5 (the `modify_relationship` writer) stays deferred** — its re-open
  condition was "after the playtest"; the playtest has now run, so the
  re-open is *available* to the user, but it is a measured
  `BASELINE_SERIES`-moving balance change (diverges at index 20, 21/41
  readings) and is NOT bundled into this slice. Separate ruling if taken.

### 5.2 One ruling narrowed on new evidence

Investigation §6.2 — *"Do not add a campaign-wide petition rarity budget"* —
rested on two reasons: (i) a budget re-creates the CA8-D3 defect (levels
losing their audience), and (ii) *"the measured problem is starvation (1 of
32 served), not frequency."* Reason (ii) is now half-obsolete: the starvation
was measured on passive runs before the channel content was fixed; the
engaged-side measurement (PC15-10) shows the frequency problem is real. Reason
(i) survives **and governs the shape of the fix**: F1 demotes the routine
tier's *interrupt class* without dropping, deferring, or rationing a single
audience — every level still speaks. What stays forbidden, on reason (i),
exactly as before: any **lossy** budget (dropping audiences) and any
**deferral** budget (a deferred card ages into the A3/F2 stale-retirement
path — deferral IS loss in practice, which is also why F1 rejects the
"keep-modal-with-spacing" alternative in §6 Q2(c)).

### 5.3 New prohibitions from this session's evidence

- **Do not touch the DR-3 hair-trigger exemption or `THRESHOLDS`** to damp
  the firehose. The supply side is blessed drama design (M7 rode it from
  *never* to *turn 1*); the disease is the interrupt class, not the ambition.
  Any threshold change moves `BASELINE_SERIES` and re-opens a Phase-3 ruling.
- **Do not give `_push_petition` a queue** (multi-card backlog). One card at
  a time is what keeps the channel legible and the latch arithmetic bounded;
  F1's chip + retry semantics deliver the same throughput without a second
  queue to audit. (If the user prefers the letter-book shape at Q2(b), that
  is a bounded LIST with per-row answers — the IGR-F machinery — not a
  hidden queue behind one slot; the difference is that every queued item is
  *visible*.)
- **Do not batch petition arms into the mailbox's Accept/Decline rows**
  as-is: the confrontation card is a four-arm decision with per-arm honest
  availability — flattening it to two verbs would delete the Q2(a) command
  arm the row-3 gate just built. Any digest shape must open the full card.

---

## §6 The gate — ✅ RULED August 15, 2026 (authoritative gate record)

> **Held the same day the spec was authored, under the user's delegated
> grant — verbatim: *"ESTABLISH RECCOMENDATION YOURSELF AND COMMIT AND PUSH
> SPEC UPDAYTES."* All five questions are taken at the recommended defaults;
> the considered alternatives are kept below for the record. One re-open
> condition is named on Q1 and carried into §8.**

**Q1 — The tier table. RULED (a): as tabled** — audience = {L0, L1, rivalry
@−1}; crisis = {L2, L3, rivalry @−2, Fontainebleau, war-weary}. Expected
≈7–9 modals/24 turns on the flagship shape.

The judgment call inside (a), decided and recorded: **L1 rides the audience
tier.** L1's register ("no longer a passing mood") is escalation *narration*,
but its arms, prices, and stakes are byte-identical to L0's — the decision
moments of this system are L2 (the damage goes permanent) and L3 (the feud
goes mutual), and those keep the stage. The arithmetic seconds it: L0-only
audience (option b) leaves ≈13 modals/24 turns, which fails the §8 bar this
gate exists to set. Option (c) was rejected because the @−2 breach was the
best drama in the measured run and loses its stage under it.
- *Alternatives on the record:* (b) stricter, only L0 audience → ≈+4 modals;
  (c) looser, everything but war-weary/Fontainebleau audience → ≈5 modals.
- **Named re-open condition (rides §8):** if the acceptance re-run (or the
  next played campaign) shows L1 audiences systematically dying unopened —
  superseded by their own L2 before the player ever views them — the tier
  line moves to (b) and L1 returns to the modal path. That is the one
  observable that would prove L1's moment needed the interrupt after all.

**Q2 — The audience surface. RULED (a):** notification rail + Generals-card
chip + top-bar badge opening the existing dialog via `GET /marshal_petition`.
Smallest diff; reuses the reward-chip discoverability pattern (the standing
"reactive but discoverable" feedback ruling); one card at a time.
- *Alternatives on the record:* (b) the letter-book shape (IGR-F machinery,
  per-row open) — rejected for now because the channel is one-card-at-a-time
  by design (§5.3) and a multi-row surface earns its weight only if F1 ever
  goes multi-card; re-open WITH that change or not at all. (c) keep the
  modal + hard spacing — rejected as the lossy budget §5.2 forbids wearing a
  scheduler's hat (deferral ages cards into stale-retirement).

**Q3 — Retirement receipts (F2). CONFIRMED as specified:** no numeric TTL;
subject-linked retirement + supersede-by-same-pair; every retirement emits a
one-line receipt. Silent retirement stays forbidden — it is the "silent
vassal loss" family IGR-A closed elsewhere, and the receipt is what makes
F2's retirement distinguishable from a bug.

**Q4 — The acceptance bar (§8). CONFIRMED as specified:** ≤9 blocking
petition modals per 24 flagship turns; no consecutive-modal streak longer
than 2; zero silent petition losses; audience throughput unbounded but
non-blocking. These are the numbers the build is judged against, on the same
driver arm and seed.

**Q5 — PopupQueue hygiene (F8). RULED:** both removals confirmed — the dead
`coalition_popup` slot and the unreachable `alliance_paradox_popup` order
entry go (the `LEGACY_ALIASES` map is retained for old saves); the three
`len == 11` / order pins flip consciously with the removal commit.
`proposal_result` gets the written **decision procedure** rather than a
guess: at slice B4, measure in the running client whether any surface
renders the key. If nothing reads it AND proposal outcomes demonstrably
reach the player through the terminal/dialogue prose, retire the key, its
queue slot, and the `_apply_command_popup_contract` bypass arm together; if
outcomes are otherwise invisible, wire the orphan scene instead. Either
way the bypass folds into the documented contract (F8's last paragraph) —
what is forbidden is leaving a nine-producer response key in a third,
undocumented state.

---

## §7 Tests, pins, and series discipline

**Pins that flip consciously (by name):**
- `test_cooldown_popup_manager.py:452` + `test_igr_f_envoy_digest.py:818`
  (`len(PRIORITY_ORDER) == 11` → 9 under F8) and
  `test_nation_agendas_formables.py:951-956` (order) — flip with Q5.
- `test_jealousy_v32.py:760` (option-id set incl. `command`) — unchanged by
  F1 (same card); `:800-805` (load round-trip "still pending") — stays green,
  gains the F5-4 delivery pin; `:823` (separation warning present) —
  unchanged (F5c collapses the *retirement* burst, not the proximity line).
- The A3-family pins in `test_jealousy_v32.py` / row-3 tests — F2 extends
  the guard to the re-push seam; existing answer-time pins stay.
- `main.py:1448` comment correction rides F5-4 (no pin; note only).

**New falsifiable tests, per fix:** F1 tier routing (a crisis card queues +
modals; an audience card never enters the PopupQueue, emits the notification,
serves over `GET /marshal_petition`, answers over the same POST; eviction
un-stamps; supersede retires; tutorial dormant both tiers) · F2 one
retirement test per kind + the receipt line + the S7 stale-rung pin · F3 the
two narration fallbacks · F4 the enum + a fifth-producer simulation (push
without guard → central guard catches) · F5 the four latent-bug pins (S1
never-collapsed; S4 stored-vs-derived normalization; S6 bulk-mend collapse;
S9 re-prime) · F6 the W7 trace as a regression test (hybrid preempted →
survives → answered with `dialogue_id` → stale binding fires instead of
cross-destruction) · F7 the three endpoint fixes + the route-census pin ·
F9 the `.gd` source-grep tail census · F10 per-slot load-validity tests.

**`BASELINE_SERIES`:** expected byte-identical for F1–F5 and F10 **by
construction** (every petition producer is player-nation-gated; fires,
thresholds, `jealous_of`, and trust writes are untouched; only delivery
routing, player-side seen-lists in the eviction case, and dispatch prose
move) — but the house discipline stands: *verify, do not assume*, one flip
experiment per landed slice, and any divergence bisected to its cause before
re-record. F6/F7/F9 are transport/client and cannot reach the series. M1–M7:
no combat math anywhere in this spec; byte-identical expected — record it as
a fact about the harness, not proof.

**`.gd` protocol:** F1 (chip/badge/dialog open), F6(b), F9 touch the client →
XR-1 boot smoke (0 SCRIPT ERROR), regenerate the tracked
`tools/godot_parse_report.json`, and heed the Aug-9 caveat that the
stale-report guard's critical-scripts set does not cover
`marshal_petition_dialog.gd` / `marshal_management.gd` — extend the set in
the same slice.

**Docs:** SAVE_FORMAT_REFERENCE (the `tier` key inside the petition dict;
no new fields) · SYSTEMS_REFERENCE §26 (the tier split) · PLAYTESTING.md +
`tools/playtest_driver.py` (an `audience` answer-policy row so Mode-A runs
exercise the chip; today's `petition: first_enabled` policy keeps answering
crisis modals) · JEALOUSY_SPEC §6 gains a pointer to this spec's F1 (the
"popup" language becomes tier-qualified) · resolve by reading the
`CAMPAIGN_LOG_TYPES` count discrepancy (CLAUDE.md says 156, the pins
reportedly assert 157) before adding any log type — none of §4 needs one.

---

## §8 Acceptance — how "fixed" is measured

Re-run the exact flagship arm (Mode A, same seed/script/policy;
`tools/playtest_runs/flagship-1805/meta.json` holds the config) after the
build:

1. **Blocking petition modals ≤ 9 in 24 turns** (was 19), with zero on
   consecutive-turn streaks longer than 2 (was an 11-turn streak).
2. **Zero silent petition losses**: every produced-or-blocked petition moment
   appears in the digest as a modal, a chip-served card, a narration
   fallback (F3), or a retirement receipt (F2) — assert by joining the
   event log against the producer log.
3. **Audience liveness**: ≥1 audience chip served and answered by the
   driver's new policy row; the answered audience applies identically to a
   modal answer (same handler, same state writes).
4. **The Q1 re-open observable** (§6): count L1 audiences that died unopened
   — superseded by their own pair's L2 before any view. If that is the
   systematic fate of L1 cards (not an occasional edge), the tier line moves
   to Q1(b) and L1 returns to the modal path; record the count either way.
5. The §1.1 per-kind table re-derived and recorded beside the old one in the
   next playtest memo — the before/after is the row's exit evidence, and the
   `apply_mood_variance` caveat from the gate answers (10% concern
   promotion) is pinned by the driver's fixed seed.

---

## §9 Build order

| Slice | Contents | Gate? | Touches |
|---|---|---|---|
| ~~**B0**~~ ✅ **LANDED Aug 15, 2026** | F5 latents (S1, S4, S6, S9) + F4 central guard + F3 narration fallbacks + F7 drains (3 endpoints + census pin) — `tests/test_pc15_10_b0_petition_channel.py` (24). Landing notes: F4's status vocabulary is `queued`/`blocked`/`dormant` (the tier statuses arrive with B1/B2); the queue_* producers return the status and the war-weary caller reads the petition off `world.pending_marshal_petition`; the identity re-push exemption keeps the per-turn re-pusher and the S9 re-prime legal; F7-2 was landed as non-drain after verifying the capture/charge follow-ons ride the EXECUTOR result's own keys (the spec's "client stashes only the diorama" undersold `_route_response_ui`'s 12-family table — recorded, conclusion unchanged); F3's two lines are new dispatch-only event types (`rivalry_blocked_note`, `war_weary_blocked_note`) in BOTH `_DISPATCH_EVENT_TYPES` and the exempt tuple, no CAMPAIGN_LOG_TYPES change; three prior pins flipped consciously (the a13 exempt tuple, the a14 war-weary return contract, the v32 rivalry once-test made S4-stable) + one test helper cleared the slot it now cannot overwrite. `BASELINE_SERIES` + M1–M7 verified byte-identical (control arm + harness green — measured, not assumed). | clear | backend only |
| **B1** | **F1 The Antechamber** — backend tier/routing/notification + `GET /marshal_petition`; then the chip/badge/dialog-open client half | **clear — Q1(a)/Q2(a) RULED** | backend + `.gd` |
| **B2** | F2 retirement + supersede + receipts; F10 load-validity generalization | clear — Q3 confirmed | backend |
| **B3** | F6 W7 preempt + hybrid `dialogue_id` | clear | backend + `.gd` |
| **B4** | F9 stash-and-raise chokepoint + F8 order/justification (Q5 removals ruled; run the `proposal_result` decision procedure) | clear — Q5 ruled | `.gd` + backend |
| **B5** | §8 acceptance re-run (incl. the Q1 re-open count) + driver policy row + doc updates | — | tools/docs |

One commit per lettered slice minimum; B0's four latents may land as
individual commits (each has its own pin). Every slice: suite green, ruff
clean, flip-experiment note in the commit for anything that could touch the
series; `.gd` slices boot the engine (XR-1).
