# Napoleon — "The Emperor Takes the Field" (row NP)

> **Status: ✅ GATE RETURNED August 15, 2026 (same day) — v0.2. Gate record
> = §14.1, authoritative where it amends the body.** Q2/Q4/Q5/Q8 ruled by
> the user (Q2 with a historical refinement folded into §7; Q8 delegated
> and ruled as the user's middle path — see §10/§13 NP-6); Q1/Q3/Q6/Q7/Q9
> stand at their recommended defaults, presented in chat and unobjected —
> treated as blessed unless amended before NP-0 starts. Authored from a
> five-reader seam survey of master (marshal substrate, command flow, the
> glory/jealousy court, combat/AI/harness blast radius, UI surfaces + prior
> design intent).
>
> **Slot (user direction, Aug 15):** after the PC15 fix slice, BEFORE
> position 10 (the shippable build) — "the biggest item yet."
> **Routing note:** the owed played 20-turn campaign should run AFTER this
> row lands, so the campaign evaluates the game WITH its Emperor (the same
> ruling that put the HC slices before the campaign). User's call at the gate.
>
> **Reading map:** §1 why · §2 pillars + never-do pins · §3 the object ·
> §4 the hand (command) · §5 the presence (combat/AI) · §6 the court
> (glory/jealousy) · §7 the peril (capture) · §8 the seat (Paris) · §9 the
> stage (UI) · §10 symmetry · §11 blessed numbers · §12 blast radius &
> conscious pin flips · §13 slices · **§14 THE GATE** · §15D deferrals · **§15 LANDING RECORD**.

---

## §1 Why this, and why it is the biggest item yet

The game has asserted the player's identity from the first boot line —
`main.gd:635` prints **"You are Napoleon Bonaparte."** — and then never
embodies it. The player is a disembodied "Sire": 694 occurrences of the
address across 47 backend files, an `AuthorityTracker` whose own docstring
says it "tracks Napoleon's perceived authority," a diplomatic ledger row
called **The Emperor's Own Exposure**, a Gazette lead that credits "the
Emperor's genius" — and no Emperor anywhere on the map.

Meanwhile the roster already models everything an embodied Napoleon needs:
marshals with skills, personalities, relationships, glory, capture and
ransom, war-table pieces, diorama figures, portraits. The one man the whole
court orbits is the one man not in `world.marshals`.

This row puts him there. Not as a new character — as **the literalization of
the player**. You have been the voice; now you are the man, and the man can
only be in one place. That single constraint — presence as a scarce resource
— is the design. Every mechanic below is a consequence of it:

- **The Presence** (§5): where the Emperor stands, France fights harder and
  the enemy hesitates — Wellington's "his presence on the field made the
  difference of forty thousand men."
- **The Shadow** (§6): battles won under his eye are HIS victories. Marshals
  who want glory need commands away from him — the real engine of the
  Marshalate's ambition, and the existing jealousy economy priced by it.
- **The Peril** (§7): the man can be taken. The Empire is a person; put the
  person at Austerlitz and you have wagered the Empire.
- **The Seat** (§8): Paris governs better with him in it. The field fights
  better with him at the front. He cannot do both — the strategic dilemma
  of 1805–1814 in one movement decision per campaign phase.

Prior intent already points here: `ROADMAP.md:1017` (Courier Delay, planned)
assumes "Napoleon's HQ location matters" with a region-distance metric;
positions 12–13 are named **"The Emperor's Designs"**; the tester README
opens "You are Napoleon." This spec builds the anchor those rows assume.

## §2 Design pillars and never-do pins

1. **Embodiment, not addition.** Napoleon is the player's avatar, not an
   NPC. He never objects, never defies, never clarifies, never petitions,
   never speaks a voice line (Berthier narrates him; the player speaks AS
   him). Any surface where Napoleon would address the player is a defect.
2. **A marshal in the pipeline, a sovereign in the rules (GR3/GR5).** He
   lives in `world.marshals` and rides every existing pipeline — movement,
   combat, fog, serialization, pieces, diorama — through the SHARED
   executor. Sovereign behavior is expressed as a small set of guards at
   single-source seams, keyed on a property, never on the name "Napoleon."
3. **Marshals compete NEAR him, never AGAINST him.** He accrues no glory,
   holds no ladder rank, wears no crown, expects no reward. The court's
   competition is for his favor, and his presence reshapes it (the Shadow,
   the discipline dampening) without ever entering it.
4. **Presence is the resource.** Every buff he grants is location-gated.
   Nothing about him is global except what was already global (authority).
5. **Zero new serialized fields.** `is_sovereign` derives from the
   personality string (already serialized); capture rides `captured_by`;
   the aura is a registered combat transient; the seat is derived from
   `location`. If a slice needs a new serialized field, it escalates.
6. **GR6 intact.** The LLM still only parses. Every sovereign mechanic is
   deterministic.

**Never-do pins** (each becomes a test):
- Napoleon never appears in the glory ladder payload, never `glory_crowned`,
  never `jealous_of` anyone, never the target of `find_jealousy_target`.
- `get_expectation(Napoleon) == 0` forever; the Reward chip renders his
  refusal copy, never options; he never appears in Unmet Marshals.
- No objection/defiance/clarification popup ever carries his name as
  speaker; `pick_marshal_voice` returns `""` for him.
- His trust never moves (`modify_trust` no-ops for a sovereign) and he can
  never go `autonomous`.
- He never enters `marshal_pool`, is never commissionable, never dismissed.
- The legacy fixture world and the tutorial contain no sovereign and are
  byte-identical by construction (all sovereign behavior gates on the
  personality, which no legacy/tutorial marshal carries).
- A scenario with zero sovereigns behaves byte-identically to today
  (mechanism is content-gated — the whole system is dormant without an
  authored sovereign).

## §3 The object — authoring Napoleon into 1805

### §3.1 The fourth personality: `sovereign`

`IMPLEMENTED_PERSONALITIES` grows to four (`personality.py:92`), validator
`VALID_PERSONALITIES` follows (`validator.py:77`). **This consciously
re-opens the MC-4 personality guard** (`test_marshal_content_mc4_personality_guard.py:57-61`
— its named re-open owners were "the Jealousy gate / MC exit review"; this
gate is the successor of record). Why a personality rather than a bool flag:

- The objection dispatcher (`objection_v2.py:1254-1258`) and the jealousy
  subject loop (`jealousy.py:2798-2806`) are keyed on the three personality
  strings — an unknown personality already evaluates to NONE / is already
  excluded. The personality IS the single source the guards want.
- It honors the standing rule that personality = character
  ([feedback memory]): Napoleon's character in this game's terms is not
  "aggressive subordinate" — it is "the man who gives the orders."
- `Marshal.is_sovereign` becomes a derived property
  (`self.personality == "sovereign"`), so **zero new serialized fields**.

The NP-0 build includes a mandated sweep: every `personality ==` / `in`
branch in the backend is audited for an else-assumes-literal (or
else-assumes-cautious) arm, and the sovereign's path through each is
pinned.

> ⚠ **Narrowed by the promise audit (Aug 15, 2026).** What landed is
> *chokepoint guards* (objection_v2 / jealousy / dotation / marshal_voice /
> enemy_voice / the `SovereignTrust` object freeze / the `enemy_ai` alias /
> delegation-ASK) plus the five hand-named sites below — a real survey, but
> not a census, and no artifact of it was committed. The audit ran the
> mechanical scan the sentence promises (160 personality-comparison sites)
> and found ONE with a live consequence: `strategic.py`'s HOLD ladder,
> where a sovereign fell into the arm labelled `else:  # aggressive` and
> **sallied out unordered** — fixed, with its own arm and a control pin
> (§15.9). Anyone re-opening this row should treat "every branch is
> pinned" as the aspiration and the chokepoints as the mechanism. Known sites from the survey: `get_attack_modifier_for_personality`
(must return 1.0 for sovereign), `get_effective_ai_personality` (sovereign
→ plays as `aggressive` if France is ever AI-driven; one line, GR5,
content-inert while France is the player), CR-5 delegation table (no
sovereign row → delegation to Napoleon resolves to the ASK arm, pinned),
`is_reckless_cavalry` (false — not cavalry), arrival personality term
(sovereign +0, like literal).

### §3.2 The authored entry (europe_1805.json)

```json
"Napoleon": {
    "name": "Napoleon",
    "nation": "France",
    "location": "Paris",
    "strength": 10000,
    "personality": "sovereign",
    "skills": { "tactical": 10, "shock": 7, "defense": 7,
                "logistics": 8, "administration": 9, "command": 10 },
    "tactical_skill": 10,
    "trust": { "value": 100 },
    "morale": 85,
    "ability": {
        "name": "The Presence",
        "description": "His presence on the field was worth forty thousand men - Wellington",
        "trigger": "when_present_in_battle",
        "effect": "Every French corps fighting in the Emperor's province gains +10% attack and defense. Enemy commanders will not attack his army at odds they would accept against any marshal."
    },
    "biography": "Emperor of the French. The Grande Armee is his instrument; the Empire is his estate; the marshals shine only in his light - or out of it.",
    "relationships": { "Lannes": 1, "Davout": 1, "Murat": 1, "Bernadotte": -2 }
}
```

**Authored AFTER Massena** (last in the `marshals` dict) — M7's harness
roster is `_france_standing(world)[:4]` in dict insertion order
(`test_combat_sweep_metrics.py:534`), so appending preserves Ney/Davout/
Soult/Lannes and M7's scripted battles are untouched (§12.3).

- **Stats**: the game's only two 10s (tactical, command — the Rally fast
  tier and the best battlefield mind), administration 9 (the Code; Intendance
  thrifty tier + Steward-exempt), shock/defense deliberately mortal (he is
  not a saber arm). The MC-2 balance-frame tests read `BLESSED_TABLE`, not
  the world — the sovereign is **exempted from the frame, not averaged into
  it** (§12.2): the frame exists to balance the competitive roster, and the
  sovereign is deliberately above it.
