# Playtest + creative review — the CA9 fix queue, played

> **A 19-turn France/1805 campaign, driven live over HTTP against a fresh backend
> on port 8006 with `LLM_MODE=anthropic`, master at `26bbcbe`.** The user's brief:
> *"perform the playtest on all recent fixes and also review the game inc creative
> audit style as you do — play the game itself not tutorial of course."*
>
> Evidence: 100+ request/response pairs, exported readable at
> `scratchpad/campaign_readable.txt`. Nothing in the repo was modified while
> playing; every claim below was checked against production code before filing.

**⚠ Method caveat, and it matters.** An HTTP transcript is not what the player
sees. `enemy_phase_dialog.gd` rebuilds each line from `action.ai_action.action`;
`proposal_result_popup.gd` is an **orphan scene, never registered or routed**
(`dialog_manager.gd:30`). Every "the player sees X" claim below was confirmed
against the consuming `.gd` or is explicitly marked as latent. Three of my own
first-pass findings were **refuted by reading the code** and are listed in §5
rather than deleted.

---

## 0. Verdict

The **systems are markedly better than the reporting of them**, and — for the
first time — a set of yesterday's fixes made the reporting worse in the direction
that matters. Machinery earned its keep: an entire Britain–Spain war was fought,
embittered and concluded without France; Bernadotte's trust ran 40 → 0 across
fifteen turns of unrewarded victories and ended in a refusal that named its own
cause; the muster preview taught me the exact five words that would fetch Soult
and then honoured them. But CA9's through-line has not closed, it has **migrated**:
**three of the five P1s are regressions introduced by the August 9 fixes.** The
honest-availability build for the grievance channel is overwritten at the delivery
seam; the cautious-marshal confirm gate the user commissioned **never armed once**
because it reads an optimistic odds band; and CA9-N5's rewrite of the dialogue
failure string killed the fall-through that let a typed order escape a hard stop.
Two more P1s are older and simply needed a long enough campaign to hit. Directional
pillar movement is **≈6.4 from ≈6.9**, and every point of that drop is trust in
what the game *says*, not in what it does.

---

## 1. The campaign in one paragraph

France opened with the historical Ulm move — Ney into Swabia — and won. Then
Massena, trusted against Berthier's advice, attacked Archduke John in the Tyrol
mountains, lost 7,583 men, was counter-attacked at Milan, broken, and Italy fell.
Austria's Charles walked up the Rhône and took Provence and Languedoc; Mack took
Rhineland. France ground them all back, destroyed Mack's army at Nassau, and then
declared an opportunistic war on Hesse to test the "one battle for free cash"
cheese — and could not cash it in, because the war was too young and then, when it
was old enough, France was losing it on points. It ended in a white peace at
turn 14. By turn 19 the Grande Armée is **93,696 men from a starting 189,000**,
mostly eaten by supply attrition, the treasury holds **26,999 gold** and still
grows **+626 a turn**, and **five of seven marshals hold a live grievance or a
feud**. Bernadotte — crowned with glory at turn 8, never rewarded — is at **trust
0** and refused a direct order with the reason stated: *"(His loyalty is frayed by
neglect — his victories remain unrewarded.)"*

That last sentence is the game working. Three systems — glory, the ES-7 reward
economy, and the objection system — produced one legible consequence without any
of them mentioning each other. **The systems are good. The reporting layer is
still where the defects live**, which is exactly what the CA9 audit said in August
and is still the through-line: *the game computes the right answer and then tells
the player a different one.*

---

## 2. What the recent fixes actually did

### CA9 row 1 — "a short war should be hard to end" — **PASS, end to end**

The only one of the three rows I can call unambiguously successful. Measured
directly on `calculate_acceptance`, on the real board:

| war | age | `war_age_penalty` | peace-with-demand score |
|---|---|---|---|
| France–Hesse (declared turn 5) | 0 | **−30** | `gold_per_turn` **0**, `gold_lump` −62 |
| France–Austria (boot war) | 4 | **−15** | `gold_per_turn` 7 |
| France–Hesse at turn 13 | 8 | **0** | `gold_per_turn` **59** |

White peace is exempt at any age — correct, and it is what keeps this from making
a bad war unexitable. And the player-facing sentence lands:

> *"Hesse has rejected our Peace Treaty."*
> *"Talleyrand reports the key obstacle was **the war is barely begun — no court
> signs away a province over one skirmish**."*

The cheese loop is closed twice over. Beyond the age penalty, my Hesse war ran to
**war score −8 and falling** (`battle −3`, `ticking −5`) because Hesse held
Frankfurt and my own war objective ticked against me — so the "declare, win one
skirmish, collect" plan had no exit worth taking even when the age penalty
expired. Talleyrand's recommendation at turn 13 was a **white peace with no
demands**, which is the honest recommendation for a losing side, and F14's sign
coherence held.

*One copy nit:* the blocker phrase says "signs away **a province**" when the
demand was `gold_per_turn 300`.

### CA9 row 2 — the attack confirm gate — **FAIL: structurally unreachable as built**

The gate is built exactly as ruled (`objection_v2.muster_gate_arms`: `unfavorable`
**and** `cautious`; `even` blocks nobody) and both terms are load-bearing. **It
never armed once.** Three muster previews across the campaign: `favorable`, `even`,
`favorable`. The reason is not the gate — it is the number it reads. See **PT-65**
below, which is the most important finding of this playtest.

The safety net that *did* catch me is the older V2a objection: at turn 16 Davout
raised *"The odds are not in our favor. Perhaps we should reconsider."* So the
player is not left wholly unwarned — but the warning is **inconsistent**: the same
marshal, attacking the same enemy, got **no warning at ratio 0.60** (turn 15) and
a firm objection at **0.52** (turn 16). The variable in between is the optimistic
committed-strength figure.

### CA9 row 3 — the grievance channel — **PASS on content, FAIL on its flagship arm**

