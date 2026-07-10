# Wave 6 — Fun-Factor Build Spec (v1.0)

> **GATE RECORD (July 10, 2026): the user APPROVED ALL Wave 6 items in full** — every expansion (EXP-N1..EXP-D1), every escalation (E-CA-1..6), all ten BUG-CA fixes, **plus two user additions scoped this same day: Dynamic Battle Naming (W6-2) and the Literal Doctrine hone (W6-5)**. The numbers in this spec are the **blessed defaults** — a build session may tune them inside the stated bands without a new gate; **structural** changes (new serialized state beyond what a slice lists, a new modal surface, a new clause type beyond `prisoner_return`) still escalate. On the Literal Doctrine the user's steer is load-bearing and quoted: *literal marshals do NOT need to object if that's not the best way — the fantasy is "generals who do what they're ordered."*
>
> **Mission.** Convert the §8 creative audit (`docs/audits/CREATIVE_AUDIT_2026_07_10.md`) into landed play value: **greatly raise the weak pillar scores** — war narration 3.5 → **≥7**, combat legibility 4.5 → **≥7**, incoming diplomacy 4 → **≥6.5**, marshal drama 6 → **≥7.5** — without regressing the strong pillars (command 7.5, outgoing diplomacy 8, aliveness 7.5).
>
> **Who builds this.** A fresh Fable-level session with no memory of the audit. Everything needed is in this file + the referenced anchors. Slices are ordered and commit-sized; take them **in order** unless a dependency note says otherwise; one slice (or one sub-part of W6-7) per commit, directly on `master`, through the pre-commit gate (`ruff check backend/` + full pytest; **never `--no-verify`**).

---

## 0. Session bootstrap (read this first, every session)

1. Read `CLAUDE.md` top-to-bottom (Golden Rules, file reference, add-an-action checklist, serialization enforcement). The rules that bite hardest in this wave: **GR2** (`int()` to Godot), **GR5** (AI uses the same executor — every mechanic here is symmetric), **GR6** (LLM never causes — everything in this spec is deterministic; no new LLM calls anywhere), **GR8** (no hot-path region scans), serialization parity for every new field.
2. Skim the audit memo `docs/audits/CREATIVE_AUDIT_2026_07_10.md` §1–§4 for the *why* behind each slice (evidence, live exhibits). Don't re-derive designs from it — **this spec supersedes the memo where they differ.**
3. Check `docs/STATUS.md` Next Steps for which W6 slices are already landed (strike-through discipline: every landed slice gets its row updated here AND in STATUS).
4. Verify commands (Windows venv — Unix form silently fails):
   `".venv\Scripts\python.exe" -m pytest tests/ -q --tb=no` · `ruff check backend/` · backend runs as `-m backend.main` on port 8005.
5. Live-probe discipline: slices marked **[LIVE-VERIFY]** must be curl-verified against a running backend before commit (the audit found its highest-priority bug only via live play). `.env` has `LLM_MODE=anthropic` + a key; plain keyword commands resolve via the fast parser without spending API calls.
6. After each slice: update the slice row here (✅ + date + commit SHA), the STATUS.md session entry, and any doc named in the slice's **Docs** line. New/changed player-visible behavior on the typed surface needs a golden-corpus entry when it adds a mock-reachable action (CR-1 checklist step 12).

**Score accounting.** After W6-4 lands and again after W6-10, run the memo's 5-turn outsider loop (delegate, objection, 2+ battles, retreat, endow, end-turns, one incoming + one outgoing diplomacy beat) and re-score the four target pillars in a short addendum to the memo. The wave is DONE when narration ≥7 and combat legibility ≥7 are *measured*, not assumed.

---

## 1. The slice queue (order + rationale)

| # | Slice | Pillar target | Size | Depends on |
|---|-------|---------------|------|-----------|
| W6-0 | ~~Correctness A — dialogue & typed-answer routing (BUG-CA-7/8/10/1)~~ **✅ LANDED July 10, 2026** — dialogue_id identity + stale guard, pending-question router, option enumeration, re-mount fidelity, log direction; `test_w6_dialogue_identity.py` (27); live-verified (guard + router + log line probed against the running 1805 boot) | trust in every later slice | S–M | — |
| W6-1 | ~~Correctness B — combat/report/movement/stats (BUG-CA-2+E-CA-2, 3, 4, 5, 6, 9)~~ **✅ LANDED July 10, 2026** — retreat doctrine (tier-5 at-war exclusion + homeward bias + named substitutions, GR5 AI mirror), endow asks-never-defaults, report remaining derived, outcome-honest reinforcement observations + label renames, dispatch recency-first dedup, reinforcement participation counts + serialized `last_battle_turn`; `test_w6_retreat_doctrine.py` (10) + `test_w6_correctness_b.py` (18); live-verified (report arithmetic + retreat substitution message) | combat legibility floor | M | — |
| W6-2 | ~~Dynamic Battle Naming *(user addition)*~~ **✅ LANDED July 10, 2026** — serialized `battle_counts` + `compose_battle_name` (ordinals to Twelfth then Nth; Great tier ≥80k replaces the ordinal); name stamped on the log event pre-write, the diplo battle record, the war HUD `recent_battles.name`, and the result/report; campaign one-liner leads with it; `test_w6_battle_naming.py` (14) | narration | S | — |
| W6-3 | ~~The Dispatch Rewrite — "Berthier tells the story" (EXP-N1)~~ **✅ LANDED July 10, 2026** — headline selection (weights table + prose templates + ≤2 sub-beats), danger flags (fog-legal), arc memory (hunted/defeats/fled chains, ≤3), vassal-loyalty `reason` at emission + dispatch rendering, headline-aware Berthier note, NO-INTEL frontier collapse, supply-attrition event-log mirror; Godot headline block + danger lines (dispatch_view + main); `test_w6_dispatch_rewrite.py` (29); live-verified (real Bernadotte mauling headline + hunted-by-Archduke-Charles arc + morale danger flag) | **narration 3.5→7** | M–L | W6-1 (stat fixes), W6-2 (names) |
| W6-4 | Muster preview + standing orders surfaced (EXP-C1 + E-CA-4) | **combat legibility 4.5→7** | M | W6-1 |
| W6-5 | The Literal Doctrine *(user addition — hone literal)* | marshal drama | M | W6-4 (muster rows) |
| W6-6 | Enemy marshals speak (EXP-M2) | marshal drama / aliveness | S | W6-2 |
| W6-7 | Marshal Fates — capture, ransom, last stand (EXP-M1) | **marshal drama 6→7.5** | L (2 commits) | W6-0, W6-1 |
| W6-8 | The Spoils of War — estate confiscation (EXP-E1) | economy/drama | S–M | — (rides ES-7 as landed) |
| W6-9 | "What does Europe intend?" — assessment verb (EXP-D1 + R132 + R117 + coalition posture) | diplomacy/aliveness | M | — |
| W6-10 | Incoming diplomacy: voice + variety + territorial legibility (E-CA-6 + E-CA-5) | **incoming 4→6.5** | M | — |
| W6-11 | Balance duo: morale symmetry + war-priced recruitment (E-CA-1 + E-CA-3) | fun of fighting | S–M | W6-4 (measure legibility first) |

