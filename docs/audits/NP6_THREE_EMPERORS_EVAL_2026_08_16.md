# NP-6 "The Three Emperors" — the gate memo (August 16, 2026)

> **A recommendation, not a build.** Nothing in this memo is coded. NP-6 is
> strikeable at the user's word (`NAPOLEON_SPEC.md` §10, §13, §15.7).
>
> Method: a foreign sovereign — **Tsar Alexander, Russia, `personality:
> "sovereign"`, 9,000 Imperial Guard carved strength-neutrally out of
> Kutuzov's 38,000** — was authored into a **scratchpad copy** of
> `europe_1805.json` (never the repo) and the five halves of the kit were
> measured end to end: an 18-turn played arm in which the player's army met
> him in the field, a 20-turn ambient arm with **France under the AI**, and
> direct measurement at the three seams a played arm could not reach.
> Scripts under the session scratchpad; every number below is measured.

## §1 The recommendation in one paragraph

**Author Alexander and Francis — but not before deciding one thing, and the
thing is bigger than the row's framing suggests.** Four of the five kit halves
work on a foreign sovereign today, for free, exactly as §10 promised. The
fifth — the aura — works *mechanically* and is **wrong on its face at turn
one**: an authored Tsar's very first battle prints **"The Emperor commands in
person (his star dims)"** at **+8%**, before anything has happened to him,
because a non-player court's imperial grip is a flat 75 and the aura window
tops out at 85. Shipping that is shipping a lie in the first sentence the
mechanic ever says. **Sized: 1 session if the user takes ruling (a) below; 2
if (c).** The capture-worth half — the user's actual Q8 want — is already live
and costs nothing, so **NP-6's marginal value is the man on the map, not the
capture-worth**, and the row is smaller than its name.

## §2 The three findings the prompt carried, re-measured

### Finding 1 — "his aura can never decay" — **TRUE OF BATTLES, FALSE IN GENERAL, AND THE REAL DEFECT IS SHARPER**

`authority.get_imperial_grip` reads `world.authority_tracker` **only for the
player**; every other court gets the flat `GRIP_ENEMY_COURT_BASE = 75`
(`authority.py:346`, `:467-471`). So:

| what happens to a foreign sovereign | does his aura move? |
|---|---|
| beaten in the field, six times | **no** — measured, 0.818 before and after |
| his capital taken | **yes** — grip 75 → 35, aura 0.818 → **0.091** |
| half his homeland taken | **yes** — grip → 50, aura → **0.364** |
| his war score below −30 / −50 | **yes** — −8 / −15 grip |
| **he is captured** | **written, then thrown away** — see below |

So the accurate statement is: **a foreign sovereign's myth breaks on
territory and never on battle.** That is a defensible design — but it is not
what §15.4 built for France, and it is not what the user asked for.

**Two consequences the prompt did not name, both measured:**

**(1a) A foreign sovereign can never have a full aura.** The window is
`AURA_GRIP_BROKEN 30 .. AURA_GRIP_FULL 85`; the enemy baseline is 75 and
*every other grip term is negative*. So he boots at `(75−30)/55 = 0.818` and
can only fall. Measured in a played battle, five times over:

```
"defender": [{"label": "The Emperor commands in person (his star dims)",
              "value": 8, "type": "bonus"}]
```

**On turn one. Before anything has happened.** The caption `(his star dims)`
is `_pres_a >= 0.999` in `battle_report.py:157` — a French-calibrated test
that a foreign sovereign fails by construction.

**(1b) `world.nation_authority` already exists, is serialized, is ALREADY
WRITTEN for an enemy sovereign — and `get_imperial_grip` never reads it.**
`world_state.py:4458-4461` (`_apply_sovereign_capture_consequences`) docks a
captured *enemy* sovereign's court by `SOVEREIGN_CAPTURE_AUTHORITY_SHOCK`
(−40) into `nation_authority`, with a comment saying it is the GR5-symmetric
mirror of the player's tracker. Measured: setting
`nation_authority["Russia"]` to 100, 75, 60, 40, 20 or **0** leaves grip at
**75**, aura at **0.818**, fear at **0.795** — unchanged, every time. The
capture shock is recorded and discarded.