Everything the row built is live and most of it is good. Verified in play:

- **§3 "Let it stand", priced in men** — *"Free, and it fixes nothing. For 2 more
  turns he brings NONE of his 22,000 men to any battle Davout leads, and the
  quarrel may harden further."* This is the single best piece of writing the
  channel produces.
- **Q1(b) the HOLD arm** — 1 AP, and it states both effects: *"His patience is
  bought — the grievance shortens by 2 turns, and for 6 turns the quarrel cannot
  harden further."*
- **Q2(a) the council-command arm** — built, and honestly built. It is then
  un-built at the delivery seam: **6 of 10 petitions in this campaign shipped it
  `enabled` with its reason erased**. See **PT-17**.
- **A2 the recurrence register** — *"resents Davout's laurels for the third
  time"*, *"again, 3 turns after the last"*, *"again, the very next turn"*.
- **A5 the muster preview** — *"WILL NOT — Murat: will not lift a finger for this
  marshal"*, at the moment of the attack decision. Excellent.
- **A7 `jealousy_note`** — reached every battle report I saw.
- **A13 the drama cap** — *"The staff report 1 further matter among the marshals."*
- **Escalation registers** — level 0 → 1 → 2 all render distinct bodies and
  speaker lines, and the rivalry/mutual-feud beats fire.

What did not land: the **rivalry_confrontation** sibling kept its old unpriced arms
while `jealousy_confrontation` was rewritten. This is the sharpest contrast in the
whole channel. `jealousy.py:2256-2300` gives Force Reconciliation
**authority-banded odds** — ≥80 authority: 50% success; ≥60: 30% success and a 20%
chance of **−3 authority**; <60: 10% success and a 60% chance of **−5 authority** —
and Accept the Breach carries a **20%** chance that a marshal turns openly
discontent at −3 trust with defiance unlocked. The card says, in full:
*"A public gamble on your authority"* and *"one may turn openly discontent."* Two
AP, no band shown, no probability, no failure state. Next to *"For 2 more turns he
brings NONE of his 22,000 men"* it reads like a different game.

Also: the **cap covers one producer while eight other drama lines ride around it**
(turn 16 carried nine), and the channel is **loud** — 5–9 briefing lines per turn
against roughly one answerable decision, which is the grievance memo's own §9
concern, measured live.

### The 31 tier-1/tier-2 rows that were exercised

| fix | verdict | evidence |
|---|---|---|
| The typed dialogue router (P1 — signed a treaty with the wrong court) | **PASS** | `reject the Ottoman proposal` with Prussia active → *"that answer would be delivered to Prussia… Nothing from Ottoman Empire is before you"* |
| N5 — a blocked state names the words that clear it | **PASS** | *"Massena awaits your answer… Reply 'trust', 'insist' or 'compromise'."* Free reads (`status`) are not blocked |
| F6 — the war-purpose hard stop renders | **PASS** | The stop rendered, named all four options, and blocked cleanly |
| F13 — a voided order says so | **PASS** | *"Ney marched to the guns at Franconia — his standing order to pursue Mack is void"* |
| N1 — a reinforcer banks ONE win | **PASS** | Davout and Lannes each took `battles_won 1`, `glory 1`; Ney (lead) took 3 |
| IGR-B — campaign-log collapse | **PASS** | *"26 approaches rebuffed, chiefly from Bavaria and Prussia"* |
| IGR-F — the letter book | **PASS** | Digest, per-row accept/decline, lapse notices, title adapts ("THE COURTS WRITE" → "A SMALL COURT WRITES") |
| IGR-E — the plunder prompt states its terms | **PASS** | Milan 1,200g, Nassau 200g — income×4 exactly, quoted on the prompt and paid |
| CA8-2 — the supply headline | **PASS, and it is the best copy in the game** | *"Ney, Lannes and Bernadotte stand 50,473 men at Franconia, which feeds 40,000. 10,473 too many. 2,581 men lost in 2 turns. No depot may be laid at Franconia — not controlled by France. Move a corps, or continue to pay."* |
| CA8-D6 — the briefing may lead with a victory | **PASS** | *"Piedmont has fallen to our arms. The tricolor flies over it this morning."* |
| PARSE-NEG | **PASS** | *"hold your position, do not attack anyone"* → HOLD; *"I don't want to insist"* refused rather than executing INSIST |
| CR-5 delegation | **PASS** | *"Murat needs no second word, Sire — Archduke Charles is his."* |
| ES-7 endow / rente / erosion | **PASS** | Endow, rente, erosion notices, and the erosion surfacing inside an order refusal |
| The treaty-breach path (the July P1 soft-lock) | **PASS** | Four sequential modals, no loop, `breach_preview` naming treaty type, turns honoured (1) and reliability −10 |
| Stage D beat 6 | **PASS, in the wild** | *"THE CONGRESS: Britain and Spain have made their peace without France."* Spain's blockade lifted as a consequence |

---

## 3. Defects

Severity is mine; `player-visible` means I traced it to a rendering `.gd` or the
terminal.

