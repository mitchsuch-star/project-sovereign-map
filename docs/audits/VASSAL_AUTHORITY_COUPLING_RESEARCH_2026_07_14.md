# VS-R Research Memo — Authority ↔ Vassal-Loyalty Coupling

> **File:** `docs/audits/VASSAL_AUTHORITY_COUPLING_RESEARCH_2026_07_14.md`
> **Prepared:** July 14, 2026 — lead-designer synthesis for the **VS-R gate**.
> **Owner spec:** `docs/VASSAL_DEEPENING_SPEC.md` §2 (research-first item).
> **Status:** research complete, **gate-pending**. This memo **supersedes the draft
> band numbers** in the spec where noted (esp. the `≥70 → +1` band, which is a
> hard test-pin violation). No code lands until the user gate blesses §"Recommended
> Numbers".
> **Method:** four adversarially-verified research strands — *history*,
> *authority-code*, *vassal-defection-code*, *jealousy-coherence* — 9 agents,
> ~1.07M tokens, every `file:line` re-Read at HEAD by an independent verifier; the
> historical timeline independently fact-checked (Grokipedia quotes dropped, dates
> re-sourced to Wikipedia / napoleon.org / Britannica).

---

## 0. Headline verdict — *would it play like Napoleon losing his vassals in real life?*

**Yes, on every axis except one — and that one exception is a required correction
the gate should bless.**

The 1812–14 collapse of Napoleon's satellite empire *was* **loss-of-grip →
loss-of-vassals**, and it maps cleanly onto a banded authority→loyalty coupling:

| Real event (1812–14) | Proposed VS-R mechanic | Faithful? |
|---|---|---|
| Russia catastrophe breaks the aura of invincibility; the enforcement army evaporates | Grip signal falls → satellite drift turns negative | ✅ the whole fantasy |
| Bavaria holds for neutrality, flips only when Napoleon can't guarantee its frontier (**Treaty of Ried, 8 Oct 1813** — guaranteed **sovereignty + no net territorial loss**) | "No cheap recovery" clause: at the spiral floor only land (VS-3) / autonomy / release / large subsidy arrest defection | ✅ the binding concession was *existential*, i.e. the big levers |
| **Saxony returns to Napoleon after Lützen/Bautzen** (spring 1813); the web holds through the summer armistice | One-way coupling → winning battles raises grip → drift returns to neutral, in-progress defections arrestable | ✅ **reversibility is essential and the one-way default delivers it** |
| Ried is the template; Saxon + Württemberg contingents flip **mid-battle at Leipzig** (16–19 Oct); Fulda (2 Nov), then Murat (Jan 1814), follow one by one | Cascade term: first flip raises defection *risk* (not certainty) for siblings | ✅ cascade is documented; keep it probabilistic |
| The Rhine states **switched sides and turned their armies on France** — they did **not** rebel into an independent war | Today the game only models **independent rebellion**; a defector becomes a lone belligerent, invisible to the enemy coalition | ❌ **the one unfaithful element — see Q7** |

**The correction:** the flagship historical outcome is *"the satellite joins the
enemy coalition and its army joins the enemy order of battle."* The game has no such
path today (coalition membership is static — **zero `members.append` sites** — and
rebellion always mints a vassal-vs-lord war). This memo recommends **VS-R v1 ship
grip-accelerated *independent* rebellion** (faithful *enough*, near-zero build cost,
reuses `check_vassal_rebellion`) and homes **coalition-defection as its own GR9
follow-on slice** — because it is genuinely new mechanism (target selection +
membership insertion + contingent transfer), not a tuning change.

One nuance the single loyalty scalar necessarily abstracts: history produced *three*
flavours of defection — **ruler flips** (Bavaria, Murat), **army flips while ruler
stays loyal** (Saxony's king was captured *for* his loyalty and lost ⅗ of his lands
at Vienna), and **populace flips while ruler stays** (Eugène's Italy fell to a Milan
insurrection from below while he refused a bribe). The scalar collapses these; that
is an acceptable abstraction, not a gate issue.

---

## 1. The history, verified (the grounding)

### 1.1 How the web was bound (1805–1810)

Napoleon bound clients with a *bundle* of levers, not one. The **Confederation of the
Rhine** (Rheinbund) was created **12 Jul 1806** (16 states; Napoleon hereditary
"Protector" of their foreign policy). The binders, and their game analogues:

| Real binder | Example | Game lever |
|---|---|---|
| **Land grants / aggrandisement** of loyal princes with conquered enemy land | **Peace of Pressburg, 26 Dec 1805**: Bavaria gets Tyrol, Vorarlberg, Trent, Brixen, Augsburg from Austria; Saxony/Baden/Berg/Württemberg enlarged | **VS-3** (give conquered land → loyalty) — *the signature Napoleonic tool; VS-3 is historically well-grounded* |
| **Status elevation** | Electors of Bavaria & Württemberg → **kings**; Baden/Hesse/Berg → grand duchies | *no clean lever; closest is the autonomy dial* |
| **Dynastic marriage** | Eugène ↔ Augusta of Bavaria (1806); Jérôme ↔ Catharina of Württemberg (1807); Stéphanie ↔ Baden | *no marriage system (noted-absent); not needed for VS-R* |
| **Obligatory military contingents** | ~63,000 men in the 1806 founding treaty (Bavaria 30k, Württemberg 12k…), later far higher; French garrisons at host expense | **shared-war** + **garrison** levers |
| **Continental System** — binder *and* irritant | Louis Bonaparte deposed & Holland annexed (1810) for refusing to enforce it — a vassal destroyed *by the binder* | *out of VS-R scope; noted so the gate doesn't expect it* |

