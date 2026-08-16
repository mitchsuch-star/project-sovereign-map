# THE PLAYED CAMPAIGN — France/1805 with its Emperor (August 16, 2026)

> **The campaign owed since row PT.** The NP gate's Q9 ruling deferred it
> until after row NP so it would evaluate the game *with* its Emperor, and
> until after the promise audit so it would evaluate the audit's eighteen
> fixes — every one of which had unit pins and runtime probes and **none of
> which had ever been played**.
>
> Master at `086aa9b`. Suite 18,057 / 3 skipped, ruff clean.
> Harness: `tools/playtest_driver.py` (doc of record `docs/PLAYTESTING.md`).
> Four scripted arms, 68 played turns, one of them on the live Anthropic
> parser; plus eleven targeted probes for the bands play cannot reach.
>
> **Evidence lives in `tools/playtest_runs/<name>/digest.md`** (gitignored,
> on this machine): `np-campaign-emperor` (22t) · `np-campaign-alone` (20t) ·
> `np-campaign-seat` (12t) · `np-campaign-live` (14t, anthropic). Scripts are
> committed at `tools/playtest_scripts/np_campaign_*.json`.
>
> **Report-only on defects: they are ROUTED, not fixed** (`BUG_FIXES.md`
> §Napoleon Campaign NPC / `DESIGN_REFINEMENT.md` §Napoleon Campaign).

## 1. Verdict

**The Emperor works, and the game does not tell you so.**

Every mechanical half of row NP that play could reach fired correctly: the
aura is stamped and it decays, HOLD holds, the Seat pays and says why, the
Petition for Independent Command fired *unprompted in two of four arms*, the
Shadow halves a marshal's laurels, the Guard buys an escape with its own
ranks. The eighteen audit fixes hold under play. Not one of them regressed.

What play adds that no unit pin could is the **delivery** verdict, and it is
the project's own through-line again, one layer up from where PT and PC15
left it:

> Over 22 turns the Emperor's aura fell from **+10% to +4%** — France lost
> thirteen homeland provinces and **Paris itself** — and the only place a
> player could ever have seen that number is a modifier row inside a battle
> report they had to open. The dispatch narrated the fall of Paris in the
> *same sentence it used for Nivernais*. There is no beat for the Seat being
> taken, no beat for the myth cracking, and `authority` — the number the card
> shows — **never moved off 100**.

The amendment the user asked for ("his losses have weight") is **built and
correct**. It is weighted through *territory*, not through battles, and it is
**invisible**. That is the one thing this campaign changes about the row's
status, and it is a narration slice, not a mechanics one.

**A correction this memo owes its own first draft.** The second headline it
originally carried — *"`attack <marshal>` out of range is a null action; a
PURSUE closes at zero provinces per turn"* — is **FALSE, and was killed by
its own refuters.** The pursuit closes normally, at the pursuer's
`movement_range`: measured three times independently, Paris→Swabia goes
**4 → 3 → 2**, and the refuters' samples reached combat in 2 of 5 runs, once
with a capture. It is struck (`BUG_FIXES.md` ~~NPC-4~~) rather than deleted,
because it was this session's headline and the next reader deserves to see
it was tested and killed.

**The observation behind it was real, and its true cause is worse for this
memo than the wrong one was for the game.** The player fought 11 battles
across 68 turns and the live arm fought **zero in 14** — because a strategic
interrupt raised during *end-turn* processing is never promoted to the
top-level response key. The unattended driver cannot see it, so the marshal
freezes and then the turn loop does too. Measured on the ordinary input
`Napoleon, attack Mack`: the pursuit closes 4 → 3 → 3 through turn 4, a
`cannon_fire` interrupt is raised on turn 5, and Napoleon never moves again
while `current_turn` stops advancing at 7. Only **one** `strategic_interrupt`
popup appears across all four digests.

**So every battle-count figure in this playtest understates the game**, and
the "does he *feel* strong" answer below is bounded by that (§4). A human
player is unaffected — the Godot client derives the interrupt from
`strategic_reports` — which makes this **P1 for anything that evaluates the
game unattended and P3 for the player** (`BUG_FIXES.md` NPC-16).