| id | sev | claim | site | visible |
|---|---|---|---|---|
| **PT-65** | **P1** | The muster preview's `WILL JOIN` is an eligibility ladder; the resolver runs an arrival roll. The odds band — and row 2's gate — read the optimistic figure | `combat_executor.py:692`, `:327` | yes |
| **PT-17** | **P1** | `refresh_petition_affordability` **clobbers** the builder's honest `enabled: False` + `unavailable_reason`, re-enabling an arm that cannot fire — and pressing it **destroys the petition** | `jealousy.py:1557-1579` (honest build) vs `:1621-1636` (the clobber), `:1954` (pop-before-dispatch) | yes |
| **PT-25/30** | **P2** | The enemy phase drops undefended captures of the player's **own** provinces | `main.py:1427-1444` | yes |
| **PT-47** | **P2** | The muster `withholds` `≤0.0` arm renders a **pair** property as the joiner's personal grievance, naming the wrong marshal; the post-battle reason arm is one-directional and then blames the roads | `combat_executor.py:927-936`, `:1316-1319` | yes |
| **PT-45** | **P2** | An unopposed march-capture never clears `idle_turns` — the counter carries its **entire pre-capture history** across the conquest, and feeds the jealousy engine | `combat_executor.py:4135-4202` | indirectly |
| **PT-35** | **P2** | One settlement dialogue answers "who am I making peace with" three ways | `settlement_staging.py:2020-2033` → `proposal_confirm_popup.gd:395,443` | yes |
| **PT-33** | **P2** | A coalition peace queues behind a minor's NAP — and **two priority tables rank the same pair in opposite order** | `dialogue_manager.py:119-136` vs `cooldown_manager.py:145-162` | yes |
| **PT-46** | **P3** | "even" and "unfavorable" describe the same engagement two lines apart | `combat.py:418-425` vs `objection_v2.py:820,932-953` | yes |
| **PT-13** | **P3** | The per-court fog line renders as up to nine near-identical sentences — **16 of 18 enemy phases carried it** | `main.py:976-981` → `enemy_phase_dialog.gd:96-100` | yes |
| **PT-4/64** | **P3** | *"he has not seen laurels"* is asserted about the **subject** without ever reading his own windowed glory. *(My filed headline — "names a comparator who is not winning" — is **refuted at turn 2** and **unproven at turn 14**: `find_jealousy_target` draws only from peers strictly above on the ladder, so the comparator necessarily banked glory in the window.)* | `jealousy.py:2667-2678` | yes |
| **PT-19** | **P2** | A hard stop **swallows an unrelated valid order**, and CA9-N5's own rewrite of the failure string killed the executor fall-through that let a typed order escape — dead for every typed string | `main.py:2147-2153`; `diplomatic_executor.py:3499` vs `:3396` | yes |
| **PT-69** | **P2** | The strategic-objection buttons render hardcoded −10/+12/+3 and phantom AP costs; the engine applies different numbers | `disobedience.py:2238-2284`; `objection_dialog.gd:222-247` | yes |
| **PT-70** | **P2** | An ARMISTICE is announced as *"a separate peace"*, permanently ejects the court from the coalition with a −15 betrayal penalty, and the collapse never re-adds it | `world_state.py:9666-9670`; `coalition.py:1818,1823` | yes |
| **PT-72** | **P2** | The end-turn financial line prints **Upkeep unsigned** among signed siblings; the row does not sum to its own Net | `meta_executor.py:294-320` | yes |
| **PT-D1** | **P2** | *"attacks cautiously at unfavorable odds **alone**"* prints **iff `committed_attacker > 0`** — i.e. iff he is *not* alone | `combat.py:424-425` | yes |
| **PT-73** | **P2** | *"any command would restrain him"* — an objected order, a refused order, and answering the objection **all** fail to stand him down | `jealousy.py:2702-2711`; `executor.py:1854-1866` | yes |
| **PT-74** | **P2** | The trust warning at <40 advises "more independence"; `grant_autonomy` is only reachable from the redemption event at trust ≤20 | `world_state.py:10642-10649` | yes |
| **PT-75** | **P2** | The enemy phase interpolates raw camelCase marshal keys **~84 times**, with the correctly spaced name three lines below in `enemy_voice` | `enemy_phase_dialog.gd:133,308,311,315,330,352` | yes |
| **PT-79** | **P3** | The executor **builds** `suggestion: "Try 'move to Rhineland'"` and it never leaves the backend — 1 of 108 responses contains the word at all. *(This is PT-32's real root cause.)* | producers `combat_executor.py:3909,4219…`; **no consumer** in `main.py` | yes |
| **PT-77** | **P3** | Counter-punch: the notification says "within 2 turns", the expiry says "immediately after defending"; measured **one** usable turn | `combat_executor.py:1692` vs `world_state.py:10453-10468` | yes |
| **PT-76** | **P3** | The terminal and Berthier's report print two different French casualty figures under the identical label `Casualties:` | `combat_executor.py:1547-1550`; `main.gd:2111` vs `:2211` | yes |
| **PT-12** | **P3** | The diorama observation for the player's own rout is *"A standard affair. Nothing unusual to report."* | `battle_report.py:540-894` | yes |
| **PT-49** | **P3** | A resolved grievance is narrated **twice** | `jealousy.py:2550-2564` + `:1030` | yes |
| **PT-19** | **P3** | The war-purpose stop refuses the phrase its own raising message offered | `dialogue_routing.py:55-57,135-14x` | yes |
| **PT-54** | **P3** | The live-LLM unparseable fallback emits **markdown** and stage directions into a BBCode terminal | `prompt_builder.py:877-933` | yes |
| **PT-50** | **P3** | A destroyed army reports more casualties than it had (`15,815/15,437`) | `battle_report.py:919-943` | yes |
| **PT-21** | **P3** | `construction_complete` carries no `nation`, so the fog filter passes it at PARTIAL — foreign building completion is revealed | `world_state.py:5707-5732` + `meta_executor.py:104` | yes |
| **PT-58** | **P3** | A nation-named order was silently retargeted to another nation's marshal (outcome survives; my mechanism was wrong) | `combat_executor.py:3603-3736` | yes |
| **PT-61** | **P3** | The levy headline nags for an action with no legal actor, 11 turns running (root cause mis-diagnosed as filed) | `dispatch.py:201-208` | yes |
| **PT-32** | **P3** | *"cannot reach"* is a dead end that a synonym clears | `combat_executor.py:3843-3910` | yes |
| **PT-28/42** | **P3** | Marshal ack lines collide because the bank key is `turn + len(target)` — **no marshal term at all** | `marshal_voice.py:49-50,442-450` | yes |
| **PT-53** | **P3** | The rivalry petition's arms are unpriced and its 2 AP arm is a blind bet — the code has authority-banded odds and an authority penalty; the card says *"A public gamble on your authority."* | `jealousy.py:1784-1793`, `:2256-2300` | yes |
| **PT-55** | **P3** | The mailbox row reads `Armistice Losing` while the popup for the same item reads `Armistice` | `dialogue_manager.py:392-393` | yes |
| **PT-34** | **P3** | *"the offered terms for **war_1**"* — the raw war id in Talleyrand's prose | `settlement_offers.py:2588` | yes |
| **PT-24** | **P3** | *"Bohemia and 1 more provinces"* — and it is the **modal** rendering of the promotion | `emergent_designs.py:306-307` | yes |
| **PT-1** | **P3** | The clause-guard refusal path bypasses N5's option-naming helper | `main.py:2249-2271` | backend only |
| **PT-39** | **P3** | `proposal_result.outcome` is `REJECT` for a **succeeded** action | `main.py:1161` | notice rail only |
| **PT-29/31** | **P3** | `ArchdukeCharles` in pursue prose and the campaign log — **already open in BUG_FIXES**, not new | `strategic_executor.py:1361` etc. | yes |

### The severe ones, in prose

**PT-65 — the preview promises men the resolver does not deliver, and that is why
row 2 never fires.** *(Verified by me against the code, not by the review fleet —
it was filed after the verifiers launched. Everything below is quoted from the
transcript or read from the named functions.)*

`_muster_reason` (`combat_executor.py:692`) is a deterministic eligibility ladder:
broken? fortified? literal without orders? hostile? Roland marches, Eyes-on-a-Crown
does not, aggressive marches, otherwise yes. It never consults the arrival roll.
`_committed_reinforcement_strength` (`:327`) then prices every `will_join` marshal
into `committed_attacker` as `0.6 × strength × effectiveness × attack_mod ×
rel_scale` — a **strength** haircut with **no arrival-probability term**. The
resolver separately rolls each reinforcer against a threshold (measured:
`{"score": 56, "threshold": 65, "reason": "low_score"}`).

Measured twice, same shape. Turn 15, verbatim:

> `MUSTER — Davout (18,874; **39,240 if all march**) vs ArchdukeCharles (31,241
> men) at Munich — the balance of force looks **favorable**.`
> `WILL JOIN — Murat: will march to the sound of the guns — but he and Davout are
> at odds; expect about half his weight`
>
> `[Combat] Davout attacks cautiously **at unfavorable odds alone**.`
>
> `~ Murat could not reach the battlefield in time.`
> `~ Massed effective strength: 18,874 (lead) + 12,806 committed (Lannes) = 31,680.`
>
> *"Brutal stalemate… Heavy casualties on both sides: Davout's army 2,275."*

`muster_gate_arms` keys on `odds_band == "unfavorable"`; the band is computed from
39,240; so the cautious marshal is not asked, in the one situation the user
commissioned the gate for. `_defender_muster`'s own docstring names this failure
direction — *"the resulting error always pointed at 'favorable', which is the
direction that makes the player commit"* — and CA9-F1 fixed it for the defender's
term. The **arrival** term reintroduces it on the attacker's side.

Three fix directions, pick one: weight each contribution by arrival probability;
or split the display into certain / likely / may-not-come and band on the certain
subset; or give row 2 a second band computed from certain arrivals only.

**PT-17 — the only P1 the fleet confirmed: an offered button that eats the decision.**

Turn 2, Murat's jealousy confrontation. The `command` arm ships
`cost_note: "2 AP"`, **`enabled: true`**, and a detail that says *"There is no
enemy within his reach to send him against."* Pressing it returns
`success: false` with that same sentence, charges **0 AP**, and the petition is
gone. `jealousy.handle_petition_response` sets
`world.pending_marshal_petition = None` **before** dispatching to
`_apply_confrontation_choice`, and `_apply_command_choice` re-derives
availability — deliberately, per its own comment, because the card may be stale —
with no restore path. So the player's one interaction with the channel that turn
is spent on a no-op, and Murat's grievance stands untouched (`jealous_of: Davout`,
2 turns remaining, verified on the card afterwards).