Rationale: bugs first (they corrupt every later feel-evaluation and BUG-CA-7 is P1); naming is tiny and feeds the dispatch; the two legibility slices are the score-raisers and everything after is judged through them; drama content next; balance **last** so number-tuning isn't confounded with legibility gains. W6-2/6/8/9/10 are independent — a session may interleave them if blocked, noting it in STATUS.

---

## 2. W6-0 — Correctness A: dialogue identity + typed-answer routing **[LIVE-VERIFY]**

**Player-visible outcome.** Answering a popup always answers *that* popup; typing the words the game itself offers ("trust", "1", "secure") always works.

### 2.1 BUG-CA-7 — bind responses to the presented dialogue (P1)
*Live repro:* Britain's settlement offer was attached to a battle response; Saxony's envoy proposal then auto-activated on top; the player's `reject_settlement_offer` landed on Saxony (never seen), which also left a reversed campaign-log line ("Saxony rejected our open borders proposal (counterparty reversal)").
- **Design.** Stamp every dialogue pushed through `dialogue_manager` with a monotonically increasing `dialogue_id` (serialized counter on the manager, e.g. `next_dialogue_id`; round-trip both). Every payload that reaches Godot (`diplomatic_dialogue`, `incoming_proposal`, `incoming_settlement_offer`) carries its `dialogue_id`. `/respond_to_diplomatic_dialogue` accepts an optional `dialogue_id`: **if provided and ≠ the current top's id, do NOT apply the choice** — return the *current* dialogue re-attached with an in-voice notice ("Sire, another matter has arrived since — this concerns {nation}...") and `success=False, stale_dialogue=True`. Godot popups pass the id they rendered (`incoming_proposal_popup.gd`, settlement offer popup, `main.gd` routing). The typed terminal path may omit the id (it always answers the visible top).
- **Seams.** `backend/models/dialogue_manager.py` (push/replace stamp + serialization), `backend/commands/diplomatic_executor.py:handle_diplomatic_dialogue_response` (~line 125; id check FIRST, before any choice parsing), `main.py:/respond_to_diplomatic_dialogue` (pass-through of `request.get("dialogue_id")`), Godot: the popups that POST there.
- **Also fix the log line:** the wrong-direction `ai_proposal_rejected` one-liner ("X rejected OUR proposal" when the player rejected X's) — `campaign_log.py`, event direction keyed off who proposed, not who answered.
- **Tests.** `tests/test_w6_dialogue_identity.py`: stale-id response is refused + re-attaches current; matching id applies; ids round-trip serialization; the misroute scenario reproduced end-to-end (mount offer → push proposal on top → answer with offer's id → offer answered, proposal untouched). Live curl: reproduce the audit's Saxony sequence, confirm the guard.

### 2.2 BUG-CA-1 — the pending-question router
*Live repro:* with `pending_objection` set, typing "trust" fell to the LLM parser (bewildered clarification); "insist" hit the diplomatic handler.
- **Design.** In `main.py:/command`, BEFORE the parser is invoked (same altitude as CR-4 carryover, and deterministic per GR6): if a pending question exists, route exact answer tokens to its handler —
  - `world.pending_objection` + token ∈ {trust, insist, compromise} → `executor.handle_objection_response`.
  - pending capture choice + token ∈ {plunder, secure} → the `/capture_choice` handler path.
  - `world.pending_diplomatic_dialogue` + token is a digit or an `available_action_ids` keyword → `handle_diplomatic_dialogue_response`.
  Tokens only reroute **while the matching state is pending**; anything else falls through to the normal pipeline untouched (the CR fast-parser contract and golden corpus are unaffected — no keyword ownership changes).
- **Tests.** typed "trust" resolves a pending objection (trust delta applied); typed "2" picks option 2 of a pending dialogue; the same tokens with nothing pending still parse normally (corpus untouched, assert via parser eval run).

### 2.3 BUG-CA-10 — enumerate options on the typed surface
"Please choose an option (1-3), Sire." must append the numbered option labels. Seam: wherever that re-prompt is built in `diplomatic_executor` dialogue handling — compose from the pending dialogue's `options[].label`. Test: the re-prompt string contains every label.

### 2.4 BUG-CA-8 — re-mount must not degrade the diplomat
*Live repro:* a failed response re-attached the incoming proposal with `diplomat_name: "Unknown diplomat"` while the prose still said "Hardenberg". The error path rebuilds the payload through an impoverished builder — repoint it at the same builder the mailbox activation uses (`backend/mailbox_payloads.py`). Test: mount → bad response → re-mounted payload's `diplomat_name`/`diplomat_personality` equal the original's.

**Docs:** SAVE_FORMAT_REFERENCE (dialogue-manager id counter), BUG_FIXES.md rows → FIXED.

---

## 3. W6-1 — Correctness B: combat, movement, reports, stats **[LIVE-VERIFY]**

### 3.1 BUG-CA-2 + E-CA-2 — retreat honors intent and never flees INTO the enemy
*Live repro:* "Bernadotte, retreat to Rhineland" → Dresden; then auto-retreats marched him Dresden→Silesia→Lithuania→White Russia — each hop deeper into at-war Russia (17,000 men → 316).
- **Design (all deterministic, one function owns it).** Extend `world_state.get_safe_retreat_destination` (line ~2931):
  1. **New exclusion tier:** a region controlled by a nation the retreater's nation is **at war with** ranks BELOW every other option (new priority 5, "desperation-into-enemy"); it is chosen only when the alternative is encirclement. (Today at-war regions sit in tiers 3–4 alongside neutrals.)
  2. **Homeward bias:** within a priority tier, prefer (a) regions in `nation_starting_regions[nation]`, then (b) lower `get_distance` to the nation's capital, THEN (c) distance from the attacker. ("Away from the attacker" stops dominating direction.)
  3. **Explicit destination honored:** `movement_executor._execute_retreat_action` (line ~665) accepts the parsed target region; if it is adjacent and not excluded by rule 1, retreat there; if it is illegal, the message **names the substitution and why**: "Rhineland cannot be reached, Sire — Bernadotte falls back to {chosen} instead." Never silently discard the stated destination.
- **GR5:** enemy AI retreats route through the same function — its `enemy_ai._find_retreat_destination` (line ~4123) should delegate to or mirror the new tiers; verify with a test that an AI marshal doesn't retreat into a nation it's at war with when a neutral option exists.
- **Tests** (`tests/test_w6_retreat_doctrine.py`): stated-adjacent-legal destination honored; illegal destination → substitution named in the message; at-war region avoided when any alternative exists; encircled-by-war-regions still retreats (doesn't break the old guarantee); homeward tiebreak (two friendly options → the one nearer the capital); the Bernadotte chain reproduced → he now falls back WEST.

### 3.2 BUG-CA-3 — endowment without a region asks, never defaults
`grant_dotation` with no/unresolvable region currently target-defaults to the first region in the world dict ("We do not hold White Russia"). Fix at the executor entry (`economy_executor` / the grant path): missing region → `success=False` with the eligible list: "Which province, Sire? Eligible for endowment: {conquered non-homeland, non-estate, non-occupied-exempt regions}" (reuse the marshal-card `eligible_estates` derivation). Test: no-region command lists eligibles and mutates nothing; named-region path unchanged.

### 3.3 BUG-CA-4 — battle report remaining-strength fields
`battle_report.casualty_summary.attacker_remaining/defender_remaining` echo the originals (confirmed twice live). Fix in `battle_report.py` — compute from the same values the battle event carries (original − casualties). Test asserts report remaining == event remaining for both sides.

### 3.4 BUG-CA-5 — observation truthfulness + modifier label
- Reinforcement observation must not claim victory on a stalemate: `_pick_observation` branches on outcome (stalemate → "Ney reached the field, Sire — it saved the line, no more."). Same family as the July-9 side-attribution fixes.
- Rename the opaque modifier label "Strategic orders" → **"Forced march momentum (order completed)"** in the breakdown builder, and label the literal hold bonus **"Immovable (literal hold)"** where it appears. Labels only — GR1 math untouched.
- Tests: stalemate observation contains no victory language; label strings pinned.

### 3.5 BUG-CA-6 — dispatch intel freshness
*Live repro:* the dispatch's intel table said Mack @ Swabia while the same turn's events + `status` had him in Franche-Comte. Root cause in `dispatch._build_intelligence` (line ~413): the sighting dedup prefers **visibility rank** over **recency**, so a stale FULL snapshot beats this turn's PARTIAL truth. Fix: prefer the higher `intel.last_updated_turn` first; rank breaks ties. Test: stale FULL @ A vs fresh PARTIAL @ B for the same marshal → dispatch shows B.

### 3.6 BUG-CA-9 — participation counts (feeds ES-7 and W6-3)
`battles_won/lost` increments only for the primary pair (`combat.py:582/594`). Extend the post-battle pipeline so **every reinforcement participant** on the winning/losing side increments (the blessed ES-7 model already assumes this — econ-eval record: "every coordination participant increments battles_won"). Reset `idle_turns` for any marshal who fought (primary or reinforcer). Also record per-marshal `last_battle_turn` if trivially available for W6-3's arc memory — if it needs a new serialized field, add `Marshal.last_battle_turn` (serialize both ways) — one int, low risk. Tests: reinforcer's tally bumps; idle status clears; ES-7 expectation grows for a reinforcing marshal.

### 3.7 E-CA-4 — the explicit bad-odds attack warning
Deliberately **deferred into W6-4** (the muster preview IS the warning) — do not build a separate modal here. Listed so no session re-scopes it.

**Docs:** BUG_FIXES.md rows → FIXED; SYSTEMS_REFERENCE retreat section; SAVE_FORMAT_REFERENCE if `last_battle_turn` lands.

---

## 4. W6-2 — Dynamic Battle Naming *(user addition)*

**Player-visible outcome.** Battles accumulate history: "Battle of Swabia" → "Second Battle of Swabia" → "Third…"; titanic engagements read "The Great Battle of Swabia". Names appear identically in the battle message, battle report, campaign log, and the war HUD's `recent_battles`.

- **Design.** New serialized `WorldState.battle_counts: Dict[str, int]` (region → named-battle count). At the single naming site — `combat_executor.py:3661` (`battle_name = f"Battle of {target_location}"`) — increment and compose:
  - count 1 → `Battle of X`; 2–12 → `Second|Third|…|Twelfth Battle of X`; >12 → `{n}th Battle of X`.
  - **Great tier:** if total engaged (both sides' pre-battle strength incl. arrived reinforcements) ≥ **80,000** (blessed default; band 60k–100k), prefix "The Great " → "The Great Second Battle of X" reads badly, so: Great tier REPLACES the ordinal when both apply ("The Great Battle of X (their third meeting)" is over-engineering — just "The Great Battle of X").
  - Garrison assaults and bombardments are NOT named battles (unchanged scope: `resolve_battle` results only).
- **Consumers get it free** — they already read `battle_name` from the event. Verify the war HUD `recent_battles` entries carry the composed name (they carry `location` today — if so, add `name` to the recent-battle record; `war_status.py`).
- **Serialization:** `to_dict`/`from_dict` + `SAVE_FORMAT_REFERENCE.md` row + enforcement test.
- **Tests** (`tests/test_w6_battle_naming.py`): same region twice → "Second Battle of"; ordinal rollover >12; Great threshold at exactly 80,000; counts round-trip a save; two different regions independent; campaign-log one-liner shows the composed name.

---

## 5. W6-3 — The Dispatch Rewrite: *Berthier tells the story* (EXP-N1) **[LIVE-VERIFY]**

**The top-ranked item of the audit.** The simulation already produces the drama; this slice makes the morning dispatch *tell* it. Everything is deterministic templates over existing events — **no LLM** (GR6), no new mechanics.

### 5.1 Headline selection
Score the turn's fog-visible events (the dispatch already receives them) with a static priority table; the dispatch opens with the top event rendered as a one-sentence prose headline, then up to 2 sub-beats. Blessed default weights (tunable freely — display only):

| Event class | Weight |
|---|---|
| Own home region (in `nation_starting_regions`) captured by enemy | 100 |
| Own marshal broken / force-retreated in the enemy phase | 90 |
| Own marshal lost ≥25% strength since last dispatch | 85 |
| Enemy army entered own-controlled territory | 80 |
| Any own/vassal region captured | 75 |
| Coalition tier change / new war declaration touching France | 70 |
| Ally suffered a major defeat (ally marshal broken) | 60 |
| Estate erosion began (ES-7) / vindication event | 55 |
| Everything else (construction, AI-AI treaties, subsidies) | ≤20 |

Headline templates live beside the existing `_DIPLOMATIC_EVENT_TEMPLATES` pattern in `dispatch.py`; one template per class, in Berthier's register ("Sire — Mack has crossed into Franche-Comte. Lannes and Murat stand in his path.").

### 5.2 Danger flags on the marshal roster
Each dispatch marshal row gains `danger` (string, empty if none) — set when: co-located with an enemy force ≥1.5× own strength (fog-legal: use the player's own intel of that region, never omniscient reads — R5); morale <40; force-retreated last phase; supply attrition 2+ consecutive turns. Replaces the audit's "Awaiting orders" lie next to a 49k enemy. Godot `dispatch_view.gd` renders the flag line in warning color (it already colors severities).

### 5.3 Arc memory (the hunted-marshal callback)
Derive per-marshal chains at build time from the recent event log window (last ~5 turns of `world.event_log` — bounded scan, GR8-safe) — no new serialized state: `consecutive_defeats`, `hunted_by` (same enemy attacked the marshal ≥2 consecutive turns), `fled_across` (retreat count in window). When a chain exists, the marshal's status note upgrades: *"Bernadotte — hunted by Archduke Charles across three frontiers — stands at the Niemen with 300 men."* Cap: one arc line per marshal, max 3 per dispatch (highest-stakes first).

### 5.4 Cause lines on visible drift
- **Vassal loyalty** events name their cause: the `vassal_loyalty` event gains a `reason` field at emission (`vassal.py:process_vassal_loyalty` knows which modifier dominated: autonomy drift / war weariness / relation bonus / garrison) and the dispatch/log line renders it ("Switzerland 84 (−8): puppet resentment, war weariness"). This is R132's 80/20.
- **Berthier note** becomes headline-aware: one template per headline class + the existing default.
- **NO-INTELLIGENCE wall** (status report, `intel_report.py`): collapse to a count + the ≤8 frontier names (unknown regions adjacent to any known region): "No word from 85 provinces beyond the frontiers of Silesia, Tyrol, …".

### 5.5 Tests (`tests/test_w6_dispatch_rewrite.py`)
Synthetic event sets → correct headline picked (table order pinned); danger flags for each trigger (incl. the fog-legality: a fogged co-located enemy does NOT flag); arc chain detection from a scripted 3-turn event log; vassal reason strings; the NO-INTEL collapse; dispatch build cost bounded (no full-region scan — assert via the existing GR8 source-pin style if practical). Live: end 3 turns with a staged mauling, read `/dispatch`, confirm the headline is the mauling.

**Docs:** SYSTEMS_REFERENCE dispatch section; the memo's score addendum after landing (see §0).

---

## 6. W6-4 — Muster preview + standing orders surfaced (EXP-C1 + E-CA-4) **[LIVE-VERIFY]**

**Player-visible outcome.** Before a risky battle you see who will fight and *why the others won't* — the audit's three worst surprises (Soult sitting out, shared casualties, no odds warning) become the game's most characterful screen.

### 6.1 The muster block
On a player-issued `attack`, compute before resolution:
- attacker + target (fog-banded strength — exact only at FULL, else band; R5-safe),
- **per adjacent/co-located friendly marshal: WILL JOIN / WILL NOT + reason**, derived from the *existing* eligibility + Grouchy Rule logic (`combat_executor._is_reinforcement_eligible` + the literal check at `combat_executor.py:432`): `aggressive_marches` / `has_support_order` / `literal_awaits_orders` / `fortified_static` / `drilling` / `broken_recovering` / `hostile_refuses` / `cooldown_spent`. Reason codes → display strings via `display_names.py` (new map `MUSTER_REASON_DISPLAY`).
- odds band (`favorable / even / unfavorable`) via the CR-5 single source `objection_v2.inferred_attack_favorable` (do NOT write a second odds formula — GR1 spirit),
- a shared-casualty note when any co-located friendly will absorb losses.

### 6.2 Gating (E-CA-4 lands here)
- **Unfavorable or even odds** → the attack does NOT resolve on the first call: store a `pending_interrupt` of the existing contract (`interrupt_type: "muster_confirm"`, **must carry `"marshal": <name>`** — the July-7 L1 lesson — options `attack_anyway` / `cancel_order`), attach the muster block, `requires_input=True`. `/strategic_response` resolves it (the Godot interrupt popup already speaks this shape).
- **Favorable odds** → resolve immediately, with the muster block prepended to the battle message (compact, 1 line per marshal).
- **No double modal:** if this attack already passed a CR-5 delegation gate this action, skip the muster confirm (the muster block still renders on the result). AI/`_strategic_execution` paths bypass entirely (GR5 — the AI has its own scoring; the preview is a player legibility surface).
- First muster of a campaign appends the tutorial line about standing orders (§6.3), latch-on-surface like the CR-5 hint (serialized flag `muster_hint_shown` — one bool, both dict methods).

### 6.3 Standing orders — surface what exists
`"Soult, support Ney"` **already** authorizes a literal marshal to reinforce (SUPPORT order read by the Grouchy Rule). This slice only surfaces it: the `literal_awaits_orders` muster row appends *"— order 'Soult, support Ney' and he will march"*; the SUPPORT order-creation response confirms the doctrine ("Soult will march to Ney's guns — he holds your written order."). Verify SUPPORT's cost/objection path unchanged (blessed CR scope untouched).

### 6.4 The Grouchy Moment note (scope boundary — pinned)
This slice builds the **visibility substrate only**. The autonomous march-to-guns beat (AI-turn application of the muster rule) remains gated behind its own future design gate (re-homed at CR-5; unchanged). Do not implement it here; a test pins that a literal marshal with no SUPPORT order still does not auto-reinforce.

### 6.5 Tests (`tests/test_w6_muster_preview.py`)
Reason code per personality/state (aggressive joins; literal refuses without order, joins with SUPPORT; fortified static; hostile refuses); unfavorable → interrupt with `marshal` key + no resolution; favorable → immediate + block present; CR-5-gated delegation attack skips the second modal; AI path unaffected (enemy attack produces no interrupt); fog: PARTIAL target shows band not exact; hint latch serializes. Live: reproduce the audit's battle-1 (Ney vs stronger Mack) → muster confirm fires listing Soult's reason.

**Docs:** SYSTEMS_REFERENCE combat section; MULTI_MARSHAL_SPEC cross-note; golden corpus rows for "support" phrasing if any new phrasing is added (SUPPORT itself is existing).

---

## 7. W6-5 — The Literal Doctrine *(user addition — hone literal into a fantasy, not a gap)*

**User steer (verbatim intent):** literal marshals need not object — *the fantasy is generals who do exactly what they're ordered.* Their engagement comes from **fidelity you can see, precision you can exploit, and consequences you were warned about** — not from popups. This slice formally **supersedes R59/R153's literal-objection triggers** (delete the TODO rows in `personality.py:PERSONALITY_TRIGGERS` for literal or convert them to doctrine comments — they will never fire, by design; pin never-objects with a test).

### 7.1 The doctrine, stated (goes in SYSTEMS_REFERENCE + the marshal card)
> A literal marshal executes the letter of the order: no improvisation, no initiative, no objection. He is cheaper to command (strategic orders cost 1 AP, not 2 — existing), immovable on the defense (+15% literal hold — existing), and utterly predictable. What he will never do is march to the sound of the guns without your written word.

### 7.2 Components (all deterministic, mostly presentation over existing mechanics)
1. **Never-objects, pinned.** `disobedience.check_objection` already skips literal — add `test_literal_never_objects` (order a literal marshal into terrible odds → no objection, order proceeds/gates through the normal odds machinery instead).
2. **Order echo & completion report.** Literal marshals acknowledge and complete orders by quoting the order's own words (the verbatim text already rides `StrategicOrder.original_command`, rider-(d) substrate): acknowledgment — *"'March to Swabia.' It will be done exactly, Sire."*; completion — *"The order was 'march to Swabia'. Swabia is reached. I await further instruction."* Seams: order-creation response (`strategic_executor`), per-turn completion messages (`strategic.py`), literal-voice template bank in `display_names.py` or a small `backend/game_logic/marshal_voice.py` (2–3 variants each to avoid rote).
3. **Doctrine tells everywhere.** The marshal card (`marshal_overview.py`) gains a doctrine line for literals ("Executes orders to the letter"); the dispatch status note for a literal with an active order appends "(to the letter)"; the muster row already names it (W6-4); the existing reinforcement non-arrival line ("awaits explicit orders and did not march to the sound of the guns") is kept and moved into the same voice bank so all literal copy shares one register.
4. **The fidelity beat (stale-order tell) — the drama engine.** Per turn, for each **literal marshal with an active order** (bounded iteration — marshals with orders only, GR8-safe), if the order's context materially changed this turn — (a) a battle involving his own nation occurred in an adjacent region and he did not move, or (b) his PURSUE/SUPPORT target moved to a different region, or (c) his MOVE_TO destination's controller changed — emit a campaign-log + dispatch event (`literal_fidelity`): *"Soult holds at Lorraine, per your orders — the guns at Franche-Comte did not move him."* **Not an interrupt, no choice, no trust change** — pure narration of fidelity, the visible cost/virtue of commanding literals. Cap 1 per marshal per turn. Event type registered in `CAMPAIGN_LOG_TYPES` + `format_event_oneliner` + dispatch template (checklist steps 10–11).
5. **Precision rewards captioned.** At order creation for a literal: "(1 AP — Soult executes precise orders with fewer couriers)". The hold bonus label "Immovable (literal hold)" (done in W6-1 §3.4 — verify it reads through). No balance numbers change in this slice.
6. **CR-5 blessed scope untouched:** the literal ASK arm for vague delegations stays exactly as blessed (vague → ask; precise → execute). This slice never touches `delegation.py` routing.

### 7.3 Tests (`tests/test_w6_literal_doctrine.py`)
Never-objects pin; echo/acknowledgment quotes the verbatim command; completion line quotes it; fidelity beat fires on adjacent-battle-held case and NOT for non-literal marshals; fidelity beat absent when nothing changed; caps respected; event renders in campaign log + dispatch; doctrine line on the card; voice bank has ≥2 variants per beat (anti-rote assertion); a literal marshal WITH a SUPPORT order still reinforces (doctrine ≠ uselessness).

**Docs:** SYSTEMS_REFERENCE personality section (doctrine text); DESIGN_REFINEMENT R59/R153 rows → SUPERSEDED by W6-5 (user call recorded).

---

## 8. W6-6 — Enemy marshals speak (EXP-M2)

**Player-visible outcome.** The men you fight have mouths: after a battle, the enemy commander gets one line in his register, in the battle report and campaign log.

- **Design.** A deterministic template bank (new `backend/game_logic/enemy_voice.py` or folded into `battle_report.py`): keyed by (enemy personality × situation), situations = {repelled_you, beat_you_attacking, lost_ground, forced_retreat, stalemate}. 2–3 variants each (~30–40 authored lines), rotated deterministically by `world.battle_counts[region]` (no RNG — reproducible). Optional named rows for the marquee enemies (Mack, Kutuzov, Archduke Charles, Wellington, Blücher) override the personality default — e.g., cautious Mack repelling you: *"Mack does not leave his ground. He sees no reason to start today."*
- **Boundaries.** Enemy *marshals* only — named *diplomats* stay owned by `DIPLOMAT_VOICE_BIBLE.md`/DEF-1 (do not touch `resolve_named_diplomat`). Attach as `battle_report.enemy_voice` + a campaign-log flavor suffix; display-only (GR6), no serialization.
- **Tests:** line selected matches personality + situation; named override wins; deterministic across identical inputs; no line on garrison assaults; report field present and humanized.

---

## 9. W6-7 — Marshal Fates: capture, ransom, the last stand (EXP-M1) — 2 commits

**Player-visible outcome.** Broken armies carry a person-shaped stake: marshals can be taken, ransomed, exchanged — and an aggressive marshal can be offered a last stand. Building Blocks: **identical rules for the AI — Mack at Ulm becomes capturable.**

### 9.1 Commit 1 — capture core
- **Trigger.** When a forced retreat fires and either (a) post-battle strength < **5,000** (blessed default; band 3k–8k) or (b) `get_safe_retreat_destination` returns `None` or only tier-5 (into-at-war) options. Then roll the fate (combat's existing RNG, seedable in tests): **escape 60% / captured 40%** (band ±15); pure encirclement (`None`) = captured outright (replaces today's silent elimination).
- **The last stand (player-side choice, AI-side rule).** If the marshal is `aggressive` and player-owned, offer instead of the roll — `pending_interrupt` contract (`interrupt_type: "last_stand"`, **carries `marshal`**, options `fight_to_the_last` / `attempt_breakout`): *fight* = one final defense at +25% (blessed; band 15–35%), attacker halted this turn, survivors captured after; *breakout* = the escape/capture roll at −10% escape. AI aggressive marshals fight the last stand when defending a capital-adjacent or home region, else break out (deterministic rule, no roll).
- **Captured state.** New serialized `Marshal.captured_by: str` + `captured_turn: int`; a captured marshal leaves the map (location = captor's capital, strength 0, excluded from rosters/dispatch active lists — shown in a "Prisoners" line instead); remaining troops disband (50% returns to the owner's manpower pool). Fog/dispatch/ledger/marshal-overview all reflect it; capture is a top-weight headline in W6-3's table (add weight 95).
- **Serialization + enforcement + SAVE_FORMAT rows.** Campaign-log/dispatch events (`marshal_captured`, `last_stand`) through the full checklist.

### 9.2 Commit 2 — ransom & release
- **Clause type `prisoner_return`** in the existing clause registry (proposal + settlement guided-terms; follows the `forced_alliance` wiring pattern: acceptance values, harshness, keywords, display names, state mapping — the add-a-clause checklist in `diplomatic_executor`'s 4 state maps + `display_names` + `diplomatic_templates`). AI valuation blessed default: base **500g** (majors' marshals 800g), or clause-for-clause exchange when both sides hold prisoners.
- **Release paths:** ratified `prisoner_return` → marshal returns to his capital at 5,000 strength / morale 50 / `captured_by` cleared; **any peace treaty between the two nations auto-returns all mutual prisoners** (fold into `_ratify_treaty` effects). No escape mechanic in pass 1 (recorded cut — a future pass may add it; owner: this spec's backlog note, GR9 satisfied by naming it OUT).
- **AI behavior floor:** the AI *accepts/values* ransom clauses; it does not *initiate* ransom proposals in pass 1 (recorded cut, same backlog note).
- **Tests** (`tests/test_w6_marshal_fates.py`, both commits): trigger thresholds; seeded roll both branches; encirclement = capture; last-stand both options + AI rule; captured marshal absent from rosters/muster/AI candidate lists (check `enemy_ai` contact scans don't crash on captured marshals); serialization round-trip; ransom clause end-to-end (propose → accept → marshal returns); peace auto-return; Mack capturable by the player (AI-side symmetry); ES-7 interaction — a captured marshal's estates do NOT erode while captured (grace frozen; cheapest rule, pin it).

**Docs:** SYSTEMS_REFERENCE new section; SAVE_FORMAT; DIPLOMACY_SPEC clause table; the corpus row for any new typed phrasing ("ransom Marshal X" → route to proposal wizard path or typed proposal — decide in-session, corpus-pin whichever lands).

---

## 10. W6-8 — The Spoils of War: estate confiscation (EXP-E1)

**Player-visible outcome.** Conquering the province that sustains an enemy marshal's estate becomes a decision — the audit's live dead end ("Swabia already sustains Marshal Mack's household") becomes one of the most Napoleonic choices in the game.

- **Design.** When a capture resolves in a region present in any **enemy** marshal's `dotation_regions`, the existing plunder/secure capture choice (`capture_executor`) gains context + two more options:
  - **Confiscate the estate** — windfall = **2× the region's effective income** (blessed; band 1.5–3×); the enemy marshal loses the region from `dotation_regions` (his satisfaction drops → the AI nation's own ES-7 erosion machinery does the rest — no new erosion code); **−10 relations** with his nation (blessed; band −5..−15); each of the player's **cautious** marshals loses 1 trust (property is sacred — one-time, capped); the region becomes endowable by the player (normal ES-7 path).
  - **Respect the title** — the estate stays; while respected, a **+5 acceptance modifier** with that nation (blessed; cap one per nation; store as a small serialized list `world.respected_estates: List[{region, marshal, nation}]`, consumed by `calculate_acceptance` as a single additive term — follow the settlement-memories pattern).
  - Plunder/secure remain and imply confiscation? **No** — keep orthogonal: plunder/secure applies to the region, the estate choice is asked once after it (second popup via the same `capture_choice` pipeline, dialogue-typed, id-stamped per W6-0).
- **GR5:** the AI conqueror applies a deterministic rule instead of the popup: confiscates when at war with the estate-holder's nation, respects otherwise.
- **Tests** (`tests/test_w6_estate_confiscation.py`): choice appears only on estate regions; confiscate strips + windfalls + relations + cautious-trust; enemy marshal's erosion begins via existing machinery; respect stores + acceptance term applies + caps; player can endow post-confiscation ("Endow Ney with the Duchy of Swabia" finally works on Mack's old duchy — the audit's exact scenario as a named test); AI rule; serialization round-trip.

**Docs:** ECONOMY_REVISIT_SPEC cross-note (ES-7 rider landed); SAVE_FORMAT (`respected_estates`); display names for the new choice labels.

---

## 11. W6-9 — "What does Europe intend?" (EXP-D1 + coalition posture + R132 trend + R117)

**Player-visible outcome.** `"Talleyrand, assess our situation"` (the exact phrase that dead-ended live) returns the war room: per-war trajectory in prose, the coalition's **posture** (computed today in `coalition.py:get_coalition_posture`, consumed by the AI 6×, shown never), the top-3 threat sources (already itemized in `coalition_status.sources`), vassal loyalty trend + cause (rides W6-3's reason field), and **one recommendation ending in an executable option** (R117) — reuse the `proposal_options` dialogue shape so the player can click/type straight into the suggested action.

- **Seams.** `diplomatic_advisory.py` (new arm beside the nation-analysis arm; the "which nation shall I approach" router must NOT swallow "assess/situation/state of Europe" phrasings — add keywords to the mock parser per the checklist + corpus rows); data from `war_status.build_active_wars`, `coalition.py`, vassal events. Composition only — no new formulas; fog rules: army strengths through the fog-safe paths already used by the diplomatic ledger.
- **Recommendation rule (deterministic table, priority order):** losing war + settlement available → "seek terms"; coalition posture aggressive + threat >60 → "shore the weakest ally / fortify the frontier"; vassal <40 loyalty → "invest in X"; else → the highest-value diplomatic opening (relation −10..40 nation with open cooldown). One suggestion, never a list.
- **Tests:** phrase routes to the assessment (not the nation-picker); payload carries posture + ≥1 threat source + a recommendation with an executable option id; fog-safe strengths; corpus rows green.

**Docs:** DIPLOMACY_SPEC advisory section; corpus entries; DESIGN_REFINEMENT R117/R132 rows → LANDED-via-W6-9 when done.

---

## 12. W6-10 — Incoming diplomacy: voice, variety, and honest terms (E-CA-6 + E-CA-5)

**Player-visible outcome.** Envoys are people, proposals differ, and a peace offer says what happens to occupied soil.

1. **The diplomat speaks.** `incoming_proposal` gains `diplomat_line`: a deterministic per-register template bank (hawk / schemer / dove / chancery fallback — registers per `DIPLOMAT_VOICE_BIBLE.md`; **every line resolves through `resolve_named_diplomat()`**, Voice Bible rule) that *voices* the proposal AND its motive — `decision_reason` rendered in-character, not as a tag ("Hardenberg, stiffly: 'Europe grows uneasy at France's shadow, and Prussia would rather watch the roads than the frontier. Open the borders.'"). The clause bullets stay (they're the contract); the line gives them a face. Same treatment for `incoming_settlement_offer` (it already has `proposer_voice` — bring regular proposals to that bar).
2. **Anti-monotony.** Extend the existing anti-spam/cooldown machinery in `ai_diplomacy.py`: after a proposal of type T from nation N lapses or is rejected, N may not re-propose T for **6 turns** (blessed; band 4–10), and the hegemony-pressure trigger picks among {open_borders, non_aggression, trade/one-time-gift} by relation band instead of always open_borders. Respect the existing cooldown key rule (`proposal['proposal_type']`, never the rewritten `terms['type']` — documented trap).
3. **E-CA-5 — territorial honesty.** Settlement offer `terms_summary` appends the derived status-quo line when any covered participant occupies the other's soil: "Status quo: Britain retains Flanders, Amsterdam." Derive from current controller vs `nation_starting_regions` for the war's participants (bounded via `get_nation_regions`). Pure display; the ratification math is untouched.
- **Tests** (`tests/test_w6_incoming_voice.py`): line present + register matches the diplomat + motive voiced (decision_reason string absent in raw form); chancery fallback works for the 15 unnamed-court nations (NOT a bug — pinned); type-cooldown blocks a repeat within 6 turns and the trigger diversifies; the territorial line lists exactly the occupied home regions; no fog added to any diplo path (project rule: diplomacy has no fog).

**Docs:** DIPLOMAT_VOICE_BIBLE addendum note (registers reused, no new named diplomats); DIPLOMACY_SPEC proposal-variety note.

---

## 13. W6-11 — Balance duo (E-CA-1 + E-CA-3) — numbers, measured, last

Run only after W6-4 has landed (legibility first, so the feel change is attributable).

1. **E-CA-1 — morale symmetry.** Today the defender's morale barely moves through massive casualties (live: Mack at morale 95 after 15k+ losses across three battles) while attackers/reinforcers bleed. Change (in `combat.py`'s morale block, the single source): casualty-scaled morale loss applies to **both** sides symmetrically (same `_scaled_morale_loss` curve); outcome bonuses stay (+10 victory / +5 narrow / +5 stalemate-holder). Blessed shape; band: the defender's scaled loss may be dampened to 75% of the attacker's curve if playtests over-shift, but never below.
   *Acceptance test:* the audit's battle-2 numbers replayed (50k defender takes 6.3k casualties in a stalemate) → defender morale drops meaningfully (≥8 points), attacker unchanged from today.
2. **E-CA-3 — war-priced recruitment.** `economy_executor._calculate_recruit_cost` (line ~177, base 200 inf / 300 cav): multiply by **3× when the recruiting nation is at war** (blessed; band 2–4×) and by **(1 + over-limit overage ratio)** when above force limit (189k/130k → ×1.45). Effects: rebuilding a mauled army mid-war is a treasury event (~600–900g per 10k) instead of a rounding error; peacetime rebuilding stays cheap. **GR5/solvency:** the AI pays the same cost through the same executor — extend the E1 band test style check: every 1805 AI nation at war can still afford its historical recruitment cadence (a two-sided assertion mirroring `test_economy_e1_band.py`; if a minor breaks, the war multiplier may drop toward 2× within band). E6 bankruptcy mercy untouched (recruiting is optional spending).
   *Ledger:* recruit spending already flows through `record_gold_spent` — verify the Spent line reflects it.
- **Tests** (`tests/test_w6_balance_duo.py`): symmetry math; the battle-2 replay; war multiplier + over-limit multiplier compose; peacetime unchanged; AI-solvency two-sided check; ledger Spent visibility.

**Docs:** ECONOMY_REVISIT_SPEC (E-CA-3 recorded as landed EC-pass-2 item); SYSTEMS_REFERENCE combat morale section; the memo score addendum (final re-score, §0).

---

## 14. Cross-slice contracts (do not violate)

- **No new LLM calls anywhere in this wave.** Every line of new player-facing text is a deterministic template (GR6). CR-3's one-blocking-call guarantee and the CR-5/5b blessed scope are untouched.
- **Every `pending_interrupt` carries `"marshal"`** (July-7 L1 lesson) — W6-4 muster and W6-7 last-stand both.
- **Every new event type** walks the checklist: `CAMPAIGN_LOG_TYPES` + `format_event_oneliner` + dispatch template + display maps.
- **Every new field serializes** both ways + SAVE_FORMAT row + enforcement test (`battle_counts`, dialogue id counter, `muster_hint_shown`, `captured_by`, `captured_turn`, `respected_estates`, optional `last_battle_turn`).
- **Fog discipline:** player-facing surfaces use `get_visible_enemies`/intel bands (W6-3 danger flags, W6-4 muster); diplomacy stays fog-free; combat/AI stay omniscient.
- **GR8:** no `world.regions.values()` in per-turn paths — W6-3 arc memory scans the event-log window, W6-5 fidelity iterates marshals-with-orders, W6-10 territorial lines use `get_nation_regions`.
- **Voice ownership:** named diplomats = Voice Bible + `resolve_named_diplomat` (W6-10); enemy marshals = the new W6-6 bank; Berthier = dispatch templates; literal marshals = the W6-5 bank. Don't cross the streams.
- **Blessed-numbers ledger (for tuning sessions):** Great-battle 80k (60–100k) · fate floor 5k (3–8k) · escape 60%/capture 40% (±15) · last stand +25% (15–35) · ransom 500g/800g · confiscation 2× income (1.5–3×), −10 relations (−5..−15), respect +5 acceptance · proposal type-cooldown 6 turns (4–10) · war recruit ×3 (2–4) · defender morale curve 100% (≥75%).

## 15. Definition of done (the wave)

All slices ✅ with green pre-commit; BUG_FIXES.md Creative-Audit rows all FIXED; DESIGN_REFINEMENT Wave 6 rows all point here with landed dates; the re-score addendum on the memo shows narration ≥7 and combat legibility ≥7 (if a measured pillar misses, the gap analysis goes to the user with options — do not silently extend the wave); STATUS/CLAUDE.md queue advanced to the **Marshal Content Pass gate** (unchanged — MC keeps its own user gate; W6-5/W6-6 do not preempt MC-1 ability authoring).