One defect on that same order survives at P1 and is real: the PURSUE
acceptance line **names an unseen enemy's exact province from omniscient
data** and the same order is then cancelled two turns later for having no
intelligence on him (`strategic_executor.py:1400-1403` vs `_execute_pursue`)
— confirmed 2/2.

## 2. Pillar scores

Against the August 15 comprehensive playtest (directional ≈6.7).

⚠ **Read these with NPC-16 in mind.** The harness froze marshals holding
strategic orders from the turn an end-turn interrupt fired, so this campaign
saw fewer battles than the game would have shown a human. Combat legibility
and marshal drama are scored on what *did* render, which is sound; but no
pillar here is scored on battle *frequency*, and none should be.

| Pillar | Aug 9 | Aug 15 | **Aug 16** | Δ | Why |
|---|---|---|---|---|---|
| Command & parsing | 6.5 | 6.5 | **6.5** | = | The Hand works on 6 of 8 live forms and PC15-8's literal ASK is fixed; but PC15-2's family is alive (NPC-1) and a prisoner refusal answers with another province's geometry (NPC-7) |
| Marshal drama | 7.0 | 7.0 | **7.5** | ▲ | The Shadow + the Petition for Independent Command firing *organically*, twice, unprompted — a genuinely new axis. The petition firehose still caps it |
| Combat legibility | 6.0 | 6.5 | **7.0** | ▲ | The aura row with its own decay caption, WILL JOIN / WILL NOT with stated reasons, diorama `absence_reason`, "[The Emperor] He commanded in person, and Europe saw it. (Authority +2)" |
| Narration & briefing | 6.5 | 7.0 | **6.5** | ▼ | Paris fell and got Nivernais's sentence. No Seat-lost beat, no myth-cracking beat, and the aura's whole arc is unnarrated (NPC-14/NPC-15, design half NPC-D1) |
| Economy | 6.0 | 6.5 | **6.5** | = | Convergence re-confirmed: arm 1 ran +2,272/turn → −551/turn as the empire overreached; arm 2 plateaued at +42. War grinds the purse, correctly |
| Diplomacy & settlement | 6.0 | 6.0 | **6.0** | = | Little new evidence; the confirm chain recurred once (NPC-21, downgraded) |
| AI aliveness | 6.5 | 7.0 | **7.5** | ▲ | Europe took **thirteen** French homeland provinces including Paris while the player pushed east. Overextension punished beautifully and without cheating |
| Vassals | — | 6.5 | **6.5** | = | no new evidence |
| Naval | — | 6.5 | **6.5** | = | no new evidence |
| UI/UX | — | 7.0 | **7.0** | = | no visual pass taken (see §6) |
| **Directional** | ≈6.4 | ≈6.7 | **≈6.8** | ▲ | |

## 3. The run matrix

| Arm | Shape | Result |
|---|---|---|
| **1 — the Emperor takes the field** | 22 turns, mock, scripted | Completed. 65 commands, 39 popups, 4 player battles. He marched Paris→Lorraine in four turns, joined the concentration, reinforced Davout at Tyrol and led at Bohemia. Meanwhile **Europe took 13 French homeland provinces including Paris (T15)**. Aura 1.000 → 0.400. The turn-22 "sixteen `proposal_confirm` popups" that looked like a soft-lock is **mostly a harness artefact** — see NPC-21 + NPC-H1/H3 |
| **2 — the Emperor alone** | 20 turns, mock | Completed. The design intent (every marshal fortified out of the muster so the 10,000-man Guard fights alone) was **defeated by the game being good**: the marshals' objections overrode three fortify orders and won the war in three turns — Mack was *captured on turn 3*. The arm then became an unintended and very valuable test of what happens when you order an attack on your own prisoner: **fifteen consecutive turns of "cannot reach Mack … Distance: 7"** (NPC-7). The `shadow_command` petition fired here, turn 9, unprompted. |
| **3 — the Seat** | 12 turns, mock | Completed. "Napoleon, hold Paris" on turn 1 and he never moved for twelve turns; DP 6/6 throughout. ⚠ **the stillness is vacuous as evidence** — the run's own autosave shows no enemy was ever adjacent to Paris, so nothing ever tempted him. The B4 fix is confirmed by falsification probe instead (§5) |
| **4 — live parse** | 14 turns, `LLM_MODE=anthropic` | Completed. 42 commands, **0 player battles — caused by the harness freeze (NPC-16), not by the game.** Six of eight sovereign address forms bound correctly on sentences absent from the golden corpus; the two A4 negative controls both held. |