*Two corrections to my first filing.* (a) I wrote "and no further Murat petition".
That is **false** — the same pair petitioned again at escalation level 1 on turn 4
and level 3 on turn 10. The decision is lost for that cycle, not forever. (b) My
diagnosis was incomplete, and the sweep found the real root cause: **the builder
gets it right.** `_command_option` returns
`{… "unavailable_reason": reason, "enabled": False}` when `command_arm_availability`
refuses. Then `refresh_petition_affordability` (`:1621-1636`), applied to every
petition at delivery, does `option["enabled"] = ap >= cost` for anything carrying
an `ap_cost` and `option.pop("unavailable_reason", None)` when affordable —
**overwriting the gate and erasing its stated reason.** The July-25 IGR-1 fix (AP
baked at zero) over-corrected: it now re-enables arms disabled for reasons that
have nothing to do with AP.

**PT-25/PT-30 — you can lose Paris and not see it happen.**

`_filter_enemy_phase_by_visibility` (`main.py:1346`) shows an AI action only if a
player marshal is in the battle, **or** the AI marshal's post-move location is at
FULL visibility. A province the player owns is PARTIAL (only marshal locations are
FULL). So an enemy marching **unopposed** into French soil lands in a
PARTIAL region and the action is suppressed. Measured three times in three turns:
Provence and Languedoc (turn 2), Rhineland (turn 3). The campaign log records all
three; the enemy phase showed none of them. `fog_hidden_nations` does not help —
Austria had other visible actions, so it is not listed as hidden, and the player
gets no hint at all.

**Two corrections to my own filing, from the refuter, and they narrow it:** the
player *is* told, immediately — the dispatch is in the same HTTP response, raised
on the next screen, leading at the system's maximum weight (`home_captured`, 100):
*"Sire — Provence has fallen. Enemy colours fly over French homeland soil."* And
the captor **is** recoverable: the campaign log's `region_captured` passes at
PARTIAL and renders *"Provence captured by Austria"*. So this is **not** "the
player is never told" — it is a **lost theatre beat on the one screen whose entire
job is reporting what Europe did**.