### 1.2 The collapse, dated (verified)

- **1810** — Russia leaves the Continental System; Holland annexed. The strains begin.
- **Jun–Dec 1812 — the Russian catastrophe.** Of ~600,000+ who entered, roughly
  ~100,000 returned; the force included large German (~190k) and Polish/Lithuanian
  (~90k) contingents — *the satellite armies were physically destroyed alongside the
  French* (all figures approximate; sources diverge). **This is the hinge:** the aura
  of invincibility broke and the enforcement army evaporated *at the same moment*.
- **30 Dec 1812 — Convention of Tauroggen.** Prussian Gen. Yorck neutralises his
  corps by private armistice, *without his king's consent* (court initially disavows
  him). The first crack — a subordinate defects ahead of the sovereign.
- **28 Feb 1813 — Convention of Kalisch** → **17 Mar 1813 — Prussia declares war.**
  Prussia has flipped fully into the enemy coalition.
- **2 May (Lützen) & 20–21 May 1813 (Bautzen)** — Napoleon **wins both** (costly).
  **Frederick Augustus of Saxony breaks off his Austrian talks after Lützen and
  returns to the French fold.** *Reversibility evidence: a restored military position
  re-anchored a wavering satellite.*
- **4 Jun–10 Aug 1813 — Armistice of Pläswitz.** Austria mediates, then joins the
  Coalition (declares war 12 Aug). The autumn balance tips against Napoleon.
- **8 Oct 1813 — Treaty of Ried (BEFORE Leipzig).** **Bavaria** leaves the
  Confederation and joins the Sixth Coalition in exchange for a **guarantee of
  continued sovereignty and territorial integrity (with compensation for territory
  exchanged)** — *not* a frozen-borders deal (Tyrol in fact reverted to Austria,
  Bavaria compensated elsewhere). Threatened Napoleon's lines of retreat. **The
  keystone defection and the template for the rest.**
- **16–19 Oct 1813 — Battle of Leipzig ("Battle of the Nations").** ~5,400 Saxons of
  Reynier's VII Corps defect **mid-battle** to Bernadotte; Württemberg cavalry desert
  — tearing a hole in the French line. *Contingents flipping on the field itself.*
- **2 Nov 1813 — Treaty of Fulda.** **Württemberg** formally leaves and joins the
  Allies; sovereignty + recent gains secured. **4 Nov 1813** — the Allies proclaim
  the Rheinbund's formal dissolution (de facto at the ~19 Oct retreat).
