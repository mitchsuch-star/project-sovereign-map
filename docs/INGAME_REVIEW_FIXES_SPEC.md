# In-Game Review Fixes & Improvements (row **IGR**)

> **v0.1 — SPEC, awaiting a user gate on §5.** Queued July 25, 2026 from the live
> in-game review held the same day. **Evidence of record =
> `docs/audits/INGAME_REVIEW_2026_07_25.md`** (France/1805 played in the real client,
> seed `historical` turns 1–9 + a 5-turn `austerlitz` variance pass).
>
> The review found **five defects and fixed all five in-session** (commit `bdeb17c`,
> `tests/test_ingame_review_fixes_2026_07_25.py`). **This spec owns what was ROUTED
> rather than fixed** — four `BUG_FIXES.md` rows (IGR-1..4) and three
> `DESIGN_REFINEMENT.md` rows (IGR-D1..3), plus six polish items observed on screen
> but not yet filed.
>
> **Scope discipline:** this is a *polish and honesty* pass, not a systems phase. It
> raises the two weakest measured pillars — **narration 6.0** and **UI/UX 6.5** — and
> closes the GR9 promises the review found unowned. It does not touch combat, the
> economy model, or the agenda substrate.
>
> **Reading order:** §1 what the review left open · §2 the slices · §3 acceptance ·
> §4 deferrals · §5 the gate (4 questions).

---

## 1. What the review left open

The review's own summary of the three biggest fun-factor gaps maps onto this spec as:

| Review gap | Owned here by |
|---|---|
| **1. The campaign log is unreadable** (24 of 25 turn-9 events were AI-AI refusals) | **IGR-B** |
| **2. The paid half of marshal drama was dead** | *already FIXED in `bdeb17c` — nothing owed* |
| **3. The marquee carve is hard to actually reach** | **IGR-D** (+ the §5 Q2 gate) |

Everything else in this spec is smaller, and deliberately so: the review scored eight of
ten pillars at 7.0 or better. The wins available are polish wins.

### 1.1 The standing GR9 debts

Two player-facing promises currently have no landing, which is what makes them spec
material rather than backlog:

- **Talleyrand's "designs held in check" counsel** renders no rung in a normal campaign
  (IGR-4). Either it becomes reachable or it is retired in writing.
- **"Your drafted terms for X carry into the talks"** was honest-ified in `bdeb17c`, but
  the underlying situation stands: the only route the game offers a blocked player
  silently drops the `create_client` clause (IGR-3). The copy no longer lies; the
  *feature* is still hard to complete.

---

## 2. The slices

Ordered so that the two gate-free slices land first (the project's slice-review cadence:
land a low-risk slice, pause, then take the bigger one).

### IGR-A — Honest copy (no gate)

Small, independent, all player-visible. One commit.

| # | Item | Seam | Done when |
|---|---|---|---|
| A1 | **The whole hard-block vocabulary leaks raw internal keys** into the ally-entry proposal copy (IGR-2, R7). Observed on screen as *"Spain cannot join against Prussia: no_participation_path."* — see the seam note below; this is a family of **six**, not one string | `diplomatic_executor.py:1763-1767` renders `str(hard_blocks[0])` **verbatim** into both the summary line and the warning text; `campaign_log.py:1447` renders the same reason with only a `.replace("_", " ")` | Every ally-entry reason renders as prose on **both** surfaces. A test enumerates all six producers and asserts no rendered string contains `_` or matches a bare snake_case token |
| A2 | **"Political Context:" repeats its own two lines verbatim.** Observed on the WAR DECLARATION modal (*"Reliability would fall from 0 to -10." / "Likely co-belligerents: Spain, Bavaria."* then the identical pair again as bullets) and again on the ally-entry popup. **Verified structural, both ends named** — see the seam note below | backend `diplomatic_executor.py` builds `extra_lines = [w["text"] for w in warnings]` into `warning_text` **and** passes `warnings` on the same payload; `proposal_confirm_popup.gd:344` then renders `data.warnings` again under a "Political Context:" heading | The lines appear once. A test asserts no line in a war-declaration dialogue body is duplicated; boot smoke + parse harness for the `.gd` change |
| A3 | **A nation name typed as a region gets a string-similarity suggestion from the wrong end of Europe.** `Soult, move to Saxony` → *"Region 'Saxony' not found. Did you mean 'Savoy'?"* — Saxony is a nation whose capital region is Dresden | the movement-target resolution + the Sweep-5 "Nearby:" passthrough in `parser.py` | When the unmatched token is a known nation, the suggestion lists *that nation's* regions (nearest to the ordered marshal first). Corpus row added per the 12-step checklist |
| A4 | **Releasing a vassal reports nothing.** `release Kingdom of Italy` printed one line and no consequences — lost tribute, lost co-belligerency, and (materially, for NA-6) the fact that its dormant formation deck wakes | `vassal_executor._execute_release_vassal` | The message names the tribute forgone, the war exit if any, and the deck waking. Test pins all three |