It is held at P2 anyway, on the refuter's own two grounds: it is *structural*
(undefended ⇒ no French marshal present ⇒ PARTIAL ⇒ suppressed, so it is
near-guaranteed for exactly the losses that matter most — three provinces in three
of fifteen phases here), and the project has already written this standard into
this very function twice. The NV-9 carve-out at `:1376-1387` exists because *"the
player's own fleet could lose thirty sail in the enemy phase and hear nothing"*,
and CA8-15 at `:767-781` landed because a court *"was announced by name in the
enemy phase and then said nothing."* Same shape, unfixed. And showing it would leak
nothing: the same payload already flips Provence to Austria on the map and already
names Mack in `fogged_forces`.

*(I initially suspected battles were being dropped too. **Refuted** — three
`ArchdukeCharles attack -> Ney` actions were present in the turn-8 phase. Only the
no-battle capture case is affected.)*

---

## 3b. What the independent sweeps found that the playtest missed

Five sweeps (contradiction / unreachable affordance / silence / economy / voice)
read the same transcript and the same code without being told what I had found.
They returned **54 findings, of which ten are P1**. Six overlap mine — including
an independent rediscovery of PT-65 with the same arithmetic, which is the
strongest confirmation it could get. **These eight are new, and three of them are
more serious than anything I filed:**

**S-1 (P1) — an autonomous jealousy attack fights a full battle and the entire
result is thrown away.** `turn_manager.py:184,187` assigns
`process_autonomous_attacks(...)` to `jealousy_attack_results` and **nothing ever
reads it** (grep-verified). Turn 5→6: the only thing I was told was *"Murat,
hungry for glory, has attacked Archduke John on his own initiative."* No battle
event, no report, no casualties, no diorama, nothing in `enemy_phase`. Murat's
roster row went **21,384 → 17,997 men and morale 100 → 81** with no supply event
to explain it — 3,387 men lost in a battle the player was never shown.
Reproduced on all four autonomous attacks in the campaign. This is the marquee
payoff of the Jealousy system and it lands as a rumour.

**S-2 (P1) — the morning dispatch is structurally incapable of narrating anything
diplomatic that happens during the turn.** `advance_turn`'s first act is
`self.pending_dispatch_events = []` (`world_state.py:8057`), and it runs *after*
the enemy phase, the AI diplomatic phase, strategic orders and the jealousy pass
have filled that queue. Across **18 consecutive dispatches, not one carried a
`nation_eliminated` or war-declaration line** although three fired. Kingdom of
Italy — my own vassal — was destroyed on turn 2 and the turn-3 briefing carried
`['diplomatic_dp_regen', 'paymaster_subsidy', 'agenda_shift']`. The fog rule on
both lost event types is `"always"`, so this is ordering, not fog. *(This also
supersedes my PT-63, which the refuter killed for the wrong reason.)*

**S-3 (P1) — a redemption event is deleted by whatever popup outranks it.** Turn
12, one response carried both `redemption_event` (Bernadotte at trust 2 — Grant
Autonomy / Transfer to Staff / Dismiss) and Denmark's non-aggression pact.
`main.gd:1325-1339` matches the **first** route and returns; `incoming_proposal`
is index 5 and `redemption_event` is index 12. The redemption never appeared
again in the remaining 19 responses. An entire gameplay branch is silently
destroyed at the moment it is offered — and the client already carries three
purpose-built stashes (`_stash_proclamation`, `_stash_envoy_digest`,
`_stash_diorama`) for exactly this failure class.

*(In the synthesis these carry PT numbers: S-1 = the discarded jealousy battle,
S-2 = the wiped dispatch rail, S-3 = **PT-67**, S-4 = **PT-66**, S-5 = **PT-68**,
S-6 = the enemy-voice rotation key, S-7 = the Talleyrand register break.)*

**S-4 / PT-66 (P1) — the war HUD lists courts you have made peace with.** Turn 14, one
payload: the notification says *"France and Hesse have signed a Peace Treaty"*,
`France|Hesse` is gone from `active_diplo_keys` — and `opponent_display` still
reads **"Britain + Austria + Hesse + Russia"**, and stays that way for the last
five turns. From turn 10 the same panel showed the war row naming Austria *and*
an armistice card reading "Austria 5t". `war_status.py:500-521` never filters the
participant list by current state.

**S-5 (P1) — Insist quotes −15 trust and charges −18.** `objection_dialog.gd:141`
renders the quoted `insist_penalty`; `disobedience.py:1345` applies it; a second
branch adds −3 without setting the flag the client reads. Measured on Bernadotte
at trust 17: `trust_change: -18`, and he landed at **0** rather than 2 — which is
what fired the redemption event that S-3 then deleted.

**S-6 (P1) — the enemy-voice rotation key makes `bank[1]` the default.**
`rotation_key = world.battle_counts[location]` is post-increment, so the first
battle in a province is key 1 — and on a 126-province map most provinces see
exactly one battle. For a 2-line bank, index 1 *is* the line and index 0 is
decoration. Archduke Charles, the campaign's principal antagonist, said *"Even the
Grande Armée bleeds when pressed at the right hour"* in **four of his five
attacks**. Doubling the bank would not fix it.

**S-7 (P1) — Talleyrand breaks his own Voice Bible on a blocking modal.**
*"**Sire!** We have a Non-Aggression Pact with Hesse. Declaring war would
**shatter** that commitment…"* — `DIPLOMAT_VOICE_BIBLE.md:36` forbids exclamation
marks, `:38` forbids military vocabulary as metaphor. It is the one place the
composed advisor loses his composure, and it is the highest-stakes sentence he
speaks.

**S-8 (P2) — `attacks cautiously at unfavorable odds ALONE` prints if and only if
he is NOT alone.** The `" alone"` suffix is appended when `committed_attacker > 0`.