*(The emperor-led ±2/−5 battle authority is a separate gap: that site
(`combat_executor.py:2418-2446`) is inside a `player_nation` branch and
writes nothing at all for a foreign sovereign. So finding 1 is two gaps, not
one — a write-with-no-read, and a no-write.)*

**Why this is not a one-line fix.** `nation_authority` boots at **60** for
every court, not 75. Making `get_imperial_grip` read it would move every
non-player court from grip 75 to grip 60 — which changes the VS-R vassal
coupling, `get_authority_lever_multiplier`, and the fear curve for **every
nation on the board**, and would move `BASELINE_SERIES`. That is the honest
reason NP-6 is bigger than "author two JSON entries", and it is the reason
this needs a ruling rather than a patch.

### Finding 2 — `_WIRED_ABILITY_MARSHALS` is name-keyed — **CONFIRMED**

`marshal_overview.py:31`. Measured contents: `{Moore, Davout, Uxbridge,
Soult, Drouot, ArchdukeCharles, Kutuzov, Napoleon, Bernadotte, Ney, Massena,
Wellington, Murat, Lannes, Blucher}` — **`Alexander` absent**, so an authored
Tsar renders no ability block until he is added. One-line content fix; it
belongs in the row.

### Finding 3 — the capture-worth is already live and free — **CONFIRMED, and now measured on a real board**

`CAPTIVE_EAGLE_SCORE = 15` / `SOVEREIGN_RANSOM = 5000`, both keyed on
`is_sovereign` in both directions (`diplomacy.py:3056`, `:3059`, `:3150-3157`,
`:7245`). Measured on a staged save with Napoleon taken: the war-detail score
breakdown carries **`"captive": -15`**, and `0` on the two saves where nobody
is held. The `_capture_marshal` seam is likewise sovereign-aware for either
nation and says so out loud.

**Say this plainly in the row: NP-6 buys the man on the map, not the
capture-worth.** The capture-worth already ships.

## §3 The five kit halves — measured end to end

| # | Half | Verdict | Measurement |
|---|---|---|---|
| 1 | **the aura on the Austrian/Russian side** | **WORKS — and mis-captions** | Five defensive battles in the played arm, each carrying `The Emperor commands in person (his star dims)` at **value 8**. The stamp, the modifier and the report row all key on `is_sovereign` and all fire for Russia |
| 2 | **the fear — a FRENCH corps must respect him** | **WORKS at the seam; occurrence 0 in 20 ambient turns** | `EnemyAI._evaluate_target_ratio` (`enemy_ai.py:2277`), base 1.00 → **0.7955** with the Tsar in the target stack vs 1.0000 without; exactly `sovereign_fear_factor("Russia")`. For scale, Napoleon gives 0.7500. Ambient arm B (Austria playing, France under AI, 20 turns) logged **zero** `EMPEROR_PRESENT` lines — the same reachability-without-occurrence shape as AI-3r §8.2 |
| 3 | **the Shadow over Kutuzov** | **WORKS** | `record_battle_glory`: Kutuzov banks **3** laurels for the same victory with the Tsar absent and **1** with him present. The mirror for France: Ney **4 → 2**. The sovereign himself banks **0** either way (the §2 never-do pin) |
| 4 | **the capture worth** | **WORKS, free** | see finding 3 |
| 5 | **the Seat for that nation's DP** | **WORKS, free** | `sovereign_seat_bonus(world, nation)` is nation-generic and is applied in `_process_dp_regen` **above** the player-specific branch (`diplomacy.py:9607`), so Russia's AI collects +1 DP while Alexander sits at Vilna |

Also verified in passing: **§7's Peril machinery runs for a foreign
sovereign** — the played arm produced *"[!] The Guard bought the road with its
own ranks — 804 men fall covering the withdrawal"* for the **Tsar's** guard,
twice, unprompted. And the authored entry's serialized key set is
**identical** to Napoleon's (zero new fields, as §10 promised).

## §4 New defects the measurement found — NP-6 must own these

| # | What | Severity for NP-6 |
|---|---|---|
| **N6-1** | The battle-report label is the hardcoded string **"The Emperor commands in person"** — France's own title printed for the Tsar of Russia. A player fighting Alexander reads a row about "The Emperor" and cannot tell whose. Needs a per-court title (authored `sovereign_title`, defaulting to "The Emperor") at the two producers | **blocker** |
| **N6-2** | **"(his star dims)" on turn one**, at +8%, before anything has happened (finding 1a) | **blocker** |
| **N6-3** | The ability block does not render (finding 2) | trivial |
| **N6-4** | The emperor-led ±2/−5 prestige beat, the "and the field was lost" sentence and the "Europe has begun to notice that he can be beaten" tail are all inside the `player_nation` branch — a foreign sovereign's own defeats are narrated to nobody | design call: does the player deserve to *hear* the Tsar's prestige fall? |

