<!-- Audit memo. Authoritative for the Nation Agendas phase review of July 18, 2026. -->

# Nation Agendas — whole-phase audit, NA-0 → NA-6b

**Audited:** master `57dbde7` (phase diff `909594b..57dbde7`)
**Held:** July 18, 2026
**Method:** 112-agent adversarial workflow — 3 recon readers → 4 empirical probes
+ 16 finder lenses → 3 refuter lenses per finding (2-of-3 majority to survive,
default-REFUTED) → completeness critic → synthesis.
**Raw findings 29 → 8 survived.** ~17.6M subagent tokens, 2,333 tool calls.
This is the fifth review of the phase; the four prior rounds' findings were
excluded up front and are not re-reported here.

## Disposition — ALL FIXED July 18, 2026

The user directed "fix all, make decision and inform me … sensitive to the golden
rule and history and fun." Every finding was landed; the semantics calls were made
rather than deferred. Fix record = `NATION_AGENDAS_SPEC.md` §19.

| Item | Disposition |
|---|---|
| P1 deny satisfaction anchored on bloc membership | ✅ FIXED — satisfaction is a statement about the PROVINCES |
| P2 diplomatic nation-picker dead name | ✅ LANDED `e44c5db` |
| P2 ultimatum yield after the peace lapses | ✅ FIXED — `_ultimatum_void_reason` gates both arms |
| P3 armistice both arms and disarms the Ansbach trap | ✅ FIXED — an armistice is belligerency; §5.9 predicate amended |
| P3 incoming-proposal notification dead name | ✅ LANDED `e44c5db` |
| P3 ENEMY_AI_REFERENCE P4 helper citation | ✅ LANDED `e44c5db` |
| Coherence: satisfied court cannot be priced ENTRENCH | ✅ FIXED — and wider than reported (see below) |
| Coherence: §11.9 sponsor machinery | Assessed GR9-compliant. No action, by design. |

**Two findings in this memo proved narrower than the truth.** The ENTRENCH item said
a satisfied court has no active view; in fact it often has a *different* one (Austria
holding Milan flies `primacy_germany`), so fixing only the `None` case would have left
the real case broken. And a court that wins its *whole* deck needed every satisfied
entry, not just the first.

**The P1 fix itself re-opened the P1 twice before it was right**, both caught by a
37-agent pre-push review: once by building the exclusion set from the RAW hegemon
gated on the share floor, and once by reading the LITERAL `region.controller`, which
let a French satellite pass as a neutral buffer. Recorded in §19 because the
generalizable lesson is worth more than the fix: **any predicate asking "who holds
this province" must resolve `_top_overlord`; any predicate asking "who is the threat"
must be court-relative.**

## Independent verification of the P1 (auditor, not subagent)

The headline P1 was re-derived from scratch before being reported, because the
whole verdict rests on it and one refuter had rejected it on reachability.

`coalition.form_coalition(["Austria","Britain","Prussia","Russia"], world)` run
against the real `europe_1805.json` world, with the authored boot alliances
first cleared:

```
formed: True
intra-coalition states: [('Austria','Britain','PEACE'), ('Austria','Prussia','PEACE'),
                         ('Austria','Russia','PEACE'), ('Britain','Prussia','PEACE'),
                         ('Britain','Russia','PEACE'), ('Prussia','Russia','PEACE')]
bloc Britain: ['Britain']
```

Zero ALLIANCE rows. `grep -n "set_diplomatic_state|diplomatic_states\["
backend/game_logic/coalition.py` returns exactly one hit, at line 375, inside a
docstring. **Spec §18 line 599's "Coalition formation produces real `ALLIANCE`
states" is factually false** — the boot Third Coalition is allied only because
`europe_1805.json` authors those rows. That claim is the sole justification for
scoping deny satisfaction to bloc membership.