- **Trust 100, fixed** — `modify_trust` no-ops for a sovereign; the French
  trust-mean-70.0 pin keeps reading the 7 marshals.
- **Relationships** (Q6): four authored edges inside the existing −2..+2
  band — Lannes the friend, Davout and Murat trusted (the brother-in-law,
  complicated but bound), **Bernadotte −2** (the man who never forgave him
  and will refuse to reinforce him — Wagram, by machinery: the A-D4
  hostile no-show now applies to the Emperor himself, which is spicy,
  historical, and already priced by existing systems). No edge boots at +2
  (the no-pair-boots-Devoted pin holds); runtime drift via the Win/Loss
  formula can still take Lannes to +2 by shared victories — earned, not
  authored. Marshals with no authored edge start at 0 and drift.
- **The Guard is carved, not added: Soult 40,000 → 30,000, Napoleon 10,000.**
  France's national total stays exactly 189,000, and because the carve is a
  multiple of 1,000, per-marshal upkeep floor-division keeps `base_upkeep`
  byte-identical — E1 absorption (0.555), the ES-3/EC-U3 surcharge pins,
  the levy pins and the exposure pin all survive untouched (§12.1).
  Historically clean: the Guard was constituted from the army, not beside
  it, and IV Corps was the largest formation on the Rhine.
- **Paris is the boot slot** — the only clean one: Rhineland and
  Franche-Comte both already run over supply capacity with 2 marshals, and
  a third fires the death-ball stacking arm and breaks the
  `supply events == 1` (Mack-only) pin. Paris (cap 50,000 ×1.5 home,
  currently empty) absorbs the Guard with zero events. It is also the
  correct OPENING move of the campaign: the Emperor is at the Tuileries,
  and the first Napoleon decision the player makes is when to leave the
  Seat (§8) and ride to the front.
- **Portrait**: a PD Napoleon portrait (Gérard's 1805 coronation-era or
  David) ships at `assets/portraits/Napoleon.jpg` with a
  THIRD_PARTY_LICENSES row — required, because the portrait-coverage test
  reds on any roster name without one, and the Emperor is the last marshal
  who should wear the monogram fallback.
- The tutorial scenario is untouched (no sovereign; optional-key tolerance
  confirmed). The legacy fixture world is untouched (N1).

## §4 The Hand — commanding yourself

The fantasy: orders to Napoleon are the player's own will, so they are
frictionless and they accept first-person phrasing.

### §4.1 Address forms

A normalization pass at the top of `CommandParser.parse` (upstream of the
mock roster scan, `ADDRESS_TOKEN_RE`, fuzzy matching, and
`detect_strategic_command`, so all four agree by construction — the CR-4
precedent of rewriting the raw string) resolves, **only when a sovereign
exists in the player roster**:

- `"Napoleon, ..."` — works today the moment he is in the roster (CR-0
  derives commandable names live); nothing to build.
- `"(the) Emperor, ..."` / `"the Emperor <verb>..."` → `Napoleon` — today
  this hard-errors `Marshal 'Emperor' not found`.
- Leading first person — `"I will march to Ulm"`, `"I attack Vienna"` →
  `Napoleon <verb>...`, **gated three ways**: (a) no other addressee in the
  sentence (corpus row 3953 `"Ney, I want you to move to Lorraine"` is
  pinned unchanged — an address token always wins); (b) military/movement
  verbs only — diplomacy keeps its verbs, and the survey confirmed the
  corpus has zero "I offer/I propose" diplomatic forms to collide with;
  **the authoritative list is `parser._SOVEREIGN_ORDER_VERBS`, and every
  member of it must PARSE** — `ride` and `advance` were named here in
  v0.2 and neither is a verb this game has, so both were retired (§15.8
  item 4), as were `take`/`besiege` when measured. `test_every_sovereign_
  order_verb_actually_parses` is the standing guard, and **gate (b) binds
  all three arms** — the Emperor-lead arm shipped with no verb gate
  (§15.8 item 3) and the self-marker arm shipped with none either
  (§15.9 A4);
  (c) the question detector runs FIRST, so "Can I attack Vienna?" stays
  `help` (the `is_question` interrogative-lead + first-person second-signal
  contract is pinned in both directions).