## §5 The ruling this memo asks for

**Q. What should a foreign sovereign's aura be derived from?**

- **(a) — RECOMMENDED. Leave the grip alone; fix the two blockers.** Declare
  in writing that a foreign court's myth breaks on **territory**, not on
  battle, and make the copy honest about it: give the aura a per-court title
  (N6-1) and make the `(his star dims)` caption relative to that court's own
  ceiling rather than to 1.0, so a Tsar at his boot grip reads **"+8%"** with
  no dimming clause and only dims when his grip actually falls (N6-2).
  *Cost: ~1 session with the authoring. No `BASELINE_SERIES` movement — the
  boot aura is unchanged, only the caption and the label.*
  *Honest cost: an authored Tsar's presence is permanently 8% not 10%, and
  the fear 0.795 not 0.75. That is a small, defensible asymmetry — Napoleon's
  myth was the bigger one — but it is an asymmetry, and it is a decision.*

- **(b) Raise the sovereign courts' baseline to `AURA_GRIP_FULL` (85).** Boot
  aura becomes exactly 1.0 and N6-2 dissolves; battles still never move it.
  Cheap, but it means `GRIP_ENEMY_COURT_BASE` stops being one number for
  every court, and grip is read by VS-R and by every AI fear check.
  *Cost: ~1 session. Moves the fear on every court that has a sovereign.*

- **(c) Wire `nation_authority` into `get_imperial_grip` for non-player
  courts, and write the emperor-led ±2/−5 there.** The honest fix, and the
  one that makes the user's brief symmetric: beat the Tsar six times and his
  aura *does* fall. But `nation_authority` boots at **60**, so every
  non-player court's grip moves 75 → 60 unless a sovereign-scoped floor is
  added, and the change touches VS-R, the lever multiplier and every fear
  check. **`BASELINE_SERIES` will move and must be flip-attributed.**
  *Cost: ~2 sessions, and a re-record.*

**My recommendation is (a)**, with (c) named as the re-open condition if the
user later wants foreign sovereigns to have felt arcs rather than felt
presence. (b) is the trap: it looks cheapest and it silently generalises a
constant that three subsystems read.

## §6 Sizing, if the user says build

| Item | Cost |
|---|---|
| Author **Alexander** (Russia, Imperial Guard ~9,000, carved strength-neutrally from Kutuzov) + **Francis** (Austria, nominal command) | small — the schema accepts them today and boots clean |
| `_WIRED_ABILITY_MARSHALS` rows (N6-3) | trivial |
| Per-court sovereign title at the two aura producers (N6-1) | small |
| Caption relative to the court's own ceiling (N6-2) | small |
| Portrait + map-piece assets, **git-added** (the §15.5 lesson: `assets/` is gitignored) | small, easy to forget |
| Russia/Austria roster + relationship-web re-blesses (MC-2 set-equality, MC-3 edge counts) | small, mechanical |
| A measured ambient pass; `BASELINE_SERIES` **will move** — the carve changes Kutuzov's battles exactly as Soult's carve did (§15.2 arm 0) | one re-record, flip-attributed |
| Frederick William III | **do not ship.** §10 lists him as authorable content, not shipped; nothing here changes that |

**Total: 1 session under ruling (a), 2 under (c).**

## §7 One thing worth saying out loud

The played campaign that accompanies this memo
(`PLAYTEST_NAPOLEON_CAMPAIGN_2026_08_16.md`) found that **capture never
happened in 68 turns on either side**, and that the player's Emperor rarely
gets to fight at all. Both of those apply to a Tsar as much as to Napoleon.
So the honest expectation for NP-6 is: **the fear and the aura will be felt;
the Shadow will be felt by Russia's own petition traffic; the capture-worth,
which is the half the user asked for, will almost never fire.** That is not
an argument against building it — the Tsar standing on the map beside Kutuzov
is worth the session on its own — but it should be built for the presence,
not for the prize.