The consequence, reproduced on the real world (Britain unallied + Austria's bloc
out-massing France + Britain's three targets untouched in French-camp hands):

```
Britain's targets   : [('Flanders','France'), ('Brabant','Holland'), ('Amsterdam','Holland')]
bloc Britain        : ['Britain']
hegemon(Britain)    : ('Austria', 0.5084745762711864)
SATISFIED?          : True        <-- France holds all three
active agenda       : None        <-- invisible to the player
resolve vs France   : 10          <-- sues sooner, for winning nothing
separate peace ready: True
covets              : []          <-- unpriceable by acceptance/settlement scorers
```

One probe note for whoever takes this: `power_score` reads
`world.get_nation_regions`, which is cached behind `invalidate_active_nations_cache()`
— *not* `invalidate_bloc_members_cache()`. A probe that mutates `region.controller`
and flushes only the bloc cache will see a stale, unchanged bloc share and wrongly
conclude the geometry is unreachable.

---

# Nation Agendas — phase audit, master 57dbde7

## 1. Verdict

The phase is broadly sound: the substrate is well-architected, all six §0 G2 coupling pillars have live production call sites, and four prior review rounds have swept the delivery, naming, and dead-machinery surfaces thoroughly. **One P1 survives and was reproduced end-to-end**: the §18 court-relative hegemon fix is anchored on formal ALLIANCE membership, but `form_coalition` writes no diplomatic states, so any coalition formed in-game leaves a `deny_regions` court reading its design SATISFIED while the denied power holds every listed province — +10 peace resolve and early separate peace for winning nothing. Everything else is P2 or below.

## 2. Confirmed defects

### P1 — defect — `backend/game_logic/agendas.py:316` — deny satisfaction is anchored on bloc membership, and a coalition is not a bloc

The satisfaction guard added by §18 only fires when the denier sits *inside* the raw dominant bloc:

```python
raw_hegemon, _raw_share = _hegemon(world)
if raw_hegemon is not None and (
        nation == raw_hegemon
        or nation in set(world.get_bloc_members(raw_hegemon))):
    return False
hegemon, _share = _hegemon(world, nation)      # :321
```

`get_bloc_members` (`world_state.py:1736-1746`) admits only the leader, its vassal chain, and nations at `ALLIANCE`/`DEFENSIVE_ALLIANCE`. The spec's justification for why that suffices is **factually wrong**: `NATION_AGENDAS_SPEC.md:599` asserts *"Coalition formation produces real ALLIANCE states"* — `coalition.form_coalition` writes `world.active_coalition`, calls `declare_war`, and applies a +10 relation nudge (`coalition.py:1379-1381`); `grep -n "set_diplomatic_state\|diplomatic_states\[" backend/game_logic/coalition.py` returns **zero state writes**. The boot Third Coalition is allied only because `europe_1805.json` authors those rows.

Reproduced on the real 126-province world (completeness-critic probe, and independently by two refuters):

```
formed: ['Austria','Britain','Prussia','Russia','Sweden']
ALLIANCE rows after form_coalition: []
bloc Britain: ['Britain']
Flanders/Brabant/Amsterdam controllers: ['France','Holland','Holland']
Britain hegemon (court-relative): ('Austria', 0.483)
low_countries SATISFIED?         True
active agenda:                   None
resolve delta Britain vs France: 10
separate peace ready:            True
```

**Failure scenario.** Britain is at war with France; France holds Flanders and its vassal Holland holds Brabant and Amsterdam — the Low Countries design is entirely unfulfilled. A coalition forms during play (or Britain's boot alliances lapse via the §8.8.7a defensive-refusal termination). Austria's bloc out-masses France. `_hegemon(world, "Britain")` returns Austria — Britain's own co-belligerent — the raw guard doesn't fire because Britain is in nobody's bloc, no target is held by Austria's bloc, and `entry_satisfied` returns True. Britain takes `AGENDA_RESOLVE_SATISFIED` (+10 on `effective_p1_threshold`, `ai_diplomacy.py:955-956`) and `agenda_separate_peace_ready` returns True (`ai_diplomacy.py:986-990`), breaking coalition ranks at −30 war score instead of −50. Simultaneously `get_active_agenda`/`build_agenda_payload`/`get_agenda_covets` all return empty, so the player has no surface that could explain or contest it — and cannot buy Britain off, because the design driving Britain to the table is invisible to the acceptance and settlement scorers.

This is **not** recorded limitation D70, which is the opposite polarity (false *negative* for a court inside the dominant bloc holding its own targets, explicitly scoped to "when the denier and the hegemon are allies"). Here the denier is unallied and the reading is a factual falsity.

The degenerate form of the same bug sits two lines below: `if hegemon is None: return True` (`agendas.py:322-323`) — the last major standing reads every deny design satisfied regardless of who holds the targets.

**Minimal fix.** Stop scoping deny satisfaction to the hegemon bloc. Satisfaction is a statement about the listed provinces:

```python
own = set(world.get_bloc_members(nation))
return not any(_region_controller(world, r) not in own
               for r in (entry.get("regions") or []))
```

Keep guard 1 and D67's activation/satisfaction split. Then add a `TestInvertedHegemonyGeometry` arm that leaves co-belligerents at PEACE instead of hand-writing ALLIANCE rows (`tests/test_nation_agendas.py:323-325` currently hard-codes the assumption, which is why the geometry was never tested), and correct the §18 claim about coalition alliance states.

Two of three refuters independently reproduced this; one refuted on reachability grounds (arguing no production path dissolves an AI–AI alliance). That refutation is answered by the completeness-critic probe above: the coalition path needs no alliance dissolution at all — a coalition formed in-game simply never creates the rows.

---

### P2 — defect — `backend/commands/diplomatic_executor.py:226,237` — the diplomatic nation-picker shows a formed nation's dead name

```python
"label": display_nation(known_nation),
...
"Sire, which nation shall I approach? Our diplomatic landscape includes "
+ ", ".join(display_nation(n) for n in known_nations)
```

Probe with Italy proclaimed, driving the natural command `Talleyrand, open negotiations` through POST /command:

```
text: ...Our diplomatic landscape includes Austria, Bavaria, Britain, Denmark, Hanover, Hesse, Holland, Kingdom of Italy, Naples, ...
option: {"label": "Kingdom of Italy", "terms": {"target_nation": "KingdomOfItaly"}}
same response: "nation_display_overrides": {"KingdomOfItaly": "Italy"}
```

Neither repair door reaches it. `utils.gd:170-172` substitutes raw *tags*; the string is already humanized to "Kingdom of Italy" so `contains("KingdomOfItaly")` is false. `proposal_confirm_popup.gd:132/139` assigns `btn.text = original_label` verbatim. The backend's history door `apply_formation_names_to_history` *would* repair it but is wired only at `main.py:2790` for campaign-log lines. Meanwhile the F1 wizard's own nation list ships the raw tag and renders correctly through `Utils.display_nation_name` — this call site is the outlier, missed by the §17.1 sweep that took `dispatch.py`, `war_status.py`, `combat_executor.py` and `diplomatic_advisory.py` through `formed_display_name`.

Violates §11.8 stage 3 / P84 ("no surface may show the dead name — R7 pin") on the surface the player uses to talk to the nation he just created. Cosmetic only: `terms.target_nation` carries the correct tag, so the row functions.

**Fix.** `formed_display_name(world, n)` at both lines. `diplomatic_dialogue.py:952` is the same root and the same one-liner (world is in scope).

All three refuters confirmed; not settled by D65(b), which homes the *input* direction (name→tag resolver) to NA-6c.

---

### P2 — defect — `backend/commands/diplomatic_executor.py:5717` — yielding to an ultimatum after the pair falls to WAR still executes the full concession and reports "The peace holds"

`_handle_accept_ai_ultimatum` reads only `context["proposal"]` and `context["source_nation"]`, applies `_apply_ultimatum_demands`, and emits a fixed message. Its docstring asserts *"No diplomatic-state change: yielding preserves the peace; that is the point of yielding"* — nothing verifies the peace still exists. The dialogue is non-blocking (`ai_diplomacy.py:1262`) and lapses only at the start of the next end_turn, so it survives arbitrary state change across the player's whole turn.

Reproduced with zero player action: Austria issues an ultimatum in `_process_ai_diplomatic_phase` (`turn_manager.py:259`); Britain declares war on France and Austria enters via its own boot alliance cascade; `advance_turn` (`:294`) runs later in the same tick.

```
France-Austria state now: WAR
ultimatum dialogue survived: incoming_ultimatum
[yield] "...Conceded: 300 gold/turn tribute; Milan annexed; 5000 infantry conscripts. The peace holds — at a price."
```

Milan transfers, a perpetual tribute treaty is written to `active_treaties`, 5,000 conscripts leave the pool, and the game reports the peace holding while the two are at WAR. A milder arm of the same missing re-check: yielding to an issuer eliminated during the turn resurrects it (`Prussia active: False` → after yield `Prussia active: True`).

**Fix.** Re-check `world.is_at_war(world.player_nation, source_nation)` and issuer liveness before applying demands; pop the dialogue and return a void-demand refusal. Mirror in `_handle_reject_ai_ultimatum` so a void demand plants no pressure marker.

Two refuters confirmed; one refuted on reachability, arguing `form_coalition`'s `remove_matching` clears the dialogue and every player war route replaces it. That refutation covers the coalition and player-declaration routes but not the ally-cascade route reproduced above, where the issuer is dragged into an existing war by a third party's declaration.

---

### P3 — defect — `backend/game_logic/agendas.py:951` — an armistice both activates a guard_neutrality design and removes the war exemption

```python
if world.is_at_war(violator, holder):
    continue  # open war supersedes outrage
```

`is_at_war` is strict `== "WAR"` (`world_state.py:1524`) and `_guard_active` is `not get_nations_at_war_with(nation)` — both treat ARMISTICE as peace. So an armistice simultaneously wakes the paused opponent's guard design and strips the exemption for the army that is on its soil *because of that war*. Nothing in `cleanup_war_end` repositions marshals when `conclude_objectives=False` (`world_state.py:8096`).

```
Sweden campaigns onto Danish-held Jutland; bilateral armistice signed
violations during WAR:      []
violations under ARMISTICE: [{'violator':'Sweden','guard_holder':'Denmark','region':'Jutland'}]
relation -45 -> -70
```

−70 crosses `ARMISTICE_AUTO_PEACE_RELATION` (−60), so `_process_armistice_expiration` resumes war instead of maturing to peace. Requires an *uncapturable* guard province (Copenhagen's 10k garrison, or a fortified province under the occupation timer) — an unfortified one flips to the violator on entry and the own-soil exemption applies. The codebase disagrees with itself here: `diplomacy.py:281-283` states *"ARMISTICE is belligerent-adjacent and deliberately excluded; it is treated like WAR for this check"*, and `agendas.py:594` itself pairs `("WAR","ARMISTICE")` for the NA-2 entrench arm.

**Fix.** Widen line 951 to `world.get_diplomatic_state(violator, holder) in ("WAR", "ARMISTICE")`. Spec §5.9's written predicate ("not at war with the guard-holder") needs the same amendment — the code matches the spec, so this is a shared gap rather than an implementation slip.

All three refuters reproduced; severity ranged P2–P3, settling at P3 on trigger narrowness.

---

### P3 — defect — `backend/game_logic/ai_diplomacy.py:1382,1391` — the incoming-proposal/ultimatum notification composes the nation name from the raw tag

```python
f"Envoy from {nation}",
f"An envoy from {nation} has arrived with a proposal.",
```

No display resolution at all. Reproduced 4 and 17 turns *after* formation (two independent refuters):

```
[diplomatic_proposal] 'Envoy from Holland' / 'An envoy from Holland has arrived with a proposal.'
```

The client cannot repair it: `notification_bar.gd:379/441` route through `humanize_nation_keys_in_text`, which skips any key failing `_is_prose_safe_nation_key` — whose docstring at `utils.gd:194` literally names `"Holland"` as unsafe. Affects single-token formable tags only (KingdomOfItaly is multi-token and repairs client-side). `git blame -L 1377,1394` puts the entire block, both arms, in NA-5 commit `7fcfd8e` — new in-phase code. `build_ai_proposal_dialogue`'s `talleyrand_text` (`:1302/1310/1315`) has the same root.

**Fix.** `formed_display_name(world, nation)` at both arms, matching the §17.1 treatment already applied at `dispatch.py:130/166`, `war_status.py:420`, `combat_executor.py:1599`.

Two refuters confirmed with post-formation repros; one refuted, arguing the formation-tick instance is correctly contemporaneous (true — the AI diplomatic phase runs before the formation poll) and the remainder falls under D50/D65(b). The post-formation repros close that.

## 3. Coherence findings

### §0 G2 six-pillar observability — the arithmetic

Measured over 40 turns of live `TurnManager.end_turn` on the shipped world (an early probe using bare `advance_turn` recorded zeros everywhere — the enemy phase lives in `TurnManager._process_enemy_turns`; that was a probe artifact, not a finding).

| Pillar | Fires? | Magnitude vs. noise floor | Verdict |
|---|---|---|---|
| 1. Acceptance ±12/−8 | 0 / 864 AI evaluations | Summed outside the −60 composite floor (`diplomacy.py:6893`); measured to carry France→Austria 38→50, i.e. REJECT→ACCEPT | **Player-path only.** AI bilateral proposals carry no territorial vocabulary (100% `has_territory=False` across 22 shape buckets), and France is deckless (a §9 settled cut). The AI-side twin `agenda_settlement_mod` *does* price AI courts — `tests/test_nation_agendas.py:1962` scores Austria at −8 with an empty term list — so the pillar is not player-only in general, only in the bilateral seam. |
| 2. War resolve −8/+10 | 65 / 102 calls nonzero | Largest single non-personality term on `effective_p1_threshold` (base −40; war exhaustion contributes 0–5) | **Healthiest pillar.** 40-turn tally `{('Austria',−8):40, ('Russia',+10):27, ('Russia',−8):13, ('Britain',+10):5}` — fires continuously and flips sign as designs move. Mild boot flatness: all three coalition members read −8 on turn 0, indistinguishable from retuning the base to −48; differentiation appears ~turn 5. |
| 3. AI target bias | 150 picks, 103 multi-candidate, **0 exact-ratio ties**, 1 changed pick | Tie-break only by design | **Near-inert, but correctly built.** The aggressive P4 arm is an exact-float tiebreak (`enemy_ai.py:2683-2686`); the P7 distance credit fired 18 / 1096 calls; the strategic-region sort reordered design-first on all 16 covet-present calls. Reproducible in isolation (two equal-strength corps produce bit-identical ratios; every commissioned corps enters at exactly 5,000 — `recruitment.py:32,47`), so it is rare rather than dead. Balance observation, not a defect. |
| 4. Paymaster tiers | 22 / 30 ticks paid | 400 g/turn vs. Austria's ~+18 g/turn boot margin ≈ 22× | **Clean and live.** 200 → 300 (t2) → 400 (t4), saturating at cap thereafter. Boot turn pays nothing (D23, floor-exclusive, behaved as recorded). |
| 5. Pressburg separate peace | `agenda_separate_peace_ready` True on 51 coalition-member-turns; **0** coincidences with the −30..−50 window | −30 vs. the outer −40 P1 gate | **Wired, not observed firing.** Britain's war score sat +6..+22 all run because the probe player was passive. Driver limitation, not evidence of unreachability. |
| 6. Post-peace grudge | 0 events in 40 turns | +1/turn, cap 2 shared with `formation_grudge` | **Wired, not exercised.** No war *ended* in the run. The D24 `participant_meta` fix was verified separately on the real war-end seam: `Austria meta exit_path='separate_peace'` → `get_agenda_grudge_nations → ['Austria']` → threat 1. Window boundaries exact (present at exit+4, gone at exit+10). |

**Verdict: 4 of 6 pillars observable in unattended play; 2 wired-and-pinned but not organically triggered.** That matches the recorded §15 D31 limitation rather than exceeding it.

---

### §11.9 aggrieved/sponsor machinery — GR9-compliant deferral, not a dead promise

The unreachability is total and confirmed: no JSON in the repo authors `forms.aggrieved`, and `_resolve_sponsor` (`formations.py:236-250`) is structurally guaranteed to return `""` for every Class T formation, because `process_formations` skips vassals so the lord arm is dead and a first formation has no prior record. `get_formation_grudge_nations` gates on `player in (sponsor, current_lord)`, so the entire `formation_grudge` contributor is unreachable on every production path.

It nonetheless clears every GR9 bar: named owner (`§11.10-8`, ROADMAP row NA → NA-6c/NA-6d), landing slice, completion definition (spec P94's exact pins), STATUS tracking line (`STATUS.md:20`), and **behavior tests that exist today** (`tests/test_nation_agendas_formables.py:404-507` covers the blow, the empty-list negative, the unknown-nation skip, accrual, cap sharing, and the budget clamp). The dead arm is documented *at the line* — `_resolve_sponsor`'s own docstring states "the lord arm is dead for Class T today and lives for the NA-6c creation record" — and every skip is debug-logged. The `_form_under_player_sponsorship` test helper hand-writes the sponsor record, which is the suite openly conceding no production path produces one. **Deferred-with-a-contract. Not a finding.**

---

### Argued position: correct deny-satisfaction semantics

The current implementation asks *"is any listed region held by the currently-largest-bloc-I-am-not-in?"* That conflates two questions and produces both a false positive (the P1 above) and a false negative (recorded D70).

**Satisfaction for a deny design should be a statement about the provinces, not about bloc rankings.** The design is "the invasion coast may not stay in French hands" — the correct predicate is *"no listed region is held by a power outside my own bloc."* Concretely:

- Britain holds the Scheldt itself → satisfied. (Fixes D70 — and D70's framing as "an authoring decision about what deny means when denier and hegemon are allies" dissolves, because under this predicate the hegemon's identity is irrelevant.)
- An ally of Britain holds it → satisfied.
- France holds it, regardless of who is currently biggest → **not** satisfied. (Fixes the P1.)
- Nobody is left standing → satisfied, correctly, because no foreign power holds it.

This preserves D68 (allying into the hegemon's camp is dormancy, not fulfilment — that lives in `_deny_active`, the *activation* predicate, which is where the bloc question belongs) and D67 (the share floor gates activation, never satisfaction). It also removes the need for the raw-hegemon guard at `:316` entirely, since bloc rankings no longer enter satisfaction at all. `contain_hegemon` should keep its share-based satisfaction — containment genuinely *is* a statement about relative size — which is why I am not extending the change to that arm.

---

### P3 — coherence — `backend/game_logic/agendas.py:558,818` — a court that has WON its design cannot be priced at ENTRENCH

Both acceptance scorers gate on the active view (`view = get_active_agenda(...)`; `if view is None or view.survival: return 0`), while `get_agenda_resolve_delta` bypasses activation entirely via `_court_design_satisfied` on the raw `deck[0]`. So on the same tick:

```
Sardinia holds Piedmont only    active=house_of_savoy_restored  strip=-8  resolve=-8
Sardinia holds Piedmont+Savoy   active=None                     strip=+0  resolve=+10
Austria  holds Milan+Piedmont   active=redeem_italy             strip=-8  resolve=-8
Austria  holds all three        active=primacy_germany          strip=+0  resolve=+10
```

More complete success = *less* defence of the province just won. Spec line 39's fantasy — "a nation whose agenda is satisfied mid-war sues to lock its gains" — ships the "sues" half (+10 resolve, Pressburg) with nothing delivering "lock". The `agenda_acceptance_mod` docstring's promise of ENTRENCH for "a demand stripping a HELD design region" is unreachable exactly when the region is most held.

Mitigations that keep this at P3: the term is 8 points on an additive term outside the composite floor, sitting on top of ~−24 points of general territorial pricing; multi-entry decks still draw −8 via the formal-peace arm when the successor design is advancing; and ceding the region reactivates the entry, so the system partly self-corrects. Exposure is armistice-with-demand on any deck, formal peace where the successor is not advancing, and unconditionally for single-entry decks.

**Fix, if taken.** When `get_active_agenda` returns None, fall back to the highest-priority satisfied deck entry for the ENTRENCH-strip arm only. This is the same structural insight D43 already applied to the formation predicate ("activation is the exact complement of satisfaction") — the acceptance seams never received the equivalent. One refuter argued an author could defensibly answer "the term prices the *live* design"; that is why this is a coherence item for the owner to rule on, not a defect.

---

### P3 — coherence — `docs/ENEMY_AI_REFERENCE.md:141` — the P4 agenda-bias row cites the wrong helper

The row reads `(agendas.get_agenda_covets)`; `enemy_ai.py:623-624` calls `get_agenda_military_targets`. They are not interchangeable — probe on boot: `Britain deny → mil=[]` while covets returns Flanders/Brabant/Amsterdam. `git log -S` puts the wrong citation in commit `2890196` — the very NA-3 commit whose §14 records the acquire-only narrowing as an adversarial-review fix, and whose spec §14 L411 *claims* the reference doc was updated with its drift fixes (promise P33). `SYSTEMS_REFERENCE.md:3952` states it correctly, so the two reference docs now disagree.

Runtime risk is guarded — `tests/test_nation_agendas.py:1445` pins `_agenda_covet_set("Britain") == frozenset()` while `get_agenda_covets` is truthy, so a maintainer swapping the call site fails the pre-commit gate. **One-token doc fix.**

## 4. Delivered vs. claimed

| Promise | Slice | Delivered? | Evidence |
|---|---|---|---|
| P1 Decks are 1–3 authored JSON entries, validator-checked | NA-0 | ✅ | 10 decks / 15 entries in `europe_1805.json`; 18-case validator probe, every claimed rule caught |
| P2 Active agenda derived, never stored | NA-0 | ✅ | `_agenda_cache` derived; excluded from `to_dict`; flushed via `invalidate_bloc_members_cache` (27 call sites reach it) |
| P3 Exactly one active per nation per turn | NA-0 | ✅ | `get_active_agenda` loop; boot probe all 20 nations |
| P4 All six G2 pillars coupled in pass 1 | NA-2/3 | **Partial** | All six have production call sites; 4 observable in 40 turns of play, 2 (Pressburg window, grudge) wired-and-pinned but never organically triggered — see §3 table |
| P5 R162 ultimatums as NA-5, no further gate | NA-5 | ✅ | Rung at `ai_diplomacy.py:1067-1076`, literally between P7 and P8 |
| P7–P18 Blessed constants at value | NA-2/3 | ✅ | Tiers probed live 200/300/400 cap; violation −25 / 10-turn boundary exact; grudge window exact at exit+4 / gone at exit+10 |
| P19 `PAYMASTER_TREASURY_FLOOR` 2,000 authored | NA-0/3 | ✅ | Britain deck; floor-exclusive behavior per D23 |
| P20–P22 Formation rewards +2000 / +2 / −30 | NA-6a | **Partial** | Gold verified once-only and idempotent; stability inert in the direct-cession case (honestly omitted from the card by design); −30 has **zero authored input** (no `aggrieved` in any JSON) |
| P23 NA-5 constants (1.25× / 15 / 8 / 2 / 4) | NA-5 | ✅ | Boundary probed: 12,499 none / 12,500 issued; cooldown `{'Prussia\|ultimatum': 15}` set at issue after the territory check |
| P24 Boot pins (Austria/Prussia/Britain/Russia) | NA-0 | ✅ | Re-verified live in three independent probes |
| P25 Survival override / cache / round-trip pins | NA-0 | ✅ | Override fired organically (Bavaria t5, France t30) and round-tripped |
| P26 Satellite dormancy pins | NA-0 | ✅ | Both `id: None, override: True` for all 30 turns while vassalized |
| P27 NA-1 surfaces, no new popup | NA-1 | ✅ | Ledger row, war-room lines, rung-1.5 counsel, register bank, dispatch beat all verified live |
| P28 Acceptance pins both directions; corpus untouched | NA-2 | ✅ | +12 / −8 probed; corpus clean |
| P29 M1–M7 byte-identical | NA-3/6a | ✅ | Recorded green before and after; not re-derived |
| P30 Resolve / target-bias / paymaster / grudge / violation pins | NA-3 | ✅ | All re-probed; violation fires GR5 both directions (France −15, Austria −25) |
| P31 Rider (a) settlement per-court term | NA-3 | ✅ | 11th component wired at `settlement_scoring.py:2171`; per-court isolation verified |
| P32 Rider (b) preview positive row | NA-3 | ✅ | Reached on the armistice→peace route; the memo is a per-call local, no staleness path |
| P33 `ENEMY_AI_REFERENCE.md` drift fixes | NA-3 | **Partial** | Rung order, P4.78→P7.4 relabel, +75→+25 all correct; the P4 row's helper citation is wrong (§3) |
| P35–P44 Ultimatum gate answers | NA-5 | ✅ | Every gate falsified in probe; dtype whitelisted at both `main.gd` sites; capital doubly guarded; lapse≠rejection; no unilateral war |
| P45–P50 Formable mechanics | NA-6a | ✅ | `forms` validated; tag never changes; once-only + permanent; post-deck free via priority; announcement fan-out complete |
| P51–P52 The two T-formables | NA-6a | ✅ | Holland formed **organically** (see §5); Britain-deny satisfaction derived |
| P53–P55 Warsaw / Normandy / RomanRepublic | NA-6c/d | ⬜ | Unbuilt by plan |
| P64–P71 §11.6 UX contract | NA-6c/d | **Partial** | (7) ceremonial moment ✅ for T-formables; the other seven are NA-6c/6d scope |
| P72–P73 NA-6a DONE bar | NA-6a | ✅ | Latch, rewards-once, next-turn deck, save/load, no-formation-while-vassalized all verified |
| P82–P86 Proclamation content + never-do pins | NA-6b | ✅ | Layer 117 un-double-booked; ESC-safe; Acknowledge always enabled; both flags exist with `.import` siblings; boot `EXIT=0`, zero SCRIPT ERROR |
| P87–P92 §11.9 political implications | NA-6a | **Partial** | Validator + blow + contributor + cap-sharing all coded and tested; **zero authored input and the sponsor arm is structurally dead for Class T** — deferred with contract (§3) |
| P97 Six flag SVGs authored | NA-6a/b | **Partial** | 2 of 6 (Italy, UnitedNetherlands); the other four are NA-6c tags |
| P104–P105 NA-6a/6b bars | NA-6a/b | ✅ | Both met; XR-1 boot clean at this commit |

## 5. Refuted, worth knowing

**Did the AI visibly pursue a design over 30–40 turns? Mechanically yes, narratively barely.** Austria took Milan (one of `redeem_italy`'s three targets) under pure AI control by turn 31; covet sets stayed exactly the authored provinces; Britain's paymaster escalated 200→400 by turn 4 and paid 22 of 30 ticks. But no ultimatum, no violation, no separate peace, and no grudge fired in 40 turns of unattended play. Agenda state was **monotonic** — every decked nation flipped at most once and never flipped back — which independently refutes the oscillation hypothesis for the AI target bias.

**Did a formation occur organically? Yes, once — the first ever.** United Netherlands formed through real gameplay: `vassal.release_vassal("Holland")`, a Dutch marshal in Amsterdam, then repeated `attack Flanders` through `CommandExecutor` → garrison combat (12,000 → 6,000 → collapse) → `_attempt_region_capture`. No `region.controller` was ever assigned. The forming entry was **already INACTIVE** at the firing moment, confirming live the structural fact D43 protects. Rewards applied once and were idempotent across repeat calls; the proclamation payload came through a real `POST /command` and was not re-delivered on the next response. This closes half of residual risk D65(a). Italy was not organically formed (a scripting limitation, not a game defect).

**What does typing "Italy" get you after it forms? Nothing, exactly as recorded.** `propose peace to Italy` → *"Sire, which nation should I direct this proposal to?"*; `declare war on Italy` → same; `assess Italy` → Berthier's generic shrug. `propose peace to Kingdom of Italy` still works. Root cause: `_roster_nation_patterns()` builds needles only from `display_nation(key)` + `key`. This is recorded residual risk D65(b), homed to NA-6c — **not** re-reported as a finding. One detail for the NA-6c owner: the failure is a *generic* shrug, not the honest "I am not aware of a nation called 'X'" branch at `diplomatic_executor.py:80-86`, which is unreachable because resolution returns None before `target_nation` is populated.

**Other high-value refutations, so nobody re-investigates:**

- **`AGENDA_RESOLVE_ADVANCING` "stranded" by deck[0] scoping** — refuted by a discriminating test (`test_satisfied_first_entry_sues_sooner`, `tests/test_nation_agendas.py:420`) that pins the exact geometry, plus D43's explicit contrast between the whole-deck formation scan and the deck[0] resolve scope. The +10 is the phase's load-bearing Pressburg lever.
- **Post-formation designs are peacetime-only, so a conquered formation has no agenda** — refuted: `settlement_ratify.py:597` always transitions through PEACE, so cession-driven formation is a peace-state event by construction (probe: `merchants_peace` active immediately). And `guard_neutrality → None at war` is pre-existing type behavior — Ottoman and Denmark do it today with no formation involved.
- **The Ansbach trap can't arm against Prussia** — refuted: `armed_neutrality` is deck index 1 behind `hanoverian_prize`, and taking Hanover activates it (pinned at `tests/test_nation_agendas.py:125`). Acquire-then-guard is the authored arc, not shadowing; the latent-guard no-op is recorded D28 and test-pinned.
- **A queued second Proclamation destroys the first** — refuted: the `enemy_phase` carve-out at `main.py:574-580` means `_include_popup_passthroughs` is never called on the response carrying card A, so no competing modal can share it. Latent fragility if NA-6c widens the formation call sites; not live at this commit.
- **Authoring any deck disables the British subsidy world-wide** — refuted: `if not decks` is a deliberate world-mode switch (legacy byte-compat), documented at four layers, and a test pins the opposite of the implied fix.
- **`_agenda_covet_cache` staleness** — refuted: every consumer keys on a candidate, and `_unmet_targets` drops a region exactly when it stops being a candidate, so the stale delta can never be selected.
- **The ultimatum rung can fire during an armistice** — refuted: `armistice_cooldowns` (set to 5, `ARMISTICE_DURATION` also 5, expiry runs before decrement) closes the window on every reachable path. Worth noting as a latent coupling: raising `ARMISTICE_DURATION` without touching the literal at `world_state.py:7776` would open it.
- **The +12/−8 term is dead** — refuted: the AI-side twin `agenda_settlement_mod` charges AI courts the same constants with an empty term list (`tests/test_nation_agendas.py:1962`, passing).
- **`FORMATION_STABILITY_BONUS` is inert** — refuted for conquest paths (battle drops stability to 25 or below; probe `regions_lifted = 2`); true only for a pure cession with no combat, where the card honestly omits the line.
- **`_hegemon` degenerate cases** — swept clean: one-nation world, exact ties (deterministic sort), vassal courts, empty worlds. `identify_ranked_bloc_shares` is byte-identical to the max-only helper it extends.

## 6. What was not exercised

- **The formed nation as a diplomatic counterparty in the *input* direction** — the name→tag resolver is unpatched (D65(b), NA-6c).
- **A formed nation as formation sponsor, paymaster, or an active `guard_neutrality` holder.** `formations.py:338`'s `sponsor_display` uses the static `display_nation` and would show a dead sponsor name — unreachable with the two shipped Class T formables, live once NA-6c mints creation records.
- **Two same-tick formations with a pre-empting modal**, end to end. The backend overflow list is test-pinned; the client-side path was not staged.
- **The Pressburg −30 window** — 0 occurrences in 40 turns because the probe player was passive and coalition war scores stayed positive. Wired and pinned only.
- **An organic war *end***, so the post-peace grudge was driven through the war-end seams directly rather than played to. Mirrors recorded D31.
- **Live-LLM mode** — every campaign ran `LLM_MODE=mock`.
- **Godot rendering beyond boot + a headless Utils probe.** The engine boots clean (`EXIT=0`, zero SCRIPT ERROR, both new scenes instantiate) and the R7 chokepoints were exercised headlessly including the cache-flush transition, but no formation was observed rendering in a played session.
- **`deny_regions` / `contain_hegemon` formables in shipped content** — authored and run in a scratch scenario only (both fire correctly; only the progress marker is acquire-shaped). Recorded D65(c).
- **The full test suite** — targeted files only, per instruction. `tests/test_nation_agendas.py` 184 passed and `tests/test_nation_agendas_formables.py` 119 passed at this commit.