**The P2s worth naming from the same sweeps** (the full 54 are in the workflow
transcript at `subagents/workflows/wf_0394ac7b-9c7/`):

- **The jealousy attack silently deletes the marshal's standing order** — the
  exact case CA9-F13's own code comment says it fixed.
- **The strategic-objection dialog quotes trust deltas and AP prices that no code
  applies.** Same family as S-5, one dialogue over.
- **An ARMISTICE is announced as "a separate peace"**, permanently ejects the
  court from the coalition, and the engine then collapses it back to war.
- **"any command would restrain him"** — the autonomous-attack fore-warning names
  a remedy that does not work: an objected or refused order does not restrain him.
- **The trust warning names a remedy that has no player control at the trust level
  that triggers it.**
- **Berthier's closing note is one fixed sentence per headline class**, and the
  entire priority ladder beneath it was dead for the whole campaign.
- **The marshal roster's danger line has no bank at all** — one sentence per
  class, repeated in 14 of 18 dispatches.
- **Every marshal's FIRST petition is pinned to bank index 0**, and the petition
  *body* has no bank at all — which is why Murat's and Massena's petitions were
  word-for-word identical.
- **Berthier prints raw internal marshal names in his own mouth** —
  "ArchdukeCharles", "ArchdukeJohn" — in the battle observations.
- **Marquee marshals have bank-size-1 slots**: Ney, Davout and Murat have 3–4
  lines *total* across five situations.
- **"No word from 84 provinces beyond the frontiers of …"** names eight provinces
  that are themselves among the 84.
- **Counter-punch tells the player two different windows**, and neither matches
  the mechanic.

**And a genuine disagreement between two of my own agents, arbitrated rather than
buried:** the voice sweep filed the entrenched cooling line as a **P1 broken
sentence**; the refuter and then the synthesis both **refuted it**, and the
refutation is right on every leg. The ellipsis is ordinary VP-ellipsis off the free
relative *"What was settled…"*; the two test assertions on `"has not been"` are arm
discriminators, not typo defence; and the sweep's proposed fix — suppressing
`_cause` on the entrenched arm — would make *"the Emperor forced the
reconciliation"* **production-dead**, since `force_reconciliation` exists only in
the −2 transition branch. **Withdrawn in full.** What survives is line *volume*,
which belongs to the narration row, not a copy bug.

---

## 4. Creative observations that are not defects

1. **The economy, measured turn by turn — the clearest answer this campaign
   produced to the standing "economy shouldn't go crazy" question.**

   **The arithmetic is exact.** A dedicated sweep asserted
   `Income + Requisitions + Overseas − Occupation − Contributions − Charges −
   Dotations − Rentes − Admiralty − Blockade − Upkeep + Other == Net` on **all 18
   turns with zero drift**, and reconciled every banner-to-banner treasury delta
   against the mid-turn `[Materiel]` and plunder flows. EB-1, ES-2, ES-7, EC-U3,
   EC-W1, EC-W3, EB-2, EB-5 and the naval components coexist without a gold going
   missing or double-counted. Record that as a win.

   **EB-1 is converging, and the mechanism is visible.** `Charges of Empire` rose
   0 → 2,643g while Net fell from its peak **+2,191 (turn 3) to +626 (turn 18)** —
   a 71.4% decay. The *pre-charge* surplus went the other way, 1,873 → 3,269
   (+74.5%), and plateaued near 3,231g/turn from turn 12. The brake grew faster
   than the engine, which is what it was gated to do. Extrapolated fixed point
   ≈ **32,600g**, substantially converged around turn 30–35.

   **But it never bites inside a played campaign.** Net was positive on **18 of
   18** turns and the treasury rose on every one, 800 → 27,625g (**×34.5**). The
   war never posed a financial question at a moment a player would notice.

   **And there is a perverse rebate.** Upkeep fell 1,924 → 688g (−64.2%) as the
   army was ground from 166,333 to 89,972 men (−45.9%), and the over-limit /
   Grande Armée surcharge reached 0 by turn 8. Because upkeep bills on *actual*
   fielded strength, **losing 76,361 men was worth +1,236g/turn** — the second
   largest structural swing in the campaign, after the Charges themselves.
   Attrition was a bigger lever on my treasury than any economic decision I made.

   The sweep's conclusion is the one worth carrying: **the brake is keyed to the
   wrong variable for the fantasy.** Pricing on the chest means the Emperor pays
   least exactly when he is losing; pricing on nothing else means an army's
   destruction reads as a windfall. Both are consistent with converging arithmetic
   and both invert the intended feeling. If EB-1 is revisited, the lever is the
   rate's **condition terms** — which do respond to play; the rate dropped
   273 → 206 the turn the Austrian armistice was signed — not the fraction.

   *Two defects inside all this.* The end-turn line prints **Upkeep unsigned**
   among signed components, so the row does not add up to its own Net:
   `3812 − 45 − 1955 − 200 − 120 − 90 − 181 + 848 + 973 = 3,042`, not the stated
   `+1,346`. It is only true if Upkeep is read as −848, and that is every one of 18
   lines. And the briefing's `treasury_delta` disagrees with the banner's Net on
   **10 of 18 turns**, by up to 643g, **always in the optimistic direction** —
   every named component matches; only the total differs, because one surface
   measures the treasury while the other sums declared components and
   `[Materiel]` has no declared component.
2. **Supply is the dominant loss channel, and the interrupt system feeds it.**
   Cannon-fire interrupts pulled Ney and Lannes off their marches into Munich,
   stacking 54,659 men on a 30,000 province; by turn 19 four corps sat at Milan
   losing ~1,900 men a turn indefinitely. The warning copy is excellent. The
   systems that create the stack are not talking to it.
3. **The jealousy channel produces 5–9 briefing lines per turn against ~1 decision.**
   The A13 cap fires, and eight other producers ride around it.