**Why A4 matters beyond flavour:** releasing Kingdom of Italy is exactly what lights the
`→ forms: Italy` watcher. The game currently performs its own most interesting causal
link in silence.

#### A1 seam note — verified July 25, 2026

`diplomacy.py` appends **six** hard-block kinds, and **three of them are dynamic**, so a
flat `display_names` map cannot cover them:

| Producer | Key | Shape |
|---|---|---|
| `diplomacy.py:5747` | `armistice_cooldown_with_<nation>` | dynamic |
| `diplomacy.py:5751` | `at_war_with_<nation>` | dynamic |
| `diplomacy.py:5755` | `direct_enemy_of_<nation>` | dynamic |
| `diplomacy.py:5761` | `anti_promiser_coalition_member` | fixed |
| `diplomacy.py:5766` | `hard_reject_posture` | fixed |
| `diplomacy.py:5770` | `no_participation_path` | fixed |

The fix is therefore a **small formatter** (fixed map for the three static keys + a prefix
rule that splits the trailing nation tag and resolves it through the existing
`display_names.display_nation()`), placed at a **single new chokepoint** that all three
call sites use — not per-surface copies, which is how the beat-7 cause copy drifted
(IGR-F3, fixed in `bdeb17c`).

**Reachability:** one click from boot. `europe_1805.json` authors
`"France|Spain": "ALLIANCE"`, so the very first war declaration against a PEACE nation
raises the ally-entry review with Spain as a candidate, and Spain has no march route to
Prussia — which is exactly the path this review walked.

> ⚠ **The fix must be display-only — do NOT rename the keys.**
> `diplomacy.py:6385-6388` branches on the literal strings `"hard_reject_posture"` and
> `"no_participation_path"` to choose the AI feasibility `decision_reason`; renaming
> silently mis-routes `ai_should_propose_bargain` to the generic `hard_blocked` arm.
> `tests/test_wb_c_war_entry.py` also pins the key vocabulary in six places
> (`:207 :213 :220 :230/:235/:245 :250 :257`). All six stay green under a display-only
> change.

#### A2 seam note — verified July 25, 2026

The duplication is **structural, not a copy slip**, and it spans the wire:

1. `diplomatic_executor.py` composes `extra_lines = [w["text"] for w in warnings]` and
   appends them to `warning_text` (the modal's body prose);
2. the same `warnings` array also rides the payload;
3. `proposal_confirm_popup.gd:344` renders `data.warnings` **again** beneath a
   `[b]Political Context:[/b]` heading (capped at 2, which is why exactly two lines
   repeated on screen).

Fix on **one** side only — the natural choice is to stop folding `extra_lines` into
`warning_text` and let the popup own the presentation, since the popup can colour by
severity and the prose cannot. Note `proposal_confirm_popup.gd` has three
"Political Context:" call sites (`:344`, `:1630`, `:1658`); check all three for the same
double-render before landing.

### IGR-B — The campaign log becomes readable *(gate Q1)*

The review's #1 gap. Turn-9 evidence: 25 events, 24 of the form
`D <X> rebuffs <Y> (open borders)`; per-turn counts 19–40 dominated throughout; the one
dramatic line (`The court of Russia takes up a new design: The Gulf and the Straits`)
buried at the bottom in identical styling.

**Hard constraint:** the underlying `ai_ai_proposal_refused` record is AI-3's
ladder-gate substrate (AI-2a) and **must not be deleted**. This slice is a *rendering*
change only.

Recommended shape (Q1 option **a**): aggregate at the log-formatting seam — one line per
(target, proposal_type) per turn, e.g. *"Nine courts rebuffed Austria's overtures
(non-aggression)."* Keeps the information, removes the volume, needs no new UI and no
schema change.

Done when: a turn that generated 24 refusals renders ≤3 log lines for them; the Russia
design line is visible without scrolling; a test drives N synthetic refusals and asserts
the rendered line count and that the aggregate names the correct courts.

### IGR-C — Talleyrand's counsel stops promising what it cannot deliver *(gate Q3)*

`designs_in_check` was `[]` across two live war-room runs. The rung requires
`_restraint_block_reason == 'exposed'` on a **non-player → non-player** design; at the
1805 boot Austria short-circuits on `busy` and Prussia reads `None`, and AI-3r's own
§8.2 measured 0 ambient council wars across 8 seeds × 40 turns.

Recommended shape (Q3 option **a**): **broaden the rung to France's own designs held in
check.** The Emperor's Own Exposure block already computes exactly this reading
(`Free field army: 159,000 of 189,000 — prudence holds the rest against Britain`), so the
counsel becomes *advice the player can act on* rather than trivia about third parties —
and it is reachable on turn 1 of every campaign.

Done when: the war room renders a designs-in-check rung in a boot 1805 campaign, and a
test pins it firing for the player's own exposure. If Q3 goes to **c** (retire), the rung
and its copy are deleted and `AI_WAR_DECISION_SPEC.md` records the retirement.

### IGR-D — The carve becomes completable *(gate Q2 — the biggest question in this spec)*

**The situation, measured.** I reached every prerequisite by real play: at war with
Prussia, Posen held and secured, the Formables gate flipped to green ticks, the clause
*"Erect Duchy of Warsaw from Prussia's lands"* authored into the draft. Then:

- the **joint** route needs Austria, Britain, Prussia *and* Russia each at 50/50 — they
  sat at −31, −24, −18, −34;
- the **bilateral** route the game itself offers ("Make peace with Prussia only") drops
  identity clauses by design (`_pair_substitute_seed_terms` translates money and taken
  territory only).

So the Proclamation card **has never been sighted in-client**.

**The historical argument for allowing it (Q2 option a):** the Duchy of Warsaw was
created at **Tilsit — a separate peace with Prussia alone, while the war with Britain
continued.** That is precisely the case the engine currently forbids. Carving from one
defeated court while other wars run is not an edge case; it is the canonical instance of
the feature.

Done when: a player who has beaten one court can carve from that court alone, the
Proclamation card fires, and the review's must-see #4 can be closed with an in-client
sighting. Includes a live verification pass (boot the engine, grep `SCRIPT ERROR`).

### IGR-E — Plunder earns its prompt *(gate Q4 — needs a blessed number)*

Plundering Nassau yielded **87 gold** against 3,085/turn income and a 5,177g treasury.
Secure (stability 25) was strictly correct in every situation met, so a per-conquest
modal that stops the game asks a question with one right answer.

This is a balance change and therefore escalates: the number is the user's. §5 Q4 offers
the shapes.

### IGR-F — The small courts write one letter, not five *(no gate)*

Turns 2–5 delivered ~3–5 near-identical Open Borders / Non-Aggression proposals per turn
from minors, each a blocking modal that interrupts a command already in flight (the typed
order echoes, then its result is deferred behind the popup).

The per-nation voices are genuinely among the best writing in the game — Reis Efendi's
*"an old admirer of whatever endures"*, Consalvi's *"her friendship rather than her
fear"* — and volume is flattening them. Batch minor-court routine proposals into one
digest with per-row accept/decline; keep the voice line on each row. Great-power and
settlement traffic is unaffected.

### IGR-G — Two legibility fixes on surfaces the review used constantly *(no gate)*

| # | Item | Evidence |
|---|---|---|
| G1 | **The settlement authoring viewport shows ~5 lines.** With the header, the Allied-petitions block and the button grid pinned, working a 7-item demand list meant many small scrolls to reach the carve clause | screenshot sequence, review §3 |
| G2 | **A five-marshal stack is an illegible pile.** Co-located corps render overlapping sprites under overlapping name labels at default zoom | the U5 "piece size/clustering" sign-off item, still open |

---

## 3. Acceptance

- Suite green and ruff clean per commit; the pre-commit hook is the gate.
- **Any `.gd`/`.tscn`-touching slice boots the engine once and greps `SCRIPT ERROR`
  before landing**, and regenerates the parse harness report (EXIT=0) — the standing rule
  from the MC exit review.
- **IGR-B, IGR-D and IGR-F are verified live in the client**, not just by test: the
  review found five defects that all tests were green through.
- IGR-D closes with an **in-client screenshot of the Proclamation card** — the one
  must-see this review could not deliver.
- `BUG_FIXES.md` IGR-1..4 and `DESIGN_REFINEMENT.md` IGR-D1..3 are struck through with
  their landing commit as each slice lands.

---

## 4. Deferrals (GR9)

Nothing in this spec is deferred without an owner. Items observed in the review and
**deliberately not taken here**, with their reasons:

| Item | Why not here | Owner |
|---|---|---|
| Beats 2/3/7 never firing | Structural and already measured (`AI_WAR_DECISION_SPEC.md` §8.2: 0 crises / 40 turns × 8 seeds); not a defect | AI-V arm (a) |
| "The Polish Question" grudge label unsighted | Requires the Duchy to exist — becomes reachable the moment IGR-D lands | IGR-D's live pass |
| Congress beat 6 unsighted | The campaign ended at turn 9; the exhausted-pair exit needs ~T15+ | Any longer playtest |
| Modal stacking (a queued envoy rendered over the settlement I had clicked) | Observed once, not reproduced; needs a repro before it is worth a fix | Re-check in IGR-F's live pass |

---

## 5. The gate — four questions

### Q1. How should the campaign log handle AI-AI diplomatic traffic?

| | Option | Effect |
|---|---|---|
| **a** | **Aggregate per (target, proposal_type) per turn** *(recommended)* | *"Nine courts rebuffed Austria's overtures."* Keeps the information, removes the volume, no new UI, no schema change |
| b | New "minor diplomacy" log category, off by default | Player-controllable, but adds a filter UI and a preference to persist |
| c | Suppress AI-AI refusals from the log entirely | Cheapest; loses a real signal about who is isolated |

**Recommendation: (a).** The information is genuinely interesting in aggregate — *"nine
courts rebuffed Austria"* is a story; twenty-four separate lines are not.

### Q2. Should identity clauses survive a separate peace? *(the important one)*

| | Option | Effect |
|---|---|---|
| **a** | **Carry them** — extend the pair-substitute carry-over to translate `create_client` (and vassalage / liberation) into the bilateral dialect *(recommended)* | Tilsit becomes possible: carve from Prussia alone while the British war runs. Makes the Proclamation reachable in a normal campaign. Cost: the bilateral acceptance model must price an identity clause, and the armistice arm must keep excluding them (the G4F-15 ruling stands) |
| b | **Steer back** — when the draft holds an identity clause, disable "Make peace with X only" with a reason naming the joint route | Small and honest, but leaves the marquee feature gated behind beating four great powers at once |
| c | Leave as is | The copy fix in `bdeb17c` already stops the lie; the feature stays hard to reach |

**Recommendation: (a)**, on the historical argument above — and because a feature the
review could not reach in nine turns of competent play is a feature most players will
never see.

### Q3. What becomes of the "designs held in check" counsel?

| | Option | Effect |
|---|---|---|
| **a** | **Broaden to France's own exposure** *(recommended)* | Reachable turn 1; reuses the Emperor's Own Exposure reading; turns trivia into advice |
| b | Give the AI-AI form a reachable trigger | Larger — it means changing when `exposed` can be the blocking reason, which is AI-3r balance |
| c | Retire the rung | Honest and cheap; loses a good idea |

**Recommendation: (a).**

### Q4. What is plunder worth? *(a blessed number is required)*

| | Option | Effect |
|---|---|---|
| **a** | **Scale to the province** — plunder yields ~3–5 turns of that province's income *(recommended shape; the multiplier is the user's call)* | Nassau would have paid ~450–750g instead of 87g — enough to matter early, never enough to fund a war |
| b | Re-cut the choice as stability-vs-authority rather than gold | Removes the balance question entirely; changes what the prompt is *about* |
| c | Leave it | Accept that Secure is always correct and the prompt is flavour |

**Recommendation: (a) with a multiplier of 4.** In-band tunable; escalate any structural
change.

---

## 6. Build order

`IGR-A` (gate-free) → **pause for review** → `IGR-B` (Q1) → `IGR-C` (Q3) → `IGR-G`
(gate-free) → `IGR-D` (Q2, the big one, ends with the live Proclamation sighting) →
`IGR-F` (gate-free) → `IGR-E` (Q4) .

`IGR-D` sits late deliberately: it is the only slice that touches the settlement engine,
and it wants the polish slices already landed so its live pass is clean.