## 4. What only play could answer — the seven NP questions

| Question | Answer |
|---|---|
| **Does the Emperor feel strong?** | **Mechanically yes; experientially NOT ANSWERED, and this memo should not pretend otherwise.** When he fights, the screen is unambiguous: "The Emperor commands in person — every corps on this field fights +10% harder", the modifier row, the authority beat. He fought rarely — but the cause was the harness freeze (NPC-16), not the game, so the felt answer is **owed to a human-played session**. N1/N2 are correctly sized and must not be raised on this evidence. |
| **Do his losses have weight?** | **The mechanism yes, the delivery no.** Measured on the arm-1 t22 save: authority **100**, grip **52**, aura **0.400**, battle row **"+4% (his star dims)"**. The number moved. Nothing ever said so outside a modifier row (NPC-2). |
| **Does the Shadow reshape the court?** | Partly. It fires (measured: a marshal's 3 laurels become 1 under his eye; 4 → 2 for Ney), and it produced the Petition — which is the intended court pressure. But it never changed *my* play, because stacking never became the dominant thing to do: he is too slow to stack with. |
| **Does the Petition for Independent Command fire in ordinary play?** | **YES — unprompted, in two of four arms** (arm 2 turn 9, Soult; live arm turn 13, Soult). Not dead content. |
| **Does capture ever happen?** | **No, in 68 turns, on either side** — correctly rare per §7, but that means the Eagle in Chains is content nobody will see. The machinery is sound: forced through the production seam it says *"[!] THE EAGLE IN CHAINS — Napoleon is TAKEN by Austria at Orleanais! The Empire reels; 5,000 of the Guard escape home to the depots."* and the war-detail row carries **`captive: -15`**. |
| **Is the Seat worth staying home for?** | **It pays and it is legible** (DP 5→6, `seat_bonus: 1`, "+1 the Emperor holds court in the capital"), but +1 DP against ~30% more army in a battle is not a real decision — arm 3's twelve turns at Paris never once made me want him there. It is a correct v1 and a thin one. |
| **Ambient council wars / the D1 band** | Still 0. No AI-vs-AI war opened in any arm. AI-3r §8.2's finding is re-confirmed a third time; the band stays unmeasured. |

## 5. What was fixed by the audit and never played — all seven CHECKED

Each row states **how** it was checked. A find→refute fleet (9 verifiers, 2
independent refuters per surviving claim) was run over this section
specifically to attack the session's own "verified in play" wording, and it
corrected four of the eight rows. Those corrections are kept in place rather
than smoothed over, because the distinction between *played* and *probed*
is the whole value of a playtest memo.

| Check | Verdict | How, exactly |
|---|---|---|
| the aura visibly dims in battle reports as authority falls | **PASS — by probe, not by campaign** | Direct reproduction at `/command`: attacker side end to end, defender side at the producer. `{"label": "The Emperor commands in person (his star dims)", "value": 9}`. ⚠ **`value: 10` does not prove a full aura** — at grip 83–84 the row reads value 10 *with* the dimming label. **None of the four campaigns produced the dimming row**, which is itself the narration finding (NPC-2) |
| the "+0%" band is closed (audit B11) | **PASS** | The whole ladder: authority 100→85 renders +10, 80→+9, 70→+7, 60→+5, 50→+4, 40→+2, 33→+1, **31–32 suppressed entirely**. Three producers carry `if _pct > 0`, attacker *and* defender |
| a charge out of the Emperor's province grants no aura row and full glory | **NOT REACHED** | `Murat, charge Mack` refused honestly — "needs to build momentum first! … recklessness (currently 0)". The B2 fix stays pin-only |
| the muster note appears only when he will actually march, and hedges | **PASS with a wart** | Both directions verified. The silent half is healthy — a fortified Emperor prints "WILL NOT — Napoleon: is dug in and will not abandon his works" and **no** presence line, on one screen. The wart is the opposite direction: the hedge also fires when he is the *lead attacker*, who is definitionally marching (NPC-3) |
| **HOLD holds** | **PASS — by falsification probe** | ⚠ arm 3's twelve still turns are **vacuous evidence** (no enemy was ever adjacent to Paris). Properly falsified instead: a weaker at-war enemy parked in a Paris-adjacent province for three HOLD ticks — the sovereign held and lost no men; the identical board with the personality flipped to `aggressive` sallied and bled 95. The guard at `strategic.py:1669` is load-bearing |
| a captured sovereign is announced taken, not destroyed | **PASS (probe)** | The production capture seam says "[!] THE EAGLE IN CHAINS — Napoleon is TAKEN by Austria at Orleanais! The Empire reels; 5,000 of the Guard escape home to the depots." No destruction sentence on any route |
| the Petition's dispatch beat | **PASS** | Quoted from `last_morning_dispatch['turn_events']`: `{"message": "Soult seeks an audience, Sire — he asks for a command of his own.", "severity": "warning", "type": "shadow_petition"}`. ⚠ its appearance *in the two played arms* is not verifiable from the artifacts — the digest keeps one headline per turn and does not carry `turn_events` |
| the DP HUD reads 6/6 | **PASS, with one correction** | `dp_remaining: 6, dp_max: 6, breakdown {base 3, skill 1, authority 1, capital_penalty 0, **seat_bonus 1**}`, and the dispatch line "+1 the Emperor holds court in the capital". The payload key is **`max_diplomatic_points`** (not `diplomatic_points_max`, which exists nowhere), and on **turn 1 the HUD reads 5/6** — the Seat's +1 lands at the DP regen tick while the ceiling derives immediately |

## 6. The visual sign-off — STAGED, NOT SIGNED, and NOT captured

Three saves are staged for the user's own pass. **The client-driven screenshot
capture was deliberately abandoned**: the paired client came up correctly on
`SOVEREIGN_PORT=8006` and connected ("The war office answers · 127.0.0.1:8006"),
but the user's own game was live in the foreground, and driving synthetic
input past it is exactly the hazard the standing desktop-automation rule
exists to prevent. What was done instead: the **data behind all five owed
surfaces was verified over the wire**, so the user's pass is a look rather
than a hunt.

| Surface | Save | Payload verified |
|---|---|---|
| the emperor map piece | `saves/np_visual_field.json` (t12, Bohemia, 7,579 men) | `"arm": "emperor"` rides the marshal payload |
| the Generals apex card | any of the three | `"sovereign": true`, `"sovereign_note": "The Empire is his estate."`, `ability_name "The Presence"`, and on the captive save `"captured": true, "captured_by": "Austria", "status": "captured"` |
| the diorama locket "N" cipher | `np_visual_field` (replay a battle) | contingents carry `"sovereign": true`, `"arm": "emperor"` |
| the Captive Eagle war-detail row | `saves/np_visual_captive.json` | score breakdown `"captive": -15` (and 0 on both other saves) |
| the Tuileries ledger line | `saves/np_visual_seat.json` (turn 6, Paris) | `dp_breakdown.seat_bonus: 1`, `dp_max: 6` — the key `diplomatic_ledger.py:1158` says the `.gd` renders it off |

To run the pair without touching a live 8005 session:

```bash
SOVEREIGN_PORT=8006 .venv/Scripts/python.exe -m backend.main
```

The captive save is **forced** through the production capture seam and
labelled so: §7 needs a true encirclement, which 68 played turns did not
produce. It is a screenshot fixture, not play evidence.

## 7. Defects — 27 game rows + 3 harness rows, all ROUTED

Full table with seams: **`BUG_FIXES.md` §Napoleon Campaign (NPC)**; design
calls: **`DESIGN_REFINEMENT.md` §Napoleon Campaign** (NPC-D1..D4).

Method: nine verifiers, each required to point at `file:line` with a
reproduction before a row could be filed; then two independent refuters per
surviving claim. **The verifiers corrected four of the session's own
"verified in play" claims** (§5) and refuted three candidate defects outright;
**the refuters then killed two more rows, corrected one root cause and split
the severity on two** — all folded into the routing table rather than
appended. The two P1s marked ⛔ were additionally reproduced by hand,
independently of the fleet.

Two corrections worth carrying here because they change what a fixer would do:
NPC-2's cause is **not** "TUT-F4a implemented at 1 of ~38 seams" — the clear
IS written and is *unreachable for strategic orders* (`executor.py:873`
excludes `is_strategic_command`); and the session's claim that NPC-9 is "not
the retirement of `take`" was **refuted for its first input** — restoring
`take` to the verb set does bind that sentence, so the real fix is the
`$`-anchored self-marker regex, not the verb list.

**Four P1s** (a fifth was filed and killed — see below). ⛔ NPC-1 typing an
enemy's name *the way the game prints it* fights a different enemy and wins ·
⛔ NPC-2 the stale interrupt that makes NPC-1 possible survives a replacement
order (TUT-F4a's clear is unreachable for strategic orders) · NPC-3 `attack
Archduke John` silently attacks Archduke Charles · NPC-5 the PURSUE
acceptance leaks an unseen enemy's exact province and the same order is then
cancelled for having no intelligence on him · ⛔ NPC-16 the end-turn interrupt
freeze, **P1 for evidence and P3 for the player**.

**Two rows were filed and then killed by their own refuters, and both were
this session's claims rather than someone else's:** ~~NPC-4~~ the "null
pursuit" (the pursuit closes — measured three ways) and ~~NPC-22~~ the
sovereign's cannon-fire ask, which is a **recorded, dated, census-pinned NP-V
decision** with Berthier speaking, not a silent inheritance. NPC-22 had been
written up here as "the only NP-shaped mechanical defect the campaign found";
it is not a defect at all, and the campaign found **none**.

**Eleven P2s** — a dead marshal's name retargets a living one; an attack on
our own prisoner answers with Spain's geometry and has an executing arm;
`support Marshal Ney` supports Bernadotte; the compound self-address and the
returned phantom province; the A4 verb gate too loose one way and too tight
the other; the literal's "verbatim" quote fabricated from database keys; raw
camelCase keys on seven surfaces; a retreat offered that does not exist; a
fallen homeland province forgotten after one turn; Paris given Nivernais's
sentence with no captor named; an end-turn interrupt never promoted to the
response.

**Ten P3s** — the muster hedge and "this marshal"; the title-as-referent gap;
two more answers to "what about our prisoner?"; the cannon_fire `own_ground`
key mismatch; the dead `proposal_confirm` button; the retreat-that-does-not-
exist; the enemy-incursion grammar; the bare famine number; the charge
threshold never named; and the raw-authority-vs-derived-grip contradiction.

**And the finding that is not a defect at all: the campaign found ZERO
NP-shaped mechanical defects.** Every sovereign-specific row it produced is
copy (the hedge, "this marshal", the title as referent) — and the one that
looked mechanical, ~~NPC-22~~, turned out to be a recorded NP-V ruling. Row NP
came through a played campaign with its mechanics intact.

**The through-line, stated once.** Almost every P1 and P2 here is one defect
in five costumes: **the player names a thing the way the game printed it, and
the game acts on something else** — and only one of the five refuses out loud.
That is CA9's through-line moved one step earlier in the pipeline: it is no
longer that the delivery of a correct computation misleads, it is that the
*referent* is resolved wrong before any computation happens.

## 8. What this playtest discharges, and what it does not

**Discharges:**
- The played 20-turn campaign owed since row PT (Q9 ruling) — 68 turns, four arms.
- All seven "fixed but never played" checks (§5); six PASS, one not reached.
- The NP-V review's two open scores get their played answer (§4).
- The D7 variance contract is *not* re-tested here (one seed, four arms).

**Does not:**
- The user's own visual sign-off (§6) — staged, never signed.
- The naval, vassal and UI pillars — no new evidence; carried forward.
- The D1 ambient-war band — still 0, third confirmation.
- The Emperor at the head of a *winning* campaign: every arm ended with
  France losing ground at home. A campaign that consolidates instead of
  chasing would test the Seat and the Shadow far harder.