4. **Four stacked modals to declare war on a minor** (war purpose → treaty breach →
   Talleyrand objection → ally entry). Each is individually justified; together
   they are a lot.
5. **Charles attacked Ney three times in one enemy phase** (turn 8), 8,942
   casualties, 17,330 → 7,709. Worth a balance look.
6. **Britain's expeditionary corps ended up at Munich**, 800km inland, ground down
   to 5,715 men between two marshals. The naval expedition puts an army ashore and
   the land AI then marches it at a strategic-region target with no sense that it
   is an isolated corps on another continent.
7. **Marshal voice repeats verbatim across marshals, within a turn.** Ney and
   Lannes, in consecutive commands: *"Good. An army rots standing still."* Davout
   and Bernadotte: *"As ordered. I keep my flanks as I go."* Murat's and Massena's
   petitions share an identical body **and** speaker line. XR-5 grew the
   `enemy_voice` banks; the marshal ACK and petition banks were not grown, and the
   game's marquee promise is that these men are different people.

---

## 4b. Pillar scores — the creative-audit half

Seven independent judges, one pillar each, each grepping the transcript for its own
moments and reading them as a player would. They were given the CA9 calibration
numbers, so **read the reasons rather than the arithmetic** — the anchoring is
real, the campaign was 19 turns against CA9's 26, and the scorer sets differ.

| pillar | score | vs calibration |
|---|---|---|
| Marshal drama | **7.0** | 7.5 ▼ |
| Narration & briefing | **6.5** | 6.0 ▲ |
| Command & parsing | **6.5** | 7.0 ▼ |
| AI aliveness | **6.5** | 7.0 ▼ |
| Combat legibility | **6.0** | 6.5 ▼ |
| Economy | **6.0** | 6.5 ▼ |
| Diplomacy & settlement | **6.0** | 6.5 ▼ |
| **directional** | **≈6.4** | ≈6.7 |

**Narration is the only pillar that rose** — the same thing CA9 found. CA8-2's
supply headline, CA8-D6's victory leads, the A2 recurrence register and IGR-B's
log collapse are all doing visible work. Everything else slipped half a point, and
in every case the judge named a specific measured defect rather than a vibe.

### The three highest-leverage changes, in the judges' own words

1. **Weight each `will_join` contribution by its arrival probability before the
   band is computed.** *(Combat legibility.)* One number fixes three things: the
   preview stops over-promising, "favorable"/"unfavorable" stop meaning opposite
   things on one screen, and the cautious-marshal gate starts arming in the fights
   it was built for.
2. **Render `diplomatic_events` in `main.gd:_display_morning_dispatch`** — a copy
   of the ~14-line block already sitting in `dispatch_view.gd`. *(AI aliveness.)*
   It moves every agenda shift, revanche, subsidy switch, intent change and
   third-party peace from a screen nobody opens to the one the player reads every
   turn. Pair it with **S-2**, or the rail it renders will still be empty.