- **11 Jan 1814 — Treaty of Naples.** **Murat** (Naples; Napoleon's brother-in-law)
  defects to Austria, pledging **30,000 troops against the Kingdom of Italy** to
  **keep his throne**. A family-appointed marshal-king betrays under survival calculus.
- **6 Apr 1814** — Napoleon abdicates unconditionally; **Treaty of Fontainebleau
  (11 Apr)** formalises it. **Eugène (Italy) stayed loyal to the end** — refusing a
  Bavarian offer of the Italian crown — but the **Milan insurrection (20 Apr)**
  toppled the kingdom from below.

### 1.3 The analytical core (the load-bearing design lessons)

1. **Defection tracked *perceived weakness*, not ideology.** The Rheinbund fragmented
   because of the *evident failure of French arms*, not coordinated popular revolt.
   The south-German dynasties were elites calculating survival (raison d'état);
   nationalism was a *secondary* driver (real in Prussia, not decisive for Bavaria).
   **This strongly endorses an authority/grip-coupled model.**
2. **It was a cascade.** Bavaria's *successful* defection at Ried gave the others a
   pattern they could see *work*. One credible flip legitimised the next.
3. **What arrested it was existential — or victory.** The peeling concession was a
   **guaranteed survival** (sovereignty + no net loss), which only the *winning* side
   could credibly offer. Conversely the one thing that demonstrably *re-anchored* a
   waverer was **Napoleon winning** (Saxony after Lützen). So "cheap levers stop
   working; only the big ones do" is right — and the biggest "concession" of all is
   **restoring your military position**.
4. **Switch sides ≠ go independent.** The single clearest game-unfaithfulness: the
   satellites *joined the enemy coalition and turned their armies on France*.
5. **Loss was contingent, not inevitable until late.** After Lützen/Bautzen the web
   held; defections only flooded once Austria joined and autumn turned. **A big enough
   1813 victory could plausibly have held them** — exactly the "risk, not certainty;
   reversible by winning" property VS-R wants.

---

## 2. The seven research questions, answered

### Q1 — Which authority signal drives the coupling?

**The problem the code surfaced (and my own read confirmed): `authority_tracker`
does NOT spiral on military collapse.** Verified:

- The only military-linked authority movers are the ±5 per-battle nudges, *each gated
  on an `outnumbering` condition* — being **overrun by a superior enemy makes
  `outnumbering` False → no dock** (`combat_executor.py:1461-1471`). Authority punishes
  *embarrassing* losses, not *catastrophic* ones.
- Losing your capital to an enemy **garrison assault** runs `_resolve_garrison_combat`,
  whose authority block is guarded `if marshal.nation == world.player_nation`
  (`:1642`, `:1750`) — **False when the enemy is the assailant → capital falls, zero
  authority change.** The auto-charge mirror omits the capital-loss arm entirely
  (`world_state.py:9288-9290`).
- No per-turn process folds `war_score` / territory / capital status into the tracker.
  **A player can lose the war, shed home provinces, and have Paris taken with
  `authority_tracker` sitting near 100** — high exactly when history says the
  satellites should defect. It is the *wrong spine* on its own.

`world.nation_authority[player]` is **worse — it is inert code.** Its mutator
`modify_nation_authority` (`diplomacy.py:7292`) is **never called**; its would-be
driver `_process_nation_authority` (`:9444`) *is* invoked per turn (`:8831`) but the
body is a literal `pass` (`:9458`); the player key is usually absent on Europe
(defaults to a frozen 60). **Do not key VS-R off it.**

The **only** signal already tracking collapse is the jealousy enemy proxy — but only
for enemies. `get_authority_proxy(world, nation)` (**`jealousy.py:343-366`**): player
branch returns raw `authority_tracker.authority` (no territorial term); enemy branch
is a pure collapse signal — capital held + homeland majority → **75**, capital lost OR
home-region minority → **25**, else **50**. This asymmetry is the crux of the design.

**RECOMMENDATION — a single-source "imperial grip" helper, symmetric by
construction.** Generalise the enemy proxy's territorial logic to *both* sides,
blending the player's `authority_tracker` (the *court / marshal-deference* component)
with the identical territorial-collapse term the enemy branch already carries. This
finally makes the player's grip respond to losing capital / homeland / war, and gives
the enemy coupling **for free (GR5)**:

```python
# home: backend/models/authority.py  (see the layering flag, §6)
def get_imperial_grip(world, nation) -> int:
    """Napoleon-style grip, symmetric. Court standing eroded by visible
    territorial collapse. Boot: player 100 / full empire → 100 (dormant);
    enemy intact → 75 (jealousy parity)."""
    if nation == world.player_nation:
        base = world.authority_tracker.authority      # court component (0-100)
    else:
        base = 75                                     # enemy court baseline (proxy parity)
    # territorial collapse term — same inputs the enemy proxy already uses,
    # now run for the player too:
    if not _capital_held(world, nation):        base -= GRIP_CAPITAL_LOST      # 40
    elif _homeland_minority(world, nation):     base -= GRIP_HOMELAND_MINORITY # 25
    if world.is_at_war(nation):
        ws = get_war_score_for(world, nation)   # live import at vassal.py:685
        if   ws < -50: base -= GRIP_WARSCORE_DEEP  # 15
        elif ws < -30: base -= GRIP_WARSCORE_LOSING #  8  (aligns w/ cascade -30)
    return max(0, min(100, base))
```

All dependencies are **real seams**: `world.get_nation_capital`,
`world.get_active_nations` / `is_at_war` (used in `is_capital_threatened`,
`jealousy.py:377-382`), the `get_war_score_for` import (live at `vassal.py:685`), and
`nation_starting_regions` (populated for *every* nation incl. the player,
`world_state.py:2214`; serialized with a derived fallback at `:5207-5220`).

**Boot returns (verified against the helper logic):** player at boot → **100**
(dormant); enemy intact → **75**; enemy capital lost → **35**; enemy capital + homeland
gone → graded toward the sub-30 the old discrete `25` signalled.

**Two scoping decisions the gate must make (→ Open Question #1):**
1. **Do NOT dock `authority_tracker` directly** as VS-R's spine — it is *also* read by
   `get_obedience_modifier` / `get_severity_modifier` / `get_trust_gain_modifier`
   (`authority.py:133/155/190`) and the jealousy bands; pushing it down on military
   defeat would silently make marshals disobey & object more severely for an unrelated
   reason. Keep the collapse response inside the *derived* grip helper.
2. **Jealousy-pin preservation.** The exact 75/50/25 enemy pins at
   `test_jealousy_v32.py:833/838/849` must stay green. **Recommended:** keep
   `get_authority_proxy` as-is for jealousy; make `get_imperial_grip` a **VS-R-only
   superset**. Migrating jealousy onto the graded helper is cleaner long-term but is
   out of VS-R scope — flag, don't silently do.

*Cheaper v1 fallback (if the gate wants the smallest possible slice):* key VS-R off
`get_authority_proxy` **as-is**. Enemy lords then spiral their satellites correctly;
the **player** only spirals via the marshal-deference exploit + botched-battle/
capital-region −5s — historically *thin* but not wrong. The `get_imperial_grip`
superset is the recommendation precisely because it closes that gap for the human
player, who is the one whose collapse the fantasy is about.

### Q2 — The coupling curve

The draft's 4-band curve (`≥70 +1 / 40–69 0 / 20–39 −2 / <20 −4`) has **two problems,
one of them a hard test pin**:

1. **`≥70 → +1` must become `0`.** This is not soft advice — it is a **boot-dormancy
   pin against ~10 test files** (8 `TestLoyaltyTicks` pins + 4
   `test_vassal_recovery_lever` pins, all verified byte-exact:
   `test_satellite_drift_now_surfaces` asserts `delta == -2`,
   `test_grant_autonomy_reverses_drift` asserts `+1`, both at default authority 100).
   `process_vassal_loyalty`'s `_contribute` closure **records only nonzero values**
   (`vassal.py:276`), so a grip term returning `0` at healthy authority is
   *byte-identical*. A `+1` "ascendant" bonus is a **balance change**, not dormant
   coupling. **Coupling is negative-only, spiral-band only.**
2. **The interior thresholds (40, 20) don't match jealousy's salient lines (70, 30).**
   A player at authority 35 sits *above* jealousy's `<30` (marshals calm) yet the
   draft's 20–39 band already bleeds vassals — two unrelated dials, undercutting "one
   grip". Anchor on the shared breakpoints so crossing a line lights up **both** systems
   as one felt moment.

**RECOMMENDED CURVE — anchored on jealousy's 70 / 30:**

| Grip band | Vassal drift term | Rationale |
|---|---|---|
| **≥ 70** (`AUTHORITY_SUPPRESS_ABOVE`) | **0** (no contribution) | Same line that calms the marshals. Byte-identical boot. |
| **30 – 69** | **0** (neutral) | No coupling; ordinary autonomy drift governs. |
| **< 30** (`AUTHORITY_ACCELERATE_BELOW`) | **−2** loyalty/turn | Same line that makes the army infight. The one advertised spiral threshold. |
| *(optional nested)* **< 15** | **−4** floor | Only if playtest shows −2 too gentle; a VS-R-internal refinement *below* the shared 30 line — 30 stays the single advertised threshold. |

Applied **additively** to the existing `AUTONOMY_DRIFT` (`vassal.py:25` =
`{PUPPET:-4, SATELLITE:-2, AUTONOMOUS:+1}`). **Worst realistic case** = puppet (−4) +
spiral floor (−4) = **−8/turn ≈ 13 turns** 100→0 — dramatic but slow enough to arrest.
**Never a multiplier** — that is the one shape that yields unrecoverable collapse;
reject it. A **per-turn magnitude cap of −4** on the grip term (non-stacking) is a hard
requirement.

**Enemy side is auto-bounded (GR5 bonus):** because the enemy proxy floors at 25
(`jealousy.py:364-365`), an enemy lord can never reach the sub-15 `−4` band — enemy
VS-R bleed tops out at the `−2` tier. Sacking an enemy capital (proxy → 25) wavers
*their* satellites at −2, recoverable if they retake it. The discretisation does the
bounding for free.

### Q3 — The "no cheap recovery" clause

**The crux of the brief, and the strongest history match.** Once collapse was visible
the binding concession was *existential* — guaranteed sovereignty + no net loss (Ried,
Fulda) — which in game terms is precisely the **big** levers: a **land grant (VS-3)**,
**full release / autonomy-up**, or a **large subsidy**. Token invest / small subsidy
failing at the floor is faithful.

**Shape — a lever-effectiveness multiplier, not a block.** No single-source lever
helper exists today (levers are scattered). Introduce:

```python
def get_authority_lever_multiplier(world, lord) -> float:
    """1.0 at healthy grip (byte-identical boot); blunts CHEAP one-shot
    levers in the spiral band."""
    grip = get_imperial_grip(world, lord)
    if grip >= AUTHORITY_ACCELERATE_BELOW:   # >= 30
        return 1.0
    return VS_R_CHEAP_LEVER_MULT             # e.g. 0.40 in the <30 spiral band
```

**Which levers it hits (v1):**

| Lever | Site | Softened? |
|---|---|---|
| **Invest** (+10 one-shot) | `invest_in_vassal:822` | ✅ `old + int(INVEST_LOYALTY_GAIN * mult)` |
| **Autonomy-up** (+10 one-shot) | `change_vassal_autonomy:875` (upgrade branch **only**) | ✅ |
| Token subsidy (+1/100g per turn) | `process_vassal_loyalty` step 3, `:307` | ⚠️ **Open Q #2** — v1 leaves full-strength; a *large* subsidy should stay a valid existential lever |
| Autonomy-**down** (−15) | `:879` | ❌ never — you don't want low grip to *cushion* a downgrade |
| **VS-3 land grant** | (VS-3 slice) | ❌ never — **the premier arresting lever** |
| **Full release** | `release_vassal` | ❌ never — an existential concession |

**Critical history addendum:** the single most effective "concession" was **restoring
the military position** — Saxony re-anchored because Napoleon *won* at Lützen. This
falls out of the one-way coupling automatically (a battle win raises grip → drift
returns to neutral → in-progress waver arrests), but it **must be explicitly verified
in the recoverability test**, not assumed. The clause is really *"only existential
concessions **or winning** arrest it."*

**Copy home:** the healthy-band `recovery_hint` (`vassal.py:388-392` — *"Invest,
garrison their capital, or grant autonomy to steady them."*) is in *tension* with this
clause. Add a **spiral-band variant** naming *land grant / large subsidy / release /
win a decisive battle* — a copy change the gate should bless, homed at that line.

### Q4 — One-way vs feedback loop

**RECOMMEND ONE-WAY (authority → loyalty) for v1.** Do not feed vassal state back into
authority. Verified justifications:

1. **Preserves recoverability.** Jealousy's *only* authority writers — Fontainebleau
   −2 (`jealousy.py:1281`), mediation/force-reconciliation −3/−5 (`:1173/1217/1226`) —
   are **all player-choice-gated**; authority never drains automatically per turn. A
   two-way VS-R (losing vassals → −authority) would introduce the **first automatic,
   non-player-gated authority sink**, firing hardest exactly in the spiral zone where
   Fontainebleau *also* fires (≥3 marshals eroding). That closes a brakeless loop:
   low authority → vassal loss → −authority → more drains → more vassal loss. Precisely
   the unrecoverable spiral the spec warns against.
2. **One-way already delivers the full fantasy.** Grip spirals → satellites loosen →
   the player spends *real* concessions → grip recovers through **wins** (+5) → the
   instant it crosses back above 30, VS-R relaxes. History's actual recovery channel
   *was* "military victory raising grip" (Saxony after Lützen) — already modelled.
3. **Non-compounding by construction.** Both systems *read* grip; only jealousy
   *writes* it, and only on player choice. VS-R read-only → co-fire (thematically
   correct) without ever multiplying into collapse.

**If a bolster term is ever revisited** ("only if v1 feels inert"): constrain to
**asymmetric, small, capped, positive-state-gated** — a loyal satellite empire grants
a tiny per-turn authority trickle **only while authority is already ≥ a healthy floor,
never in the <30 zone**. Polishes a winning position; can never auto-rescue a spiral.
Bounded; not v1.

### Q5 — Interaction with jealousy (compounding guardrails)

**Thematically correct co-firing:** jealousy and VS-R measure **two casualties of one
cause** (marshal cohesion vs. satellite cohesion) — the 1813–14 fantasy exactly, not a
double-count.

**The load-bearing structural fact (verified as the strongest claim): jealousy does
NOT autonomously drain authority.** A full grep finds exactly four authority writes,
every one player-choice-gated inside a petition handler. **There is no per-turn
automatic authority sink.** As long as **VS-R stays read-only on authority (Q4
one-way)**, both systems *read* the spiral zone but neither closes a loop → a
**pressure spike, not a runaway**: a single combat win (+5) relaxes *both* next turn.

**Guardrails (all required):**
1. **Reversible, latch-free.** Recompute drift from *current* grip every turn (mirror
   jealousy's derived −1 that auto-restores). **Do NOT mirror jealousy's permanent
   escalation track** (`_check_escalation`, level-2 permanent −1 at
   `jealousy.py:584-585`, level-3 forced spiral at `:611-613`) — vassal loyalty already
   carries its own irreversibility (rebellion at 0 → WAR + marshal transfer + cascade
   −10).
2. **Additive + capped, never multiplicative** (per Q2). A per-turn magnitude floor of
   **−4** on the grip term, **non-stacking**.
3. **Defection is RISK, not certainty.** Route the spiral-floor outcome through the
   existing random-roll `check_defection_cascade` (`vassal.py:654` — gated
   `war_score < −30` at `:688` **AND** `loyalty < 50` at `:672`, roll
   `random() < (50-loyalty)/100` at `:698-699`) — **not** a deterministic flip. Matches
   "he *may* lose them". **Watch the indirect double-count:** grip drift lowers loyalty,
   which *raises* that roll's probability. The roll doesn't read grip directly, but
   drift feeds it — the per-turn cap (guardrail 2) is what keeps this from running away.
4. **Stagger the crises — opposite polarity on capital-threat.** Jealousy goes
   **silent** when the capital is threatened (`is_capital_threatened` → `continue` at
   `jealousy.py:1408-1409`; survival override). **Keep VS-R ACTIVE there** — do not copy
   the suppression. Army-infighting when grip is merely low; satellite-flight when the
   capital is under the knife. More legible **and** more historical (the Rhine states
   flipped as Paris fell). *This is the key de-compounding lever.*
5. **Recoverability test (mandatory).** A full-spiral boot (all 3 French satellites,
   grip pinned <30) must take **≥ N turns** to fully collapse *and* be arrestable by
   winning battles back above 30. "He MAY lose them" = risk, not certainty.

### Q6 — Boot-band & fixture safety

**Confirmed dormant at authority 100 / full empire → grip = 100 → drift term = 0.**
Because `_contribute` skips zero (`vassal.py:276`), the healthy band is byte-identical.

**VS-R v1 needs ZERO new serialized fields.** Every input already persists:
`authority_tracker` (`world_state.py:4764/5183`), `world.vassals` loyalty
(`:4876/5383`), `nation_starting_regions` (`:4785/5207-5220`), `region.controller`,
war_score (derived). The grip term is *derived*, not stored — same pattern as the
jealousy crown's derived −1. No `to_dict`/`from_dict` change, no
`test_serialization_enforcement` churn, no SAVE_FORMAT row.

**Exact pins that stay green (verified byte-for-byte):**

| Test | Pins | Guaranteed by |
|---|---|---|
| `test_vassal_recovery_lever.py:56` | satellite `delta == -2` | grip 100 → term 0 |
| `:109` | below-band `delta == -2` (loyalty 30 but authority 100 → keys off **lord's** grip, not vassal loyalty) | " |
| `:127` | VS-2 `delta == -2` | " |
| `:134-136` | VS-2 war-weariness *absence* | " |
| `:151` | invest 50→60 | `get_authority_lever_multiplier` returns exactly 1.0 at healthy grip |
| `:163` | autonomy-up `before + 1` | " |
| `test_session5_diplomacy.py::TestLoyaltyTicks` (8 pins) | puppet 60→56, satellite 60→58, autonomous 60→61, garrison 65, shared-enemy 60, lord-win 61, lord-loss 52, relation 60 | bare `WorldState()` at authority 100 → term 0 |
| **E1 economy band** | vassal_tribute gross unperturbed | 3 boot French satellites (Holland/KingdomOfItaly/Switzerland, `nation_config.py:408-412`) seed `loyalty=100`; cannot rebel in a 6–8-turn window at grip 100 with a 0 term |

At-risk bare-world drift pins to re-run (same family, not line-verified):
`test_diplo_refinement_wave1.py:273-286`, `test_deep_audit_session2.py`,
`test_w6_dispatch_rewrite.py:317-327`, `test_session8c_popups_notifications.py`,
`test_audit_part2.py`, `test_audit_minor_2026_03.py`.

### Q7 — Defection mechanics at the spiral floor

**Today (verified crux): independent rebellion only.** `loyalty <= 0` →
`check_vassal_rebellion` (`vassal.py:505`): `del world.vassals[...]`,
`ensure_war_instance_for_pair(entry_path="vassal_rebellion")` (from
`settlement_helpers.py:614`), `set_diplomatic_state(WAR)` with the **vassal as
`root_aggressor`**, marshal transfer-back, cascade −10 to siblings.
`_process_war_cascade` pulls in the *lord's* allies as **defenders of the lord** — it
does **not** enroll the vassal into any enemy coalition. **The vassal fights alone.**
Coalition membership is static: `active_coalition["members"]` is built once at
`form_coalition` (`coalition.py:1173/1234`); grep confirms **zero `members.append` /
`add_coalition_member` sites** post-formation.

**History says this is wrong for this scenario.** The Rhine states switched sides and
turned their contingents against Napoleon (Bavaria's army to the Coalition;
Saxons/Württembergers firing on the French at Leipzig; Murat's 30,000 against the
Kingdom of Italy). The faithful outcome is *flip to an existing enemy coalition,
contingent joins the enemy order of battle.*

**RECOMMENDATION — a two-stage build:**

- **v1 (this slice): grip-accelerated *independent* rebellion.** Reuse
  `check_vassal_rebellion` **unchanged**; the coupling simply feeds continuous loyalty
  drift into the *same* collapse condition that already fires the one-shot
  `check_defection_cascade` roll. Near-zero incremental build cost, all existing seams,
  historically *adequate* (a satellite you can no longer control turns hostile). Ships
  the fantasy.
- **v1.x GR9 follow-on slice — "The Defection" (coalition-join):** the flagship-faithful
  outcome, homed explicitly per Golden Rule 9. Build cost **moderate** — two genuinely
  new pieces: (1) **target selection** — pick *which* enemy/coalition the vassal joins
  (grounded default: the coalition currently at war with the lord holding the strongest
  war_score); (2) **coalition membership insertion** — explicitly insert the defector
  into `active_coalition["members"]` + seed its coalition relations, plus point the
  marshal transfer-back *at* the lord as a coalition combatant. Grafting this onto the
  rebellion seam risks the `war_instance_merge_required` hazard the code already guards
  (`vassal.py:584-599`) — hence a **separate slice with its own gate**, not a v1 bolt-on.
  Its serialized `defected` flag lands with it, not before.

---

## 3. Interactions — the collapse scenario, turn by turn

A concrete *"Napoleon after a failed Russian campaign"* player experience, showing
every interacting system:

- **T0 — grip 100.** All three French satellites at loyalty 100. VS-R fully dormant.
  Marshals calm (jealousy >70 dampen). Nothing on any board hints at fragility.
  *(Boot-band safety, Q6.)*
- **T1–T3 — the reversal.** The player loses a string of battles; the *derived grip*
  helper (Q1) reads the falling war_score and lost homeland and drops grip toward the
  30s — **the crucial fix: the old `authority_tracker` would have stayed near 100 here.**
  Marshals *and* satellites both begin to feel it as grip crosses 70 (jealousy
  hair-trigger pairs wake; VS-R still 0 in the 30–69 neutral band).
- **T4 — grip < 30, the spiral line.** *Both boards slip at the same number* (Q2 shared
  threshold). Marshals infight (jealousy accelerate). Satellites bleed −2/turn on top of
  autonomy drift. The dispatch surfaces the new grip contribution beside "satellite
  drift" (`_contribute` label *"the Emperor's faltering grip"*).
- **T4–T6 — enemy courting scales up.** `attempt_vassal_courting`
  (`vassal.py:1109`, enemy-only) is grip-scaled: the hard `loyalty < 50` unlock
  threshold widens and `loyalty_reduction` (15/5) amplifies when the *player's* grip is
  low — the Allies peel satellites precisely when Napoleon looks weak (**the Treaty of
  Ried dynamic**). Bounded by the existing 3-turn cooldown + one-vassal-per-nation-per-
  turn cap so it's pressure, not a one-turn wipe.
- **T5 — the player's choice: cheap vs. existential.** The player tries **invest** (+10)
  — but `get_authority_lever_multiplier` (Q3) blunts it to +4 in the spiral band. It
  slows one vassal; it does not hold the empire. The dispatch's spiral-band
  `recovery_hint` now names the real levers.
- **T6 — the arresting move.** The player grants **Kingdom of Italy a conquered
  province via VS-3** (premier arresting lever, never softened) — a big, real loyalty
  jump — *or* wins a decisive battle that pushes grip back above 30, which
  **auto-arrests the whole spiral** (Saxony-after-Lützen; the strongest arrestor of all,
  Q3 addendum). This is the *"restore your military position to hold them"* beat, and
  it's why the one-way loop (Q4) is correct: recovery flows through *winning*, not a
  bolster term.
- **T7 — the domino, if he doesn't.** If the player instead lets Holland hit loyalty 0,
  `check_vassal_rebellion` flips it (v1: independent rebellion) and cascades −10 to Italy
  and Switzerland — raising *their* `(50-loyalty)/100` defection roll next turn (Q5
  guardrail 3). Turn-bounded to one wave/turn (`vassal.py:520-522` snapshots before the
  cascade), so it's a legible domino, not an instant collapse. *(Continental System
  resentment — a real binder-turned-irritant — is explicitly **out of VS-R scope**;
  noted so the gate doesn't expect it here.)*
- **Reversibility throughout.** At no point is the spiral latched. Any turn the player
  claws grip back above 30, VS-R relaxes to 0, courting re-locks, and in-progress
  wavering arrests — faithful to 1813's contingency (the web held through the summer
  armistice; loss became inevitable only after Austria joined and the autumn campaign
  turned).

---

## 4. Recommended numbers block (every constant the gate must bless)

*All flagged in-band tunable; structural changes escalate.*

| Constant | Recommended | Home | Rationale |
|---|---|---|---|
| `AUTHORITY_SUPPRESS_ABOVE` | **70** *(reuse)* | `jealousy.py:66` → relocate to `authority.py` | Shared "one grip" line; boot-dormant edge |
| `AUTHORITY_ACCELERATE_BELOW` | **30** *(reuse)* | `jealousy.py:67` → relocate | The one advertised spiral threshold |
| `VS_R_DRIFT_ASCENDANT` | **0** | `vassal.py` | **Not +1** — hard boot-dormancy pin (Q2/Q6) |
| `VS_R_DRIFT_NEUTRAL` | **0** | `vassal.py` | 30–69 band |
| `VS_R_DRIFT_SPIRAL` | **−2** | `vassal.py` | <30 bleed; puppet worst-case −6/turn |
| `VS_R_DRIFT_FLOOR` *(optional)* | **−4** below grip 15 | `vassal.py` | Only if −2 too gentle; nested under the 30 line |
| `VS_R_DRIFT_CAP` | **−4** (non-stacking per turn) | `vassal.py` | Q5 guardrail 2 — prevents runaway |
| `VS_R_CHEAP_LEVER_MULT` | **0.40** in <30 band | `vassal.py` | Invest +10 → +4; blunts cheap recovery |
| `GRIP_CAPITAL_LOST` | **−40** | `authority.py` grip helper | Enemy parity (intact 75 → capital-lost 35) |
| `GRIP_HOMELAND_MINORITY` | **−25** | " | Majority of homeland overrun |
| `GRIP_WARSCORE_DEEP` / `_LOSING` | **−15** / **−8** | " | war_score < −50 / < −30; aligns with cascade `-30` |
| Courting unlock widen | `50 → 50 + spiral_bonus(grip)`, **0** at grip ≥ 30, up to **+15** at grip 0 | `vassal.py:1132` | Allies peel weak-Emperor satellites; 0 at healthy = pins green |
| Courting effectiveness scale | ×1.0 healthy → **×1.5** at grip 0 on `loyalty_reduction` | `vassal.py:1152/1154` | Bounded by existing cooldown / one-per-turn cap |
| Recoverability floor `N` | full-3-satellite spiral collapse **≥ 8 turns** | test | "He MAY lose them" — risk, not certainty |

---

## 5. Open questions for the gate

1. **Grip helper vs. direct dock (Q1).** Bless the *derived* `get_imperial_grip`
   superset (recommended) rather than docking `authority_tracker` directly? Keep
   `get_authority_proxy` untouched for jealousy (preserving
   `test_jealousy_v32.py:833/838/849`) vs. migrate jealousy onto the graded helper
   later? *(Cheapest v1: use `get_authority_proxy` as-is and accept a thin player-side
   signal — see the Q1 fallback.)*
2. **Does the multiplier hit the per-turn subsidy (Q3)?** v1 recommends softening only
   invest + autonomy-up (the "cheap" one-shots), leaving subsidy full-strength so a
   *large* subsidy stays a valid existential lever. Confirm.
3. **Coalition-defection now or later (Q7).** Bless v1 = grip-accelerated *independent*
   rebellion, with coalition-join homed as a separate GR9 slice? (Recommended — moderate
   build cost, genuinely new mechanism.)
4. **Optional −4 floor (Q2).** Approve the nested sub-15 `−4` band up front, or hold it
   for post-playtest tuning?
5. **Layering relocation (§6).** Approve moving `get_authority_proxy` +
   `is_capital_threatened` + the two breakpoint constants into `authority.py` so "one
   grip" is literally one module — or accept a recorded `vassal.py → jealousy.py` import
   deviation?
6. **Copy bless (Q3).** Approve the spiral-band `recovery_hint` variant naming *land /
   large subsidy / release / win a decisive battle*.

---

## 6. Seams table (for the eventual build) + architecture flag

| Purpose | File:line | Note |
|---|---|---|
| **Signal helper (new)** | `backend/models/authority.py` | `get_imperial_grip`; relocate `get_authority_proxy` + `is_capital_threatened` + breakpoints here |
| Signal today (reuse for GR5) | `jealousy.py:343-366` | `get_authority_proxy`; enemy 75/50/25 floors auto-bound enemy VS-R |
| Breakpoint constants | `jealousy.py:66-67` | `AUTHORITY_SUPPRESS_ABOVE` / `ACCELERATE_BELOW` |
| **Drift hook (insert)** | `vassal.py:353 → 361` | between step-6 relation `_contribute` and `# Apply delta`; `_contribute("the Emperor's faltering grip", authority_drift(grip))` |
| Event-surface gate | `vassal.py:371` | `abs(delta) >= 2` already surfaces a −2 grip term |
| recovery_hint copy | `vassal.py:388-392` | add spiral-band variant |
| **Lever multiplier (new)** | `vassal.py` | `get_authority_lever_multiplier`; **must return exactly 1.0 at healthy grip** |
| Lever attach — invest | `vassal.py:822` | `old + int(INVEST_LOYALTY_GAIN * mult)` |
| Lever attach — autonomy-up | `vassal.py:875` | upgrade branch only; **never** the `:879` −15 downgrade |
| Courting scale — unlock | `vassal.py:1132` | widen the `loyalty < 50` gate by grip |
| Courting scale — effectiveness | `vassal.py:1152/1154` | scale `loyalty_reduction` 15/5 by grip; bounded by cooldown `:1136-1139` + `:1194` cap |
| Defection roll (reuse) | `vassal.py:654` (`check_defection_cascade`) | `war_score<-30` + `loyalty<50` + `random()<(50-loyalty)/100`; risk not certainty |
| Rebellion path (v1 reuse) | `vassal.py:505` (`check_vassal_rebellion`) | `ensure_war_instance_for_pair` from `settlement_helpers.py:614`; cascade −10 at `:611-614` |
| Coalition-join (GR9 follow-on) | `coalition.py:1173/1234` (static `members`) + `diplomacy.py:7996` (`_attach_cascade_pair`) | new target-selection + `members` insertion + `defected` flag |
| war_score import (live) | `vassal.py:685` | `from backend.game_logic.diplomacy import get_war_score_for` |
| Serialization (no change) | `world_state.py:4764/5183` (authority), `:4876/5383` (vassals), `:4785/5207` (regions) | all inputs already persist; v1 = zero new fields |

**Architecture flag (Open Q #5):** `get_authority_proxy`, `is_capital_threatened`, and
the two breakpoint constants currently live *inside* `jealousy.py`, which imports
`dotation` and sits high in the stack; `vassal.py` is lower and more independent. A
`vassal.py → jealousy.py` import inverts the natural layering and risks a circular
import. **Recommend relocating the three shared items to `backend/models/authority.py`**
(verified to exist, houses `class AuthorityTracker`) so both jealousy and vassal import
*down* into one module — making "one grip" literally one source of truth. If relocation
is rejected, the import is tolerable but should be a recorded deviation.

---

## 7. Net build shape for v1

One pure derived helper (`get_imperial_grip`) + one lever multiplier + one banded
`_contribute` term + two courting knobs + one copy variant. **Zero new serialized
fields. Boot-dormant at authority 100.** Coalition-defection ("The Defection") and any
authority-bolster loop are explicitly homed as **later, separately-gated slices (GR9)**.

**Two things to press at the gate above all:** (1) key the coupling off a **derived
"imperial grip"** so the *player's* collapse is legible (the raw tracker stays high in
a real military disaster); (2) make the high-authority band **0, not +1** — it is a
hard boot-dormancy pin, not a preference.

---

*Prepared July 14, 2026 for the VS-R gate. Historical timeline independently
fact-checked; every `file:line` re-Read at HEAD by an independent verifier. No code
until the gate blesses §4.*