- `"... myself"` / `"... in person"` as a trailing marker ("march to Ulm
  myself") → addressed to Napoleon. **"myself" also enters the parser skip
  lists and `_NON_TARGET_WORDS`** — the survey found it is currently
  eligible for phantom-province fuzzy matching (the PARSE-NEG family), a
  latent defect this slice closes regardless of the gate.

Golden-corpus rows land with it (new-action checklist step 12). Mock-parser
keywords and few-shots are deliberately NOT needed and did not land: the
rewrite runs UPSTREAM of both parsers, so neither ever sees an
un-normalized sovereign address (recorded deviation, NP-1 commit; the
original wording promised work that would have been dead by construction): at minimum `napoleon-address`,
`emperor-address`, `first-person-march`, `first-person-attack`,
`myself-suffix`, `i-question-still-help`, `addressed-i-want-unchanged`,
plus `mock_only`/`live_only` arms as CR-1 requires.

CR-4 carryover: first-person pronouns ("I", "me") get a sibling regex
beside `_PERSON_PRONOUN_RE`/`_PLACE_DEIXIS_RE` resolving to the sovereign,
with the same anchor discipline that file exists to enforce (subject
position, not object position — its own anchor rule). "him/her/them" never
resolve TO Napoleon (he is never "him" to the player).

### §4.2 No friction

One predicate, four guards (the survey's exact sites):

1. `should_check_objection` (executor.py:834-845) — AND `not is_sovereign`.
   Kills tactical objections; defiance dies transitively (only reachable
   via `handle_objection_response`).
2. Strategic `should_check` (strategic_executor.py:835-842, beside the
   existing enemy-nation bypass) — kills strategic objections + defiance.
3. The literal-clarification gate (executor.py:1521) — moot by personality
   but guarded for belt.
4. The `form_square` universal MILD (objection_v2.py:1279-1293 — fires
   BEFORE personality dispatch) — guarded, so the Emperor never grumbles at
   his own order.

Everything else is already structurally silent for an unknown personality:
`evaluate_situation` → NONE, the vindication tracker is objection-driven
(never populated), `marshal_voice` gets an explicit `is_sovereign → ""`
guard before its cautious fallback. The friendly-fire hard refusal
(executor.py:1177) deliberately REMAINS — it is a rule of the game, not a
subordinate's opinion.

**AP:** Napoleon's own strategic orders cost **1 AP** (the literal discount
seam, both sites — executor.py:724-730 pre-check and
strategic_executor.py:1458-1460 charge — gain `or is_sovereign`). The
Emperor does not persuade himself. Tactical costs unchanged. No AP change
for OTHER marshals near him in v1 (the Courier Delay row owns command-range
economics; §15D).

## §5 The Presence — combat and fear

### §5.1 The aura (both sides of the line know where he is)

New combat transient `sovereign_presence` (the spec's draft name
`sovereign_presence_bonus` was never the shipped one — corrected by the
promise audit; the code has used the short form since NP-2), registered in
`Marshal.COORDINATION_TRANSIENT_FIELDS` (so the two clear paths cannot
drift — the CA8-19(i) lesson is written at that constant):

- **SET** inside `_calculate_coordination_context` (combat_executor.py:494),
  in the same eligible loop that stamps coordination bonuses — "same
  province, same nation, alive, not broken/retreated" is already exactly
  the aura's audience, the battle lead included, and both sides compute
  independently at the two call sites, so an enemy-authored sovereign works
  identically (GR5 by construction). Predicate: any `is_sovereign` marshal
  in the eligible set (himself included — Napoleon fighting alone still
  carries his own presence).
- **READ** in `get_attack_modifier` / `get_defense_modifier` as its own
  multiplicative factor beside the coordination reads (marshal.py:1118 /
  :1210), `getattr`-guarded, **non-consuming** (a presence, not a one-shot).
  Deliberately NOT folded into `total_coordination_*` — those are capped at
  +25%/+20% and a well-coordinated stack would eat the aura invisibly. The
  defense global cap 1.75 still binds above everything (accepted: in a
  maximal fortified+coordinated stack the aura partially saturates — the
  cap is the older rule and wins).
- Values: `SOVEREIGN_PRESENCE_ATTACK = 0.10`, `SOVEREIGN_PRESENCE_DEFENSE
  = 0.10` (N1/N2, in-band tunable). Reinforcers arriving into his province
  are stamped by the same pass; the committed-strength RESOLVER prices it
  automatically through `get_attack_modifier(1.0, consume=False)`; the
  player-facing odds previews do NOT — corrected by the promise audit,
  which found the original wording claimed a coverage the previews never
  had.
- **Shown = applied**: a battle-report modifier row ("The Emperor commands
  in person — +10%"), a muster-preview note, and the diorama verdict names
  it when he is on the field. His locket rides the existing crowned-star
  discipline but with its own mark (§9).

### §5.2 The fear (the Trachenberg Plan, seventeen years early)

The enemy AI avoids battle where the Emperor stands. One seam, the exact
five-line pattern the overwatch term already uses inside
`_evaluate_target_ratio` (enemy_ai.py:2219-2307): if the target's stack
(indexed same-region scan) contains a sovereign, `effective_ratio ×=
SOVEREIGN_FEAR_FACTOR = 0.75` (N3), with a `bonuses_applied` string so the
AI's reasoning stays legible. Property-keyed → a French AI corps fears an
enemy sovereign identically (GR5). Covers P4 and P3.25 — the personality
ratio gates (aggressive 0.7 / cautious 1.3 / literal 1.0) then do the rest:
a cautious Austrian needs ~1.73× against the Emperor's army; even an
aggressive one wants near-parity. P0 (already-engaged) deliberately
untouched in v1 — a battle already joined is not re-litigated by fear.

The player-facing read: enemies mass NEAR him and strike where he is NOT —
which is the Trachenberg doctrine, and it teaches the player that the
Presence protects one province while exposing seven.

### §5.3 Discipline under the Emperor's eye

The jealousy threshold function gains a presence term mirroring the
authority-softening idiom it already carries (`_threshold_for`,
jealousy.py:531-559): a marshal **co-located with the sovereign** gets `base
+= 1` on his grievance threshold — professionals hold their tongues at
headquarters — with the DR-3 exemption intact (a hair-trigger Rival/Hostile
base-1 pair is NOT calmed; Bernadotte seethes in the Emperor's own tent).
Zero new state: co-location is read from the same pass that already builds
per-nation marshal maps.

### §5.4 The Emperor's prestige rides his own battles

At the existing combat authority site (combat_executor.py:2285-2306): a
battle where the sovereign personally commanded (battle lead) adds
`+2` authority on victory and `−5` on defeat (N4/N5), alongside the
existing outnumbered/capital arms. Austerlitz builds the throne; a lost
battle under his own hand shakes it — and because authority already feeds
defiance floors, trust-gain rates, vassal drift and jealousy acceleration,
the consequence cascades through four systems for free.

## §6 The Court — glory in his light, and out of it

### §6.1 Structural exemptions (the survey's single-point cut-set)

| Concern | Single seam |
|---|---|
| Glory never accrues | `_append_glory` (jealousy.py:190) |
| Never on the ladder / never crowned | `get_nation_ladder` (jealousy.py:323-327) — crown falls out free |
| Never an envy target | `find_jealousy_target` candidate filter (jealousy.py:372-382) |
| Never a jealous subject | personality dispatch already excludes; restlessness loop belt (jealousy.py:2858) |
| Expectation forever 0 | `get_expectation` (dotation.py:152-155) — shortfall/erosion/Unmet/Fontainebleau/war-weary/AI-rung all cascade from this one return |
| Endow/rente refused in character | `_execute_grant_dotation` guard site (economy_executor.py:1035) + pension sibling — *"The Empire is my estate."* |
| Erosion loop belt | the `captured_by` freeze pattern (world_state.py:5557) |
| No voice | `pick_marshal_voice` head guard (marshal_voice.py:361) |
| Trust frozen / never autonomous | `modify_trust` no-op + autonomy gate |
| Never benched | recruitment is one-way into `world.marshals`; `_standing_count` counts him (correct — he IS a standing marshal for the AI-cap predicate) |

### §6.2 The Shadow (Q4) — glory ×0.5 under the Emperor's eye

In `record_battle_glory`: when a sovereign is among a side's participants,
every non-sovereign marshal on that side accrues `floor(points ×
GLORY_SHADOW_MULT)` with `GLORY_SHADOW_MULT = 0.5` (N6). One site, both
polarities (shadowed defeats also bite half — serving under him shields
reputation in both directions, which is the honest reading of Auerstedt vs
Jena: Davout's glory was possible only because the Emperor was NOT there).

This is the court's engine: a marshal at the Emperor's side is safe, buffed
(§5.1), disciplined (§5.3) — and dim. The ambitious man wants a detached
command. The player now faces the real Napoleonic staffing problem: keep
Ney under your eye and he stays loyal and lightless; give him Bavaria and
he wins YOUR war while building HIS legend (and the existing jealousy
ladder prices the legend). No new state; the ladder, envy triggers,
petitions and crown all read the glory that the shadow shaped.

### §6.3 The Petition for Independent Command

A fifth petition kind on the existing single channel (the survey documented
the exact contract: builder → `_push_petition` → `handle_petition_response`
elif arm → `KIND_TITLES` row; no new PopupQueue slot): a marshal who has
spent `SHADOW_PETITION_TURNS = 4` (N7) consecutive turns co-located with
the sovereign, with glory below the ladder median and skills worth using
(tactical or shock ≥ 7), petitions: *"Sire — give me a command of my own."*
Arms: **Detach him** (free — counsel names a frontier province; it's advice,
the player still issues the order), **He stays with me** (his shadow
continues; the existing grievance machinery may pick it up), **Promise him
the next campaign** (1 AP, mirror of the confrontation Promise arm).
Latched per marshal via the existing `jealousy_confrontations_seen` key
idiom (`shadow@<name>`), jealousy-dormancy (tutorial) respected, narration
cap respected. Zero new serialized fields.

### §6.4 Relationships live

He participates in the Win/Loss relationship formula as a normal name —
shared victories genuinely warm marshals to the Emperor (runtime drift can
carry Lannes to Devoted +2, which then prices his ×1.50 coordination WITH
Napoleon through the existing table), and the A-D4 hostile no-show applies:
**Bernadotte at −2 will decline to reinforce the Emperor himself** unless
explicitly SUPPORT-ordered. That is Wagram, by machinery, and the existing
failure-attribution copy already names it. His own arrival rolls (when HE
reinforces a marshal's battle — "the Emperor rides to the guns") use his
logistics 8 and the relationship edge, unchanged.

### §6.5 Surfaces

- **Generals screen**: Napoleon renders ABOVE the ladder as a fixed apex
  block — "THE EMPEROR" header, his character sheet, no glory bar, no rank,
  no envy arrow (the ladder header itself continues to gate on the
  competitive roster only). His card: ability block wired
  (`_WIRED_ABILITY_MARSHALS` + name), no GLORY & GRIEVANCES, no Reward
  chip — instead one disabled-chip line in the house idiom: *"The Empire
  is his estate."*
- **Marshal card payload** (`marshal_overview`): sovereign variant flag so
  the .gd renders the apex treatment; skill notes/rally/admin tiers derive
  as normal (he IS thrifty-Intendance and fast-Rally — shown = applied).
- Dispatch/battle reports name him "the Emperor" via existing copy
  conventions; the campaign log chronicles him in third person (its
  standing rule — it "never addresses the Emperor" — now reads as style,
  not accident).

## §7 The Peril — the Eagle in Chains (Q2 — RULED capture-only, with the historical refinement below)

**The historical frame (the user's gate question, answered — it reshapes
two mechanics).** No reigning sovereign was taken in battle in this period,
and not for lack of trying: the Prussians hunted Napoleon personally after
Waterloo, and Cossacks came close enough at Maloyaroslavets in 1812 that he
carried poison ever after. Sovereigns escaped because escape was somebody's
whole job — the Guard's service squadrons existed to cut him out, and the
Old Guard's last squares at Waterloo died covering exactly that. When
capture DID happen to kings in the field (Francis I at Pavia 1525, John II
at Poitiers 1356) the result was never a prisoner exchange — it was the
war's checkmate: Madrid and Brétigny were peaces priced at provinces and
years of royal revenue, signed from a cell. And for THIS regime the stakes
were sharper still, because the Empire was one man: the Malet coup of 1812
nearly took Paris in a morning on a mere rumor of his death, and in 1814
the marshals answered his fall by making peace within days. So: they would
always try; he would almost always get out, over the Guard's bodies; and
if truly taken, France doesn't fight on for him — it BUYS him back, at
whatever the captor names, or the regime itself starts to slide.

**The mechanical translation:** capture must be RARE and always a story of
encirclement (an Ulm done to you), never a bad dice roll; the Guard is the
escape mechanism and pays for it in blood; and captivity's real weight is
peace LEVERAGE, not a debuff bar.

The existing fate machinery already does most of this: `_check_marshal_fate`
(strength < 5,000 or encircled → escape/capture), `_capture_marshal`
(captor's capital, strength 0), `release_captured_marshal` (ransom return
at 5,000), `release_mutual_prisoners` at every road to peace, the
`prisoner_return` treaty clause with valuation. Sovereign policy on top:

0. **The Guard covers the Emperor's escape.** In the sovereign's fate
   check, the low-strength/desperation arms never roll the 60% coin: he
   ESCAPES, and the extraction burns `GUARD_ESCAPE_TOLL = 30%` (N15) of
   his corps' remaining strength — the squares die so the berline gets
   out, and the battle report says so (*"The Guard bought the road with
   its own ranks."*). Only **true encirclement** (no safe retreat
   destination at all — the existing pure-encirclement arm) takes him,
   and the last-stand interrupt still offers the fight first. Capture is
   therefore always legible as an operational failure the player authored:
   he was surrounded.

1. **He can be taken; in v1 he cannot die.** A sovereign reaching the hard
   death seams (post-battle strength-0 pops ×4 sites, coordinated-participant
   pops, the attrition sweep) is CAPTURED instead of removed, through one
   new helper `sovereign_death_guard(marshal, world, captor)` called at
   those sites (the survey's pop-site census is the checklist). The
   last-stand interrupt fires for him with its own copy (*"The Guard dies —
   it does not surrender." Fight to the last / Cut our way out*) — and the
   existing last-stand resolution (damage the enemy, then the survivors are
   taken) is already the right story. No unattributable death: if no live
   captor exists (pure attrition), the strongest at-war border nation takes
   him. Death — the Réunion cannonball — is explicitly OUT of v1 with the
   Victory Pass named as owner (final defeat belongs to the row that owns
   endings; the game currently cannot end at all).
2. **The consequences are one number plus one component, and the rest
   cascades.** On capture: `authority −40` (N8) — which by EXISTING
   derivations accelerates jealousy (authority < 30 → hair-trigger
   thresholds), drops defiance floors, craters imperial grip → vassal
   drift/rebellion pressure (VS-R), and blunts courting. Plus a sparse
   war-score component **"The Captive Eagle" ±15** (N9) on the PT-J2
   ledger for the holding court (the HC-1 blockade-component idiom exactly
   — sparse third key, shown on the war-detail popup). The dispatch leads
   with it (a new headline class at crisis weight), the Gazette prints a
   special edition (§9).
   **Captivity is peace leverage, not a status effect (the Brétigny
   rule):** while the sovereign is held, the holder's AI settlement asks
   price the prisoner in — its `generate_suggested_terms` output leads
   with a `prisoner_return` clause at the sovereign valuation (N10), and
   the war-score component means every acceptance formula already reads
   the captivity. The intended play pattern is historical: France beaten
   badly enough to lose the Emperor makes the captor's peace, pays the
   ransom as treaty terms, and lives with what that cost — the fastest
   road home is the negotiating table, not a rescue column.
3. **Three roads home**, all existing machinery: any peace with the holder
   (mutual release — already fires at the `set_diplomatic_state`
   chokepoint); a `prisoner_return` clause priced at sovereign valuation
   `SOVEREIGN_RANSOM = 5000g` base (N10) instead of the marshal's 500–800;
   or military rescue — take the capital where he is held (capital capture
   already relocates/frees by the existing capture-cleanup path; verified
   at build, pinned either way). He returns at Guard strength 5,000, morale
   50, and authority does NOT snap back — the wound heals at the
   tracker's own pace. Recapturing the narrative is the player's problem.
4. **While he is held**: the Seat bonus (§8) is dead, the aura is dead
   (location-gated things die of themselves — he stands in an enemy
   capital), his AP-free... nothing special: a captured marshal already
   can't act. The petition channel may fire ordinary grievances into the
   vacuum — correct: the court frays without him.

## §8 The Seat of Empire (Q5)

While the sovereign stands in his nation's CAPITAL province (derived,
per-turn, zero state): **+1 DP on the diplomatic-points accrual tick**
(N11) — the Emperor receives the ambassadors himself. That is the whole v1
mechanic: one derived bonus, one ledger line ("The Emperor is at the
Tuileries — the courts attend him"), one dispatch note when he leaves it
the first time each war ("The Emperor has taken the field — Talleyrand
holds the portfolio").

Why so small: the field half of the tradeoff needs no mechanic — §5 IS the
field bonus — so the Seat only needs to make Paris worth something. DP is
the correct currency (diplomacy is the Seat's business), it is scarce
(France boots at 5), and it creates the campaign rhythm: winter in Paris
banking DP and receiving envoys, spring on the Rhine spending the army.
Intrigue-while-absent (Talleyrand–Fouché 1809) is deliberately deferred
with an owner (§15D, NP-D2) — it needs the Events machinery this game
doesn't have yet.

## §9 The Stage

- **The Emperor's piece** (Q7): a fourth map arm `emperor` — the survey
  sized it exactly: one `build_emperor` function in the proven deterministic
  generator (`tools/gen_war_table_pieces.py`), 8 PNGs (bicorne figure, hand
  in coat, on the round base), `VALID_ARMS` + the two backend arm
  derivations gain an `is_sovereign` branch FIRST (never `cavalry=True` —
  the survey showed that flag silently drags recklessness, charge
  mechanics, and combined-arms type counts), UI-foundation pins re-blessed
  consciously. The diorama inherits the figure free through
  `WarTablePiece.layer_texture`. Fog: the arm rides the base dict at FULL
  visibility like every marshal — the enemy SEES where the Emperor stands,
  which is §5.2's premise and history's (his headquarters' location was
  Europe's most-reported fact).
- **Portrait**: `Napoleon.jpg` (PD, license row) — satisfies both probe
  implementations (card + locket).
- **Diorama**: his locket, his nameplate; when present, the verdict line
  acknowledges the register ("The Emperor watched this field...").
  Standards/topple/eagle-taken all inherited.
- **Gazette**: `marshal_captured` already routes to the army section; a
  sovereign-capture arm joins `_special_reason` (*"THE EMPEROR TAKEN"*),
  and the existing triumph lead ("the Emperor's genius shines upon the
  army") becomes literally true when he led the battle — one conditional
  variant line.
- **Copy alignment**: every surface that says "the Emperor" today keeps
  meaning the player — no collision, because the player and the piece are
  the same person. The one review rule: no NEW copy may have Napoleon
  address the player.

## §10 Symmetry and the AI (GR5)

**Mechanism is sovereign-neutral; shipped content is France-only.** Every
guard keys on `is_sovereign`, both combat sides compute independently, the
fear term reads the target's stack property, the AI-side personality alias
is defined — so a modder authoring `"personality": "sovereign"` on an
Austrian Kaiser gets the full kit (aura, fear, shadow over Austrian
marshals, capture severity) with zero code change. The Waterloo example mod
(which already authors a `Napoleon` marshal) is upgraded to the sovereign
personality as the modding reference.

**Enemy sovereigns (Q8 — RULED August 15, 2026, the user's middle path,
decision delegated and taken):** *"foreign heads can exist, but simpler —
they are just worth more to capture, and only the ones who commanded
armies need to exist on map."* Ruling:

- **No separate "Crowned Heads" gate.** Foreign heads are AUTHORED CONTENT
  on the same sovereign mechanism, restricted to monarchs who genuinely
  took the field: **Tsar Alexander** (Austerlitz — he overrode Kutuzov and
  forced the battle; authored with the Russian Imperial Guard, ~9,000,
  traveling with the main army) and optionally **Kaiser Francis** (present
  at Austerlitz, nominal command). Frederick William III (nominally in the
  field for the 1806 campaign) is listed as authorable content, not
  shipped. Nobody else exists on the map.
- **Their special-ness is primarily capture-worth, exactly as asked** —
  and that half is already automatic: the Captive Eagle war-score
  component, the sovereign ransom valuation, and the Gazette special all
  key on `is_sovereign`, both directions. Taking the Tsar at Austerlitz
  is worth ±15 war score and a princely ransom TO FRANCE with zero
  additional code.
- **The rest of the kit applies symmetrically because it is free and, on
  inspection, historically apt rather than a compromise**: the Shadow over
  Russian marshals = Kutuzov dimmed under the Tsar's eye, which IS
  Austerlitz; the fear term means French AI corps (and coalition AI vs
  each other) respect a sovereign's stack; the aura is the Tsar's presence
  the Russian Guard cheered. The avatar half (first-person address, the
  Seat, no-objection semantics) is player-nation-scoped by nature and
  never applies to them. AI alias: a sovereign under AI control plays
  `aggressive` (one line in `get_effective_ai_personality`) — which is the
  honest read of Alexander forcing battle against his own general's
  advice.
- **Slot: NP-6 "The Three Emperors," a small owned slice AFTER NP-V** (so
  the French kit is measured live first), strikeable at the user's word —
  see §13. Its landing owns the Alexander/Francis authoring, their
  portrait/piece assets, the relationship-web and roster-pin re-blesses
  for Russia/Austria, and a measured ambient pass (their presence moves
  the same baselines §12.3 names).

## §11 Blessed numbers (in-band tunable; structural changes re-escalate)

| # | Constant | Value | Note |
|---|---|---|---|
| N1 | `SOVEREIGN_PRESENCE_ATTACK` | +0.10 | own factor, outside coordination caps |
| N2 | `SOVEREIGN_PRESENCE_DEFENSE` | +0.10 | global 1.75 cap still binds |
| N3 | `SOVEREIGN_FEAR_FACTOR` | ×0.75 | on AI effective ratio, P4 + P3.25 |
| N4 | Emperor-led victory authority | +2 | at the existing combat authority site |
| N5 | Emperor-led defeat authority | −5 | same site |
| N6 | `GLORY_SHADOW_MULT` | ×0.5 (floor) | both polarities |
| N7 | `SHADOW_PETITION_TURNS` | 4 | consecutive co-located turns |
| N8 | Capture authority shock | −40 | cascades via existing derivations |
| N9 | "The Captive Eagle" war score | ±15 | sparse PT-J2 component (HC-1 idiom) |
| N10 | `SOVEREIGN_RANSOM` base | 5,000g | vs 500–800 marshal valuation |
| N11 | Seat DP bonus | +1/turn | capital-province derived |
| N12 | Napoleon skills | 10/7/7/8/9/10 | the game's only 10s |
| N13 | The Guard | 10,000 @ Paris, morale 85 | carved from Soult 40k→30k |
| N14 | Sovereign strategic-order AP | 1 | the literal-discount seam |
| N15 | `GUARD_ESCAPE_TOLL` | 30% of remaining corps | the escape's blood price (§7.0) |

## §12 Blast radius — conscious pin flips and the re-record plan

This section is the honest cost of authoring one more Frenchman. Everything
below is either **survives by construction**, **conscious re-bless**, or
**measure, don't assume** — no silent breakage.

### §12.1 Survives by construction (the strength-neutral carve)

National total exactly 189,000 and the carve a multiple of 1,000 ⇒
byte-identical: `test_economy_e1_band` (absorption 0.50–0.62),
`test_economy_es3_upkeep` exact pins (1512/236/882/1118), levy pins
(130,000 / 59,000 over), france_exposure standing 189,000, national-total
pins, Austria's +18 boot solvency, the Milan ≤50,000 pin (we carve Soult,
never Massena). The supply-event ==1 pin (Mack only) survives because Paris
is empty and under cap. Legacy fixture world and tutorial: untouched files,
untouched behavior. M1–M6: authored fixtures, no scenario contact.

### §12.2 Conscious re-bless (each listed in the landing record with its flip)

- `len(world.marshals) == 21` ×3 (`test_europe_1805_scenario`) → 22.
- `literals == ["Soult"]` / `aggressive == [...]` lists → sovereign
  excluded from those predicates or lists re-blessed.
- `personality in {aggressive,cautious,literal}` roster pin → set gains
  `sovereign`.
- MC-4 guard (`IMPLEMENTED_PERSONALITIES == {3}`) → {4}; the gate record
  §14 is the formal re-open this pin's comment demands.
- MC-2 `BLESSED_TABLE` set-equality vs world → sovereign-exempt filter
  (the frame stays 21 competitive rows; means/peaks read the table and are
  untouched — deliberate: the sovereign sits above the balance frame).
- MC-3 pins: 26 directed edges → 34 (4 Napoleon pairs), French-web
  9/7/2 → 13 pairs, symmetry/range/no-boot-Devoted all still hold on the
  authored values; `UNAUTHORED` empty-web set updated.
- `FRENCH_1805` parser-roster parametrization → 8 names.
- Portrait coverage test → `Napoleon.jpg` ships (never the exempt list).
- `_WIRED_ABILITY_MARSHALS` + MC1 unauthored-list → Napoleon added.
- UI-foundation piece pins (arm lists, 32→40 sprites) → re-blessed with
  the emperor arm.
- Historical-envelope `set(world.marshals) == set(historical.marshals)` →
  both sides gain him (variance never adds/removes marshals — unchanged
  invariant, new roster).

### §12.3 Measure, don't assume

- **`BASELINE_SERIES` WILL move** (quiet-France 40-turn ambient on the
  1805 boot: the enemy AI now sees a garrisoned-and-guarded Paris; Britain's
  Normandy walk toward the capital meets 10,000 Guards + the fear factor).
  The sanctioned procedure applies: **re-record ONCE**, with the standing
  flip-experiment attribution — each new lever (aura off, fear off,
  authoring absent) disabled in turn must reproduce the prior series
  byte-for-byte before the re-record lands. The fear factor and the aura
  ship behind module-level flags for exactly this experiment (the
  HOST_RULE_ACTIVE idiom).
- **M7** re-measured: roster `[:4]` is preserved by authoring order, but
  `process_turn` sees an 8th Frenchman; the ladder exclusion should keep
  the 1–8 band stable — asserted, not assumed.
- The ambient probe families (ai_intent ×18, naval ×9, map_slice8,
  hc4) rerun; divergences attributed the same way.
- A dedicated presence band test: a 2-marshal French stack with/without
  the sovereign, asserting the aura's exact delta and its independence
  from the coordination caps (the stacking-saturation edge pinned).

## §13 Slices

Build order NP-0 → NP-5, NP-V last; estimate **2–3 sessions** (0–2, then
3–5, V riding the last). Every slice: suite green, ruff clean, no `.gd`
slice lands without the XR-1 boot smoke; conscious flips dated in-file.

- **NP-0 The Sovereign Substrate** — 4th personality + `is_sovereign` +
  validator + the §6.1 exemption cut-set + the personality-branch audit
  sweep (§3.1) + the authored entry with carve/Paris/portrait + §12.2
  re-blesses. Tests: `test_napoleon_np0_substrate.py` (never-do pins as a
  both-sides regression gate, the dormancy pin: a sovereign-free scenario
  byte-identical).
- **NP-1 The Emperor's Hand** — address normalization + skip-list fixes
  ("myself") + carryover first-person + the four no-friction guards + the
  1-AP seam + corpus rows/mock keywords/few-shots. Tests:
  `test_napoleon_np1_hand.py` + corpus.
- **NP-2 The Presence** — aura transient (set/read/register/clear) + fear
  term + discipline dampening + authority arms + shown=applied surfaces
  (battle report row, muster note). Tests: `test_napoleon_np2_presence.py`
  incl. the band test and GR5 both-sides arms.
- **NP-3 The Court** — glory shadow + the Petition for Independent Command
  + Generals-screen apex + card variant + reward-refusal copy. First `.gd`
  slice → boot smoke. Tests: `test_napoleon_np3_court.py`.
- **NP-4 The Peril** — death-guard helper at the pop-site census +
  sovereign last-stand copy + authority shock + Captive Eagle component +
  ransom valuation + release-path verification (peace/clause/rescue) +
  dispatch headline + Gazette special. Tests: `test_napoleon_np4_peril.py`.
- **NP-5 The Stage & the Seat** — Seat DP bonus + ledger/dispatch lines +
  emperor piece arm (generator, sprites, backend derivation, re-pins) +
  diorama/locket/nameplate verification + Gazette arms + Waterloo example
  mod upgraded. Boot smoke. Tests: `test_napoleon_np5_stage.py`.
- **NP-V The Measured Pass** — §12.3 in full: flip-experiment
  BASELINE_SERIES re-record (once), M7 band, ambient families, a
  playtest-driver arm (Mode A seeded run commanding Napoleon: address
  forms, aura battle, a petition, the Seat), live client visual drive
  (piece, apex card, tooltips), evidence pack in `docs/audits/`.
- **NP-6 The Three Emperors** (post-NP-V; strikeable at the user's word —
  gate record §14.1 Q8) — author Alexander (+ Francis optional) per §10:
  scenario entries with the Russian/Austrian Guard corps, portraits +
  license rows, roster/web/count pin re-blesses for their nations, the AI
  alias line, and a measured ambient pass of its own (their baselines move
  too). Completion = the Tsar stands with the army the player meets at
  the Austerlitz-shaped moment, and capturing him is worth the throne's
  ransom.

## §14 THE GATE (recommended defaults marked ◆)

> **§14.1 GATE RECORD — August 15, 2026 (authoritative).** The four forks
> put to the user in chat, and the rulings:
>
> - **Q2 The Peril → (a) capture-only, RULED**, with the user's historical
>   question answered and folded in as §7's frame: capture only by true
>   encirclement, the Guard buys every other escape at `GUARD_ESCAPE_TOLL`
>   (N15), and captivity's weight is Brétigny-style peace leverage (the
>   holder's suggested terms lead with the sovereign ransom).
> - **Q4 The Shadow → (a) ×0.5 + the Petition for Independent Command,
>   RULED at the default.**
> - **Q5 The Seat → (a) +1 DP/turn in the capital, RULED at the default.**
> - **Q8 Crowned Heads → RULED as the user's middle path, decision
>   delegated and taken** (*"foreign heads can exist... simpler... worth
>   more to capture, only the ones that commanded armies need to exist on
>   map — make decision, you don't have to do it either"*): no separate
>   gate; capture-worth is the headline and is already automatic; field
>   monarchs only (Alexander, optionally Francis) as authored content in
>   the small owned slice **NP-6**, post-NP-V, strikeable. §10 carries the
>   full ruling.
> - **Q1/Q3/Q6/Q7/Q9 stand at ◆ defaults** — presented in the same
>   exchange, unobjected; treated as blessed unless amended before NP-0.
>
> Every N# remains in-band tunable after landing; structural changes
> re-escalate.

The questions as put (kept for provenance):

1. **The Hand.** ◆ (a) total obedience + first-person address + 1-AP
   strategic orders (§4 as specced) · (b) obedience but no first-person
   parsing (address him only as "Napoleon"/"the Emperor") · (c) he can
   raise soft advisories like a staff officer (NOT recommended — he is you).
2. **The Peril.** ◆ (a) capture-only v1: death converts to capture at
   every seam, authority −40, Captive Eagle ±15, ransom 5,000g, three
   release roads; final death/defeat stays with the Victory Pass · (b) he
   can also DIE (permanent, regency campaign continues — bigger, darker,
   needs succession copy) · (c) invulnerable v1 (fate seams skip him
   entirely; cheapest, but the wager-the-Empire fantasy dies with it).
3. **The Presence package.** ◆ (a) all three: aura +10/+10, fear ×0.75,
   discipline +1 threshold · (b) aura only (no AI change — cheaper, but
   the enemy walking into the Emperor at even odds reads wrong) · (c) aura
   + fear, no discipline term.
4. **The Shadow.** ◆ (a) glory ×0.5 under his eye, both polarities, plus
   the Petition for Independent Command · (b) softer ×0.75 · (c) no shadow
   (marshals glory normally beside him — simplest, but the court loses its
   central tension and stacking with the Emperor becomes strictly
   dominant).
5. **The Seat.** ◆ (a) +1 DP/turn while in his capital, one ledger line ·
   (b) also +1 stability/turn in the capital region (stronger pull home) ·
   (c) no Seat mechanic v1 (defer with NP-D2 owner; the field half still
   works, but leaving Paris costs nothing and the placement decision
   flattens).
6. **The web.** ◆ (a) author the four edges (Lannes/Davout/Murat +1,
   Bernadotte −2) — the A-D4 no-show can now happen TO the Emperor ·
   (b) no authored edges, drift-only (cheaper re-bless, colder boot).
7. **The piece.** ◆ (a) a fourth `emperor` map arm from the house
   generator, diorama inherits · (b) he renders as an infantry piece in v1
   and the arm ships later (owner: NP-5 completion definition stays open —
   NOT recommended; GR9 dislikes it).
8. **The Crowned Heads.** ◆ (a) defer enemy sovereigns to an owned
   follow-on gate (centerpiece: Austerlitz with both Emperors on the
   field), post-Victory-Pass; mechanism ships sovereign-neutral now ·
   (b) author Francis + Alexander in v1 (scope: AI sovereign movement/seat
   policy — roughly +1 session) · (c) never (close the door; NOT
   recommended — the machinery is free and Austerlitz wants it).
9. **The routing.** ◆ (a) NP runs after PC15, before position 10, and the
   owed played 20-turn campaign runs AFTER NP so it evaluates the Emperor
   (the HC-order precedent) · (b) campaign first, NP after (cleaner read of
   the pre-Napoleon balance, but the campaign's findings partly expire when
   NP reshapes the court).

## §15D Deferred with owners (GR9)

> Renumbered §15 → §15D by the promise audit (Aug 15, 2026): this section
> and the landing record below were BOTH numbered §15, so every
> cross-reference to "§15" was ambiguous. The landing record keeps §15.

| Item | Owner / landing | Completion definition |
|---|---|---|
| NP-D1 The Guard's own mechanic ("la Garde recule!" — commitment/elite morale floor) | Battle Gallery gate (owns the garrison-diorama rider already) or a post-Round-0 content slice | The Guard gets a named battle behavior beyond high boot morale, or the row is closed as "boot morale is the model" |
| NP-D2 Intrigue while the Emperor is absent (Talleyrand–Fouché 1809) | The post-EA Events System row (ROADMAP cut list) — re-opens only with it | Absence > N turns can fire an authored intrigue event chain |
| NP-D3 Courier/command-range economics | The existing ROADMAP Courier Delay row (`:1004/:1017`) — this spec builds the HQ anchor it assumes; the row stays planned, unchanged | Its own row's definition |
| NP-D4 ~~The Crowned Heads follow-on gate~~ **SUPERSEDED by the §14.1 Q8 ruling** — foreign field-monarchs are the owned slice **NP-6** (§13), no gate needed | NP-6 | NP-6's own completion definition |
| NP-D5 Sovereign presence feeding the AI-intent mirror (frontier massing read) | AI-intent backlog (spec §11 cut-list custodian) | The mirror's perceived-rung derivation gains a sovereign-at-frontier term, or closed as double-counting with §5.2 |
| NP-D6 "The Emperor reviews the Guard" morale verb | Closed unless Q-gate revives: drill already restores morale (+10/+15) and a second morale verb double-dips; revive only with a distinct cost/effect shape | N/A unless revived |
| NP-D7 Victory-Pass interlock ("The Emperor's Designs" reading his location/state) | Positions 12–13 own it; this spec only guarantees the piece exists and its state is queryable | Victory gate's own definition |

---

## §15 LANDING RECORD — August 15, 2026 (authoritative)

**ROW NP IS BUILD-COMPLETE THROUGH NP-V.** Eight commits on master,
`bb849b2`..HEAD. Suite **17,974 / 3 skipped**, ruff clean, Godot parse
harness EXIT=0, boot smoke 0 SCRIPT ERROR.

| Slice | Commit | What landed |
|---|---|---|
| NP-0 | `bb849b2` | the 4th personality + `is_sovereign` + the §6.1 exemption cut-set, DORMANT |
| NP-1 | `81c74ba` | address forms, no-friction guards, the 1-AP seam |
| NP-2 | `b426a2c` | the aura, the fear, discipline, prestige |
| NP-3 | `b1c08c3` | the Shadow, the Petition for Independent Command, the apex card |
| NP-4 | `24583a9` | the Eagle in Chains |
| NP-5 | `10f57ac` | the emperor piece, the Seat, the press |
| NP-A | `a806e55` | the authored entry + the ONE `BASELINE_SERIES` re-record |
| NP-V | (2) | the review pass and the design pass |

### §15.1 The deliberate deviation from §13

NP-0's authoring half was deferred into its own slice (**NP-A**) so
`BASELINE_SERIES` re-records exactly ONCE for the whole row — which is
what §12.3 mandates. Nothing was cut; the slice order otherwise stands.

### §15.2 The re-record, flip-attributed (§12.3 discharged)

Four arms. **Arm 0 — authoring ABSENT, both levers on — reproduces the
prior series BYTE-FOR-BYTE**, which measures the row's central claim
rather than asserting it: every NP mechanism is dormant on a
sovereign-free board. Arms 1/2/3 (authoring; +fear; full tree) are
IDENTICAL to each other, so the whole divergence (index 13) is the
AUTHORING — the Soult 40k→30k carve changing his corps' battles, plus a
22nd marshal in the per-turn loops. **Both behaviour levers are provably
inert on the ambient board, and that is reported rather than buried:** it
is an AI-vs-AI run in which the Emperor never leaves Paris and is never
attacked. M1–M7 byte-identical throughout, WITHOUT re-record.

### §15.3 The measured pass (NP-V)

A 30-agent find-then-refute fleet (10 lenses × 2 independent refuters), a
seeded acceptance drive, and a hand-measured design probe. **Three P1s,
six P2s and several P3s confirmed and FIXED in-session**; the headline
three are worth naming because all three were invisible to the row's own
181 passing tests:

* **The Presence evaporated exactly when the Emperor marched to the
  guns.** The aura was stamped only off the primary's OWN province, but
  attacker-side reinforcements relocate to the battle region first — so
  an arriving corps was in neither eligible set, and the Emperor joins
  ~95% of the time. The authored ability ("every French corps fighting in
  the Emperor's province") was false at the exact moment the battle WAS
  in his province. Both halves now key on the battle's own participant
  roster; the fix also closed the mirror case (a marshal who mustered
  beside him and marched away alone fought at +10% anyway).
* **The Shadow only ever fired on a same-province battle.** Glory runs
  after the victor advances, and `get_battle_participants` applies the
  A-D4 filter — so marshals sortied from headquarters with the full aura,
  the +1 discipline threshold AND full glory: the strictly-dominant
  stacking the gate rejected option (c) to avoid.
* **A captured sovereign was still commandable** through the first-person
  forms (the PC15-4 guard keys on a comma-address), and came home from
  captivity fortified in a stance he never chose.

### §15.4 THE DESIGN AMENDMENT — the aura of invincibility (user's brief)

Scored by the review at **6/10 "feels strong" and 4/10 "losses have
weight"**, corroborated by an independent probe. The aura is correctly
SIZED (~16 of the +27.6 points of win rate the Emperor brings a stack come
from the Presence, ~11 from his army) — **N1/N2 must not be raised.** The
defect was that the FEAR decayed with imperial grip and the AURA did not,
and the ramp began so late that six emperor-led defeats moved neither.

`authority.sovereign_aura_strength` is now the single source for both.
The combat stamp is a FRACTION, the modifiers scale by it, and the
battle-report row derives from the same product — so the player watches
"+10%" become "+9%" ("his star dims") become nothing. The window is
**AURA_GRIP_FULL 85 / AURA_GRIP_BROKEN 30** (in-band tunable): authority
boots at 100, so the old 70 meant the first six emperor-led defeats were
free; now the 4th is visible and the 14th ends the myth. And the battle
says it out loud — *"[The Emperor] He commanded in person, and the field
was lost. The court will hear of it. (Authority −5)"*, with *"Europe has
begun to notice that he can be beaten"* once the aura has cracked.

Recorded consequence: an enemy court's grip is the opaque flat 75, so an
authored foreign sovereign starts at ~82% of full dread rather than 100%.
NP-6 owns that.

### §15.5 Also caught: the assets were never committed

`assets/` is gitignored, so `Napoleon.jpg` and all eight `emperor_*.png`
existed only on the developer's disk, passed every on-disk test, and were
in NO commit — on a fresh clone (or the position-10 build) the Emperor
would have had **no portrait and no map piece**. Force-added with the
`.import` siblings an exported build needs, plus a structural pin that
asks GIT rather than the filesystem, because on-disk assertions cannot
catch this by construction.

### §15.6 Acceptance evidence

`docs/audits/NP_V_ACCEPTANCE_DRIVE_2026_08_15.md` — a seeded 10-turn
drive in which all four address forms work (`Napoleon, …` · `the Emperor,
…` · `I will march to Swabia` · `march to Bavaria myself`), the 1-AP
caption renders, and the dispatch reads **"the Emperor Napoleon holds the
field at Swabia"**. The run also surfaced a HARNESS limit, not an engine
defect: `MAX_ANSWERS_PER_POST` was 8 and the Emperor's stack now wins
hard enough to chain more decisions than that in one turn (raised to 16,
dated in-file).

### §15.7 Still open, with owners

*(Updated August 16, 2026 — the played campaign is DISCHARGED and NP-6 has
its gate memo. Records: `docs/audits/PLAYTEST_NAPOLEON_CAMPAIGN_2026_08_16.md`
and `docs/audits/NP6_THREE_EMPERORS_EVAL_2026_08_16.md`.)*

* ~~**The played 20-turn campaign** (Q9 ruling) runs after this row.~~
  ✅ **HELD August 16, 2026** — four arms, 68 turns, one on the live parser.
  **Every mechanical half of the row held under play and none of the promise
  audit's eighteen fixes regressed.** All seven "fixed but never played"
  checks taken: six PASS, one not reached (the cavalry charge refused for
  want of recklessness). Two findings land back on THIS spec: **§15.4's
  amendment is built, correct and invisible** — the aura fell +10% → +4%
  across 22 turns (grip 100 → 52) with no beat anywhere and no arm ever
  producing the dimming battle row (`DESIGN_REFINEMENT.md` NPC-D1) — and **a
  sovereign on a strategic order still inherits the *cautious* branch of the
  cannon-fire interrupt** (`strategic.py:2174` enumerates three
  personalities; NP-0 added a fourth), which is finding B4's exact §3.1
  class at a second seam (`BUG_FIXES.md` NPC-22).
* **NP-6 "The Three Emperors"** — still NOT started, still strikeable
  (§14.1 Q8). ✅ **Its gate memo now exists.** Four of the five kit halves
  work on an authored foreign sovereign today, for free, measured end to
  end (the aura on his own side, the fear at 0.7955 vs 1.0, the Shadow
  halving Kutuzov 3→1, the capture-worth, the Seat). The fifth is blocked
  on a **ruling**, not on work: §10's recorded consequence ("~82% of full
  dread") is confirmed and is worse in practice than it reads — his
  **first** battle prints *"(his star dims)"* at **+8%**. Also found:
  **`world.nation_authority` is already serialized and already written for
  a captured enemy sovereign (−40), and `get_imperial_grip` never reads
  it.** Recommendation (a), 1 session. **The user decides.**
* **A live visual sign-off** on the new surfaces: the emperor piece on the
  map, the apex card, the diorama locket cipher, the Captive Eagle row,
  the Tuileries ledger line. The standing convention is a user pass.
  **STAGED August 16, 2026** — `saves/np_visual_{seat,field,captive}.json`
  (gitignored, on the dev machine) reproduce all five between them, and the
  DATA behind each was verified over the wire so his pass is a look rather
  than a hunt. The pixels remain his.
* Review findings consciously NOT built, each with its reason recorded in
  the fleet report: the A-D4 pair keeps its own laurels (Napoleon
  refusing to march means they did not share a field — and it is the
  historically apt outcome for the marshal who built a legend outside the
  shadow); the skill-duplication observation (his 10s buy nothing over
  Soult's 9 / Davout's 9) is real and left to the MC balance frame; the
  casualty-laundering property of a small battle lead is PRE-EXISTING
  (CO-1/[S62]) and belongs to the combat-copy-unification backlog.

### §15.8 The finish pass — four things the landing record had left undone

Recorded because the user was right to ask. The row was reported
build-complete while four items the spec (or my own commit messages)
had promised were still missing. All four are now landed.

1. **The golden-corpus rows never landed.** §4.1 names seven by id, and
   the new-action checklist makes corpus coverage step 12 — and the NP-1
   commit message said in as many words that they would "land with the
   authoring slice". NP-A did not carry them, and nothing caught it
   because the corpus gate fails only on an ACTION with zero coverage,
   never on a missing phrasing. **Eight rows added** (the seven named,
   plus `emperor-lead-foreign-title-untouched` for the defect below);
   eval **524/524**.
2. **N13's blessed `morale: 85` was never authored** — the entry omitted
   the key, so the Guard booted at the 100 default. In the player's
   favour, which is why nothing complained. Now authored; the E1 / ES-3 /
   EC-U3 pins and `BASELINE_SERIES` are unmoved.
3. **The Emperor-lead arm required no verb.** `^the emperor\s+` rewrote
   ANY sentence opening that way into an order, so *"the Emperor of
   Austria demands Venetia"* became *"Napoleon, of Austria demands
   Venetia"* — a foreign sovereign's title turned into an order to ours —
   and *"the Emperor is displeased"* became an order too. It now gates on
   the same verb set as the first-person arm, and CONSUMES the modal the
   way that arm always did (*"the Emperor will march to X"* had been
   rewriting to *"Napoleon, will march to X"*, which the parser cannot
   act on).
4. **Four verbs in the rewrite set do not parse.** Measured at the
   endpoint: `ride` and `advance` shipped in the NP-1 list and neither is
   a verb this game has, so the rewrite bound the Emperor to an order the
   executor then refused — the advisory-diverges-from-executor shape the
   project keeps fighting. `take` and `besiege` failed the same way when
   added. All four retired; `test_every_sovereign_order_verb_actually_parses`
   is the standing guard, and it is what makes the rewrite's promise
   falsifiable.

⚠ **A spec error, not a code error:** §4.1's worked example *"the Emperor
will take Vienna"* uses `take`, which is not a verb this game has. The
example is wrong; the sentence does not and should not rewrite.

Left unfixed with reasons: the auto-bombardment "destroyed by
bombardment" line is a debug `print()`, not player-facing; the DP HUD can
read "6/5" while the Emperor holds the Seat (the accrual is correct and
the ceiling is cosmetic — routed rather than papered over); and
`sovereign_takes_field` can re-fire once per war instance rather than
once per war, which is latent and needs a played campaign to judge.

### §15.9 THE PROMISE AUDIT — the exit review (August 15, 2026)

**Record = `docs/audits/NP_PROMISE_AUDIT_2026_08_15.md` (authoritative).**
Commits `4638a85` + `55ec497` + the docs commit. Suite **18,032 / 3**.

§15.8 was written because the user asked whether the row was finished and
four forgotten promises fell out in ten minutes. This section is what
happened when that question was asked *systematically*: every commitment
in this spec and in all 13 NP commit messages extracted as a row and
verified against code at current line numbers — a promise that could not
be pointed at with `file:line` counted as MISSING until proven otherwise.
11 parallel extraction agents (one per promise surface) with an
independent refuter per non-LANDED row, run alongside a hand-verification
pass that was deliberately not told what the fleet was doing.

**The row is substantially as advertised** — every §2 never-do pin holds,
zero new serialized fields, no name-keyed guard (GR5), the Peril's three
roads home work end to end, the Petition fires end to end, all 19 rewrite
verbs parse, the assets are git-tracked.

**450 promises extracted, 297 LANDED, 60 non-LANDED rows put to
independent refuters (23 REFUTED, 22 downgraded, 15 confirmed/upgraded).
EIGHTEEN defects fixed, ELEVEN routed** — and the largest cluster shares
one root:

> §15.4's amendment made `sovereign_aura_strength` "the single source" for
> the aura and the fear — and updated two of its four readers. The
> **garrison assault**, the **cavalry charge** and the **muster preview**
> kept the old constant. Measured with the myth wholly broken
> (`sovereign_aura_strength == 0.0`) the Emperor still stormed a capital
> at the full +10% — attack modifier `1.2320` where the design intends
> `1.1200`. That is the split brain the amendment's own commit said it was
> retiring, surviving one seam over, inside the mechanic the user's brief
> was about.

The second theme is a **returned value three of four callers ignored**:
`destroy_marshal` returns False when it converts a sovereign to capture,
and only the charge copy read it — so the battle and auto-bombardment
copies announced that the Emperor had been **destroyed**. §15.8's note
that the auto-bombardment line "is a debug `print()`, not player-facing"
is true of `combat_executor.py:5166` and misses the player-facing sibling
seventy lines below it; the record is corrected rather than defended.
This slice's own structural pin then found a **fourth** copy on its first
run — the charge path, which had the gating right but composed its
sentence independently and so carried no captured-sovereign line at all.

**The three items §15.8 left unfixed were judged, not accepted.** Two were
cheaper to close than to carry (the DP ceiling, now single-sourced in
`diplomacy.displayed_dp_ceiling`; the departure beat, which `break`ed
after the first unnoted war and so repeated once per war instance). The
third's stated reason was half true, above.

**Pins corrected:** a THIRD surviving pin asserting a broken rewrite
(`"take the field in person"` → `"Napoleon, take the field"`, which parses
to `success=False`) — §15.8 item 4 said it found two of these; it found
two of three. And the enemy-sovereign stamp pin asserted `1.0` where
§15.4 had already recorded that a foreign court's flat-75 grip means
~0.82: it was pinning the inconsistency this audit closed.

**All eight golden-corpus rows were vacuous about the one thing they pin.**
They landed in §15.8 but every one omits the `marshal` key that 64 other
rows use — the only field distinguishing "the sovereign was addressed"
from "somebody was". Mutation-proven: with the theft simulated,
`addressed-i-want-unchanged` still PASSED.

**Corrections to this document:** §4.1's verb list still named `ride` and
`advance` (retired in §15.8 item 4) and now defers to
`parser._SOVEREIGN_ORDER_VERBS`; the deferral table was renumbered §15D
because it and this landing record were both "§15".

**Canonized rather than changed:** the reckless auto-charge fires the
Shadow without granting the aura, because that path clears every combat
transient on both sides. The rule is now written at the seam — the aura is
a transient buff and that path forgoes ALL of them (coordination too); the
Shadow is a fact about whose field it was. Suppressing it there would make
"charge beside the Emperor" the one way to bank FULL glory under his eye.

**Routed, not fixed — `BUG_FIXES.md` §Row NP (11 rows):** NP-X1 (the
marker still reaches the destination extraction in sovereign-FREE worlds →
CR-6) · NP-X2 (the general prisoner-rescue rule NP-4 said it routed, and
did not → EC-2 pass 2 / Victory) · NP-X3 (a war declared while he is
already afield still notes itself — ACCEPTED, pinned) · NP-X4 (the suite
can reach the live Anthropic API; pre-existing, non-hermetic → position
10) · NP-X5 (the §10 modding reference fails the validator; pre-existing,
verified byte-identical before this row → DEF-1) · NP-X6 (the card's "he
never asks" is half true in live mode → DEF-1) · NP-X7
(`marshal_honorific` claims "every surface", used at 3 of 49 → DEF-1) ·
NP-X8 (5 of 9 CR-4 SUPPORT anchors rewrite to something the parser cannot
act on → CR-6) · NP-X9 (the verb guard iterates stems, not inflections →
CR-6) · NP-X10 (a production-dead `game_state` fallback in the parser →
CR-6) · NP-X11 (a production-dead `sovereign` key on the last-stand
interrupt — ACCEPTED, pinned dead, re-open with NP-6).

The fleet's second wave took two more P1s, both reproduced at runtime:
the muster note's **predicate** (not just its number) scanned the
attacker's ORIGIN while the applied aura keys on the battle roster — so
the same screen printed *"WILL NOT — Napoleon: fortified"* two lines above
*"The Emperor commands in person — +10% harder"* — and the **glorious
charge** was the one glory-producing path without the NP-V roster
override, so a cavalryman charging out of the Emperor's headquarters
carried the Presence AND banked full glory (the strictly-dominant stacking
the gate rejected option (c) to avoid, and a written falsification of
§15.3's claim that the mirror case was closed). Then: the **Shadow was
switched off by a magnitude** (`_atk_presence > 0.0` — §15.4 changed the
aura's size, never said the Shadow lifts; introduced there and EXTENDED by
this audit's own part 1); the Emperor **sallied out when told to hold**,
through the `else: # aggressive` arm, in a battle nobody ordered; the
attrition sweep announced his **death**; the Petition's dispatch beat was
dropped at the whitelist so **the line NP-3 describes never existed**; the
prestige message was silent on two paths; and §6.1's named **autonomy
gate**, **restlessness belt** and pillar-1 petition guard had never been
written at all — each holding by cascade, which is the difference between
safe and safe on purpose.

`tests/test_napoleon_promise_audit_2026_08_15.py` (47) +
`test_napoleon_np1_hand.py` corpus class. `BASELINE_SERIES` and M1–M7
byte-identical throughout, run rather than assumed.

### §15.9a The two questions the exit review owed — BOTH RULED (user, Aug 15, 2026)

* **The sovereign's attack-confirm → NO CONFIRM. Ruled, and it is now the
  written rule rather than an accident of the CA9 row-2 gate keying on
  `cautious`.** He is the player's own hand (§2 pillar 1); a confirmation
  dialog on your own decision is exactly the friction NP-1 exists to
  remove, and the Peril (§7) is meant to be a wager made with open eyes.
  Nothing to build; recorded so a future reader does not "fix" it.
* **"The Interned Column" → CLOSED, not deferred.** `DESIGN_REFINEMENT.md`
  §PC15-D1 homed the rider to *"the row NP exit review"*, i.e. this
  session, and the review's own finding is what decided it: **PC15-D1's
  ruling substantially narrowed the premise.** The forced-retreat scan now
  obeys the movement law — measured live, it prints *"Skip: neutral court
  (PEACE) — the frontier is closed"* — so an army can no longer retreat
  ONTO neutral soil at all, and the case survives only for an army already
  standing there when cornered. Capitulation in place is the 1805-exact
  outcome (Ulm, Prenzlau, Ratekau), and a neutral holder would add a party
  with no other mechanics. GR9 is satisfied by CLOSURE: there is no
  remaining player-facing promise. Closure recorded at the §PC15-D1 row.

**Still open and NOT this session's:** NP-6 (strikeable at the user's
word) · the live visual sign-off on the emperor piece / apex card /
diorama locket cipher / Captive Eagle row / Tuileries line, which is the
user's own pass by standing convention · the played 20-turn campaign
(Q9 ruling).