3. **Give TURN EVENTS the treatment IGR-B already gave the campaign log** —
   collapse by family at the view seam ("supply cost you 2,027 men at Tyrol and
   Milan"; "three satellites drifted"), cap the block, let the headline breathe.
   *(Narration.)* The machinery exists and is proven one surface over; the
   nine-line fog collapse (**PT-13**) goes in the same commit.

**The structural design note, and it is the one to think about longest: give the
war a memory.** `calculate_war_score` is a live board read, so losing four
provinces and retaking them nets to zero. Measured
`settlement_tier_display: "White Peace"` on **every single sample across 18 turns**
— dials, holdout actions, harshness and the whole per-court authoring screen all
resolve to the peace Britain offered for free on turn 3. This is the deep version
of the row-1 conversation: one monotone leverage term that ratchets on captures
and decisive victories and decays slowly, instead of re-reading the board.

Two more worth carrying, both surprising:

- **Economy:** *"Surface marshal commissioning. France's bench holds six men at
  3,500–6,000g — the only sink whose price matches the chest, the only one that
  converts gold into the thing the campaign actually lacked. The word 'commission'
  appears **zero times in 98 responses**. Put it in the levy headline's place: an
  army at 4% strength sitting on 24,415g should be told it can buy a marshal, not
  nagged for 450g it cannot spend."*
- **Diplomacy:** *"Give the war a memory. One monotone leverage term that ratchets
  on captures and decisive victories and decays slowly, instead of re-reading the
  board each turn."* This is the deep version of the row-1 conversation — the
  war score currently cannot remember that a war happened.

---

## 5. Claims I filed and then refuted, or corrected

Kept on the record rather than deleted.

- **"The headline said Massena was broken at Milan but the battle was at Tyrol."**
  Refuted. He attacked Tyrol, returned, and Austria counter-attacked him at Milan
  in the enemy phase. The headline was right.
- **"Provence and Languedoc are not in the campaign log."** Refuted — they are,
  under turn 2. I had looked at turn 3.
- **"The enemy phase dropped three battles at Nassau."** Refuted — they were
  present; my compact viewer was not printing the enemy phase.
- **"`war_age_penalty` is 0 in the live game, so row 1 is inert."** Refuted by
  reading the code: `extracts_value=False` returns 0 and a white peace is exempt
  **by design**. Re-run with a demand, the penalty is exactly −30/−15/0.
- **"Marshal `trust` is `None` on every card."** Refuted — the keys are
  `trust_value` / `trust_label`.
- **"Milan should have been endowable to Ney."** Refuted — Milan is a capital, and
  the predicate excludes capitals by design.
- **"An unopposed retake of Provence should have offered a plunder prompt."**
  Refuted — IGR-E's own-soil guard is correct.
- **"`idle_turns` is never cleared on a move."** Corrected — `movement_executor.py:497`
  does clear it. The gap is specifically the **combat-executor unopposed-capture
  path** (`~:4140`), which calls `move_to` and never touches the counter.
- **"The garbled cooling sentence is a template collision."** **Fully refuted by
  the review fleet** (`jealousy.py:1119-1143`). I first called it broken, then
  called it deliberate-but-badly-written. The refuter took all three of my
  load-bearing claims apart: the ellipsis is grammatical (the antecedent is not
  "has cooled"), the sentence is the entrenched-level variant doing deliberate
  work, and the item is a re-file of an already-disposed P3. **Withdrawn.**

### Refuted by the review fleet, after I filed them

- **PT-56** (above) — withdrawn entirely.
- **PT-63** *"one peace, three dispatch lines"* — refuted: `main.gd` never reads
  `diplomatic_events` at all, so none of the three lines is on the briefing.
- **PT-59** *"the arc note repeats verbatim every turn"* — refuted: the commit
  that gave the **headline** its repeat guard decided in the same breath that the
  roster cell keeps its memory, and wrote the reason down at the seam
  (`dispatch.py:787-791`).
- **PT-26** *"`KingdomOfItaly` in the elimination notice"* — refuted: the client's
  render-time R7 chokepoint catches it. Three non-visible hygiene facts remain.
- **PT-62** *"an obstacle named on a proposal predicted to ACCEPT"* — refuted on
  all three player-visible claims; the payload routes to
  `_build_peace_preview_content`, not the code path I cited.
- **PT-29/PT-31** — real, but **already open in `BUG_FIXES.md`**; not a new finding.

### Downgraded on refutation

`PT-46` P2→P3 (my threshold citation was wrong: `combat.py:419` hardcodes the
literal, it does not read `DAVOUT_MODIFIERS`) · `PT-58` P2→P3 (outcome survives,
mechanism refuted — `parser.py:741-745` drops a nation demonym to `None` **by
design**, as the fix for the earlier "Austrians"→Asturias fuzz) · `PT-61` P2→P3
(root cause mis-diagnosed; `get_levy_status.open` is not a broken predicate) ·
`PT-1` P2→P3 (backend-only; not player-visible) · `PT-32`, `PT-21`, `PT-4/64`,
`PT-13`, `PT-39` all →P3. `PT-4/64` is **half refuted**: at turn 2 the named
comparator *was* crowned that very turn. It survives only on the turn-14 instance,
where Lannes had been idle eight turns.

### Strengthened on refutation

`PT-17` → **P1** · `PT-45` — the refuter says I undersold it: the counter does not
merely skip a reset, it **carries the entire pre-capture history across the
conquest** · `PT-33` — worse than filed: `PopupQueue.PRIORITY_ORDER` and
`DialogueManager.DIALOGUE_PRIORITY` rank the same two dialogue types in **opposite
order** · `PT-13` — 16 of 18 enemy phases carried the repeated fog line ·
`PT-24` — "1 more provinces" is the **modal** rendering, because
`EMERGENT_DESIGN_MIN_LOST = 2`.

---

## 6. Not covered — would need another session

- **The visual sign-off is still owed.** I drove over HTTP and read the consuming
  `.gd` for every visible claim, but nothing here was seen on screen. The three
  surfaces already owed (F7's per-court fog line — see **PT-13**; `Supply: Unknown`
  on the region panel and the map tooltip) remain owed. I verified the region-panel
  sentinel exists in code (`region_panel.gd:182-184`) and could not find a map
  tooltip that reads `supply_capacity` at all.
- **The battle diorama was never seen animating** — I read its payload (rich and
  correct, both registers) but not the tableau.
- **N4, the petition TTL**, is still unfixed and I hit it: a
  `rivalry_confrontation` built on turn 7 was still being served on turn 10.
- **Row 2's gate has still never been observed arming.** Fixing PT-65 is the
  precondition for testing it at all.
- **The economy's *late* game.** EB-1's fixed point is ~32,600g around turn 30–35;
  this campaign stopped at 19. Whether the brake ever produces a decision is a
  question only a 35-turn campaign can answer.
- **Marshal commissioning** — the bench was never touched, and the economy judge
  argues it is the missing sink. Untested.
- **UNDETERMINED, stated as such:** whether the `foreign_wars` HUD panel is
  reachable at all on this scenario. It was empty in **102 of 102** payloads
  carrying `active_wars`, and the Spain–Britain and Bavaria–Austria wars are
  sub-pairs of the single France-containing 1805 instance — but nobody read the
  producer's skip condition, so "structurally unreachable at boot" is a hypothesis.

---

## 7. Where the full material lives

- This memo — the played narrative, the verdicts, and every correction.
- **`PLAYTEST_CA9_2026_08_09_FLEET_REPORT.md`** — the review fleet's own report,
  verbatim (47 agents, ~10.4M tokens, 2189 tool calls). It carries the complete
  PT-66…PT-79 table with per-line citations and the five P1 mechanisms in full.
  This memo is authoritative where the two differ.
- Per-agent returns: `subagents/workflows/wf_0394ac7b-9c7/journal.jsonl`.
- The campaign itself: `scratchpad/transcript.jsonl` (108 pairs) and
  `scratchpad/campaign_readable.txt`.

---

## 8. Method, and how much of this to trust

Roughly 60 agents ran over this campaign in four phases: five cluster verifiers
reading production code, one adversarial refuter per surviving finding (default
to refuted), five independent sweeps told nothing about my findings, and seven
pillar judges. **The refuters killed five of my findings and downgraded eight**,
including two where my stated mechanism was simply wrong; those are listed in §5
rather than quietly dropped. Two agents reached opposite conclusions on the same
line and both were right about a different half — recorded in §3b rather than
resolved by picking one.

What this pass is **not**: it is not a visual sign-off. Everything was driven over
HTTP and every player-visible claim was traced to its consuming `.gd`, which is a
weaker guarantee than looking. The three surfaces already owed a sign-off are
still owed, and **PT-13** and **S-3** are both the kind of thing a single play
session in the client would have caught in a minute.

**Nothing in the repo was modified except this file.** No commits.
