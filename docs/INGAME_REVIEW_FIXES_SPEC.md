# In-Game Review Fixes & Improvements (row **IGR**)

> **v1.0 — ✅ GATE HELD AND BLESSED July 25, 2026 under the user's delegated grant**
> ("whats reccomendation for q answers" → "put in answers"). **Gate record = §5,
> authoritative.** All three live questions decided at the spec's recommendations, with one
> amendment: **Q2 lands as a split, not a binary.** The build may proceed on all slices.
>
> Queued July 25, 2026 from the live in-game review held the same day. **Evidence of record =
> `docs/audits/INGAME_REVIEW_2026_07_25.md`** (France/1805 played in the real client,
> seed `historical` turns 1–9 + a 5-turn `austerlitz` variance pass).
>
> **v0.2 → v0.3 (same day) — the verification pass.** Every routed item was re-measured
> against master by a find→**refute** fleet before this spec was trusted, and the refuters
> then went after my own corrections. Net: **seven claims across v0.1 and v0.2 were wrong**,
> **one whole slice (IGR-C) is withdrawn**, one escalation was reversed, and two unrelated
> defects were found in passing (routed, §4.1). Every correction is marked **⚠ v0.1 SAID**
> / **⚠ v0.2 SAID** so the reasoning stays auditable rather than silently rewritten. The
> spec is *smaller* than v0.1 as a result, which is the point.
>
> The review found **five defects and fixed all five in-session** (commit `bdeb17c`,
> `tests/test_ingame_review_fixes_2026_07_25.py`). **This spec owns what was ROUTED**
> — three live `BUG_FIXES.md` rows (IGR-1/2/3; **IGR-4 is withdrawn**, §2), three
> `DESIGN_REFINEMENT.md` rows (IGR-D1..3), and the polish items observed on screen.
>
> **Scope discipline:** a *polish and honesty* pass, not a systems phase. It raises the
> two weakest measured pillars — **narration 6.0** and **UI/UX 6.5** — and closes the GR9
> promises the review found unowned. It does not touch combat, the economy model, or the
> agenda substrate. **Every slice below is view/copy-layer** except IGR-D and IGR-E.
>
> **Reading order:** §5 **the gate record — read it first** · §1 what the review left open ·
> §2 the slices · §3 acceptance · §4 deferrals + the drive-by finds · §6 build order.

---

## 1. What the review left open

| Review gap | Owned here by |
|---|---|
| **1. The campaign log is unreadable** (24 of 25 turn-9 events were AI-AI refusals) | **IGR-B** |
| **2. The paid half of marshal drama was dead** | *already FIXED in `bdeb17c` — nothing owed* |
| **3. The marquee carve is hard to actually reach** | **IGR-D** (+ gate Q2) |

### 1.1 The standing GR9 debt

One, not two. **"Your drafted terms for X carry into the talks"** was honest-ified in
`bdeb17c`, but the *feature* is still hard to complete (IGR-3 / gate Q2).

The second candidate — Talleyrand's "designs held in check" rung — **was investigated and
is not a debt**: the exposure mechanic's other two surfaces render at boot (both verified
PASS in the review) and the AI-vs-AI silence already has an owner in
`AI_WAR_DECISION_SPEC.md` §8.2-1. See the withdrawal in §2.

---

## 2. The slices

### IGR-A — Honest copy *(no gate)* — ✅ **LANDED July 25, 2026**

> **Landing record — authoritative for what A1–A4 actually became.**
> Tests `tests/test_igr_a_honest_copy.py` (50). Suite 14,990/3, ruff clean,
> parser eval **461/461** mock (+4 corpus rows), Godot parse harness EXIT=0
> (17/17 scripts, both scenes instantiate), headless boot 0 `SCRIPT ERROR`,
> M1–M7 and the 40-turn `BASELINE_SERIES` byte-identical.
>
> **A1** — one helper `display_names.ally_entry_block_line(reason, ally, enemy,
> promiser)` returns the WHOLE sentence, backed by `ALLY_ENTRY_BLOCK_DISPLAY`
> (deliberately NOT in `_CATEGORY_MAPS`, per the trap below) with **prefix
> matching** for the three keys that carry a dynamic nation suffix and its own
> prose fallback (never `_fallback_display_name`, which title-cases the key into
> "No Participation Path"). Consumed at `diplomatic_executor.py`'s review
> dialogue, `campaign_log.format_event_oneliner`, and the latent
> `diplomacy.resolve_join_opportunity` site. Raw keys stay on the machine
> fields. Register is chancery third person — the same line feeds the log,
> which contains zero "Sire".
> **⚠ the spec's "2 live surfaces" was wrong: surface 2 was DEAD.**
> `filter_campaign_log` had no `hard_block_surfaced` branch and no
> default-include fallthrough, so the event never reached the overlay. A1 adds
> the branch — otherwise "renders as prose on both surfaces" was unverifiable
> in game. The event also now carries `promiser`, without which the coalition
> line could only say "against us". No new event type (`CAMPAIGN_LOG_TYPES`
> still 140).
>
> **A2** — the inline append dropped at BOTH confirm sites; `warnings[]` is now
> the single delivery and the popup owns presentation. The cap was raised
> **2→4 at all three `mini(warnings.size(), N)` sites**, not the one the spec
> named — break-treaty renders through `_build_content` (`:345`), a different
> builder. `force_break_treaty_confirmation` was ABSENT from main.gd's
> `PROPOSAL_CONFIRM_DIALOGUE_TYPES` and fired a `push_warning` on every fire;
> added, since that route now carries the only copy.
> **⚠ the paradox inline STAYS.** `commitment_paradox_popup.gd` renders
> `message` and nothing else and its payload has no `warnings` key, so
> `diplomacy.py:7792-7808` is the *only* delivery of the paradox reliability
> preview — dropping it would have silently deleted the feature with zero test
> coverage. It is routed through the new single formatter
> `display_names.warnings_to_plain_text` instead. `tests/test_playtest_bugfixes.py:250`
> consciously flipped: the line must be in `warnings[]` and ABSENT from
> `message`/`talleyrand_text`.
>
> **A3** — new single-source predicate `backend/ai/nation_names.py`
> (`resolve_typed_nation` / `nation_province_list`), NOT a widening of
> `_nation_demonyms` — that list is shared with the strategic-target
> classifier, and widening it reclassifies "march to Saxony" as a generic army
> order (a pin a prior adversarial review wrote for exactly this hazard). It
> runs **after** the exact-region check, so the collision set — **Hanover,
> Naples AND Normandy**, three not one — keeps resolving to the province, and
> **before** the demonym null, so "Ottoman"/"Papal States" get the helpful
> answer instead of the dead-end ask. It never nulls: nulling discards the
> typed word and is strictly worse than today. The answer is carried at
> `executor._fuzzy_match_region`, the single chokepoint all seven callers
> reach, and surfaced on the attack arm too.
> **⚠ three spec claims corrected.** (a) Saxony/Prussia/Bavaria do NOT resolve
> to None at the parser — they pass through and the *executor* answers, so the
> named seam was not where the defect lived. (b) **`Britain → Brittany` is a
> second wrong-province case** the spec missed — a real 7-hop march. (c) the
> attack arm does not "refuse"; it only did because Asturias happened to be
> empty, and with an enemy standing there it staged a commit-able muster
> 1,500 km away. The eval gate is **461/461**, not the 433/433 the spec cites.
> `llm_client.py` and `validation.py` deliberately UNTOUCHED — those rows are
> legacy *region* names, and two corpus rows ride them on the cold path.
>
> **A4** — the report names tribute lost (measured 375/337/225 g per boot
> vassal), the threat drop from `reduce_threat`'s RETURN value (it clamps at 0,
> so the constant −8 is a lie below 8), the 5-turn cooldown (now the named
> `RELEASE_COOLDOWN_TURNS`), the forward-looking loss of the call to arms, and
> **the woken deck plus its formation watcher** — releasing Kingdom of Italy is
> exactly what un-blocks `→ forms: Italy`, and the game had been performing its
> own most interesting causal link in silence. Every clause is conditional:
> Switzerland has no deck, the Continental System is empty at boot, and all
> three vassals field zero marshals. Gated on `not rebellion`.
> **⚠ two spec claims corrected.** Release does NOT cost co-belligerency —
> only the lord–vassal pair goes to PEACE, and the released court keeps its
> other wars. And `release_vassal(rebellion=True)` is **not** the rebellion
> path: it has zero production callers (`check_vassal_rebellion` duplicates the
> cleanup inline), though the arm is still guarded.
>
> **Also taken:** `BUG_FIXES.md` **IGR-X1** (P1 save/autosave crash), whose own
> routing said "take before IGR-A" — `del marshal._recovery_destination`
> removed the attribute that `Marshal.to_dict` reads directly.
>
> ---
>
> **Post-landing adversarial review (38 agents, 6 lenses → 2 refuters each) —
> 16 raw findings, 4 fixed, addendum below.** The headline is that **A3's first
> cut was half a fix**, and the refuters got that one wrong — I reproduced it
> by hand before accepting it:
>
> - **A3 was bypassed on the STRATEGIC path.** Only the bare `move to`
>   phrasing reaches the guarded ladder. `march to` / `advance to` / `head to` /
>   `proceed to` / `make for` / `travel to` / `push to` / `deploy to` /
>   `relocate to` / `journey to` all run through `parser.py`'s strategic-target
>   fuzzy pass, which had no guard — **ten of eleven phrasings still built a
>   real MOVE_TO order to Asturias and stepped Ney out of Rhineland.** Guarded
>   at the strategic pass, and `strategic_executor` now carries the same honest
>   answer (it has its own failure message, so a named court read as an
>   unintelligible phrase). The sentence is single-sourced in
>   `nation_names.nation_not_a_province_message` — three seams answer it now.
> - **`Ottoman` and `PapalStates` are their own demonym**, so the strategic
>   classifier called them GENERIC and sent the marshal at whichever enemy was
>   nearest — an Austrian, on the boot board. A bare nation name now classifies
>   as a court; plural/adjectival forms ("the Ottomans") stay generic, which is
>   the CR-0 behaviour its pins protect.
> - **Retreat told the player a real nation "is not known to the staff"** and
>   fell back elsewhere. The arm discards the error dict BY DESIGN (a retreat
>   must substitute, never refuse) — it now reads the `nation_named` key and
>   says "that is a nation, not a province".
> - **A1 dead-named a formed court.** Composing finished prose with the static
>   `display_nation` bakes "Kingdom of Italy" into the sentence, after which
>   Godot's raw-tag `formation_overrides` pass can never repair it to "Italy" —
>   the §11.8 stage-3 hazard `NATION_AGENDAS_SPEC.md:490` records as a
>   previously-fixed defect. `ally_entry_block_line` takes an optional `world`
>   and resolves through `formations.formed_display_name`. (This one was a
>   REGRESSION: the pre-A1 line passed the raw tag, which the client repaired.)
> - **A1 made a repeatable event visible.** The declaration review is
>   re-openable and appended an identical `hard_block_surfaced` every time —
>   invisible while the filter branch was dead, but a NEW source of exactly the
>   spam IGR-B exists to cure. Now one line per `(turn, ally, enemy, reason)`.
>
> Twelve findings did not survive refutation, including the tribute-figure and
> "wrong lord" objections to A4 (the reported number IS the applied gold flow)
> and the claim that the cap raise re-duplicates the ally-entry review.
> Final: suite **15,011/3**, eval 461/461, M1–M7 and `BASELINE_SERIES`
> byte-identical, `tests/test_igr_a_honest_copy.py` (71).

| # | Item | Done when |
|---|---|---|
| A1 | **The hard-block vocabulary leaks raw internal keys** — *"Spain cannot join against Prussia: no_participation_path."* **4 live keys, 2 live surfaces** | Every live reason renders as prose on both surfaces; a test enumerates the live producers |
| A2 | **"Political Context:" repeats its own lines verbatim** | The lines appear once; the duplication-asserting pin is consciously flipped |
| A3 | **A nation name typed as a region misresolves** (`Saxony` → *"Did you mean 'Savoy'?"*; `Austria` → Asturias, disclosed but unexplained) | Nation names answer with that nation's own provinces, upstream of both fuzzy ladders |
| A4 | **Releasing a vassal reports nothing** | The message names the tribute lost, the threat drop, the cooldown, and the woken deck |

#### A1 seam — verified, then narrowed by the refuter

`diplomacy.py:5732-5771` appends six hard-block kinds, but **only four are live and only
two surfaces render them**: `at_war_with_<n>` (`:5751`) and `direct_enemy_of_<n>`
(`:5755`) are **structurally unreachable at the only live producer** —
`build_declaration_preview` (`:5945-5960`) enqueues a nation only when its diplomatic
state is `ALLIANCE`/`DEFENSIVE_ALLIANCE`, and `is_at_war` is the *same single dict read*
(`world_state.py:1609-1611`), so one key cannot be both. The `hard_block_surfaced` event
is written from that same loop, so no save can carry them either.

**Live scope: 4 keys** (`armistice_cooldown_with_<n>`, `anti_promiser_coalition_member`,
`hard_reject_posture`, `no_participation_path`) **on 2 surfaces** —
`diplomatic_executor.py:1764/1767` (renders `str(hard_blocks[0])` verbatim) and the
`hard_block_surfaced` arm at `campaign_log.py:1443-1447` (underscore-strips only). A third
site is latent.

**Minimal seam:** one helper `ally_entry_block_line(reason, beneficiary, named_enemy)` in
`display_names.py` returning the *whole* sentence, backed by one module-level template
table, consumed at exactly those two call sites.

> ⚠ **Do NOT register the templates in `_CATEGORY_MAPS`.** `display()`
> (`display_names.py:1236-1239`) returns `display_map.get(name)` verbatim, and every other
> entry there is a finished string — registering *format templates* ships a **new** leak
> (`display("ally_entry_block","no_participation_path")` → `'{ally} cannot reach {enemy}…'`,
> braces straight to the player). **Do not** add a second `…_reason_display()` helper with
> no call sites (GR9), and **do not** edit `DECISION_REASON_DISPLAY["hard_blocked"]` /
> `["participation_blocked"]` — grep shows their only callers are tests.

**Reachability: one click from boot** — `europe_1805.json` authors
`"France|Spain": "ALLIANCE"`, so the first war declaration on a PEACE nation raises it,
which is exactly the path this review walked.

> ⚠ **Display-only — do NOT rename the keys.** `diplomacy.py:6385-6388` branches on the
> literal strings to choose the AI feasibility `decision_reason`; renaming silently
> mis-routes `ai_should_propose_bargain`. `tests/test_wb_c_war_entry.py` pins the
> vocabulary in six places (`:207 :213 :220 :230/:235/:245 :250 :257`). All stay green
> under a display-only change.

#### A2 seam — verified structural, spans the wire

1. `diplomacy.py:2298` `_build_breach_warnings` is the **single correct producer** (four
   texts at `:2312 :2325 :2336 :2343`) and must not change;
2. `diplomatic_executor.py:2083` builds `extra_lines = [w["text"] for w in warnings]` and
   appends them to `warning_text` at `:2096`, **then ships the same list** at `:2107`;
3. `proposal_confirm_popup.gd:1622-1647` prints `talleyrand_text` (which now contains
   them) and then the bullets under `[b]Political Context:[/b]`.

**Fix on the backend side** (drop `:2083` + `:2095-2096`), leaving the popup — the good
surface, which can colour by severity — to own presentation. Same pattern at
`diplomatic_executor.py:890` (break-treaty confirm) and a latent third at
`diplomacy.py:7792-7808` (paradox; its popup does not render `warnings` today).

> ⚠ **v0.1 SAID** the second duplicating surface was the ally-entry popup. **Wrong** —
> the `conflict_alert` dialogue ships no `warnings` key and cannot duplicate. The second
> site is **`force_break_treaty_confirmation`**.
>
> ⚠ **A pin asserts the bug.** `tests/test_playtest_bugfixes.py:250` asserts
> `"Reliability would fall from 0 to -10." in result["message"]`. It **will red** and must
> be **consciously flipped** to assert the text is in `warnings[0]["text"]` and *absent*
> from `message` — that inversion becomes the regression guard.
>
> **Rider:** with the inline copy gone, the popup's `mini(warnings.size(), 2)` cap
> (`proposal_confirm_popup.gd:1631`) would hide half the producer's output. Raise it to 4,
> and route any non-popup surface (headless / mailbox replay) through one
> `warnings_to_plain_text()` helper so the duplication cannot be reintroduced.

#### A3 seam — stays **P3**, and the seam is not where I first put it

Measured against the shipped 1805 world:

```
Saxony  -> None      "Region 'Saxony' not found. Did you mean 'Savoy'?"
Prussia -> None      "Region 'Prussia' not found. Did you mean 'East Prussia'?"
Bavaria -> None      "Region 'Bavaria' not found. Did you mean 'Balearics'?"
Austria -> Asturias  (auto-corrected)
```

> ⚠ **v0.2 SAID** the Austria case is a silent P1. **Refuted — it is not silent.**
> `movement_executor.py:186-203` already discloses:
> *"Ney begins marching to Asturias (distance: 8) … Route: … → Asturias. (Our maps read
> Asturias as the province nearest your order, Sire.)"* The province is named three times
> and the substitution is explicitly flagged; the attack arm is safer still —
> `"Ney, attack Austria"` **refuses** (*"Your order names no foe our maps know, Sire."*).
> This is a **P3 copy-quality gap** — "nearest your order" should say "Austria is a
> nation" — not a correctness defect. **Claim withdrawn.**
>
> ⚠ **v0.2 SAID** fix it at `executor.py:259`. **That is dead code for this case.** The
> parser resolves `"move to Austria"` → `target="Asturias"` *before* the executor, so
> `_fuzzy_match_region("Asturias")` exits at the exact-match return
> (`executor.py:246-248`) and never reaches the proposed pre-check.

**The real seam** is `parser.py:99 _is_nation_demonym` — the function whose own docstring
already names this exact bug class (*"`Austrians` fuzz-matched the Spanish province
`Asturias`"*), already carries the `_VASSAL_ACTIONS` carve-out (`parser.py:622-628`), and
is already wired at `parser.py:636` and `:724`. **Generalise it from demonym forms
(`base+"ian"/"n"`) to the bare nation NAME**, which covers Austria *and*
Saxony/Prussia/Bavaria in one function, upstream of both fuzzy ladders.

Two guards, both required: run it **after** the exact-region check (`Hanover` is both a
nation and a region and must keep resolving exactly), and keep the `_VASSAL_ACTIONS`
exclusion. Then improve the answer to name the nation's provinces via the cached
`world.get_nation_regions()`.

Also clean up the mock parser minting nation names as region targets —
`llm_client.py:1513-1514` (Saxony), `:1483-1484` (Bavaria), `:1520-1521` (Netherlands).

> **Regression gate:** re-run the parser eval harness (`parser_eval.py`, mock arm 433/433)
> and add corpus rows per the 12-step checklist. `tests/test_sweep5_parse_validation.py`
> pins the movement-target passthrough that *feeds* this seam — improve the message at the
> far end; do not re-null the target in `validation.py:396-399`.

#### A4 seam — verified live

`vassal.py:1739-1742` returns a two-key dict. Measured consequences of releasing Kingdom
of Italy, **none of them reported**: the dormant deck **wakes** (`get_active_agenda` None
→ `risorgimento`, watch `2 of 5 provinces held` toward proclaiming Italy); tribute ends
(~**375 g/turn** at boot); coalition threat **85 → 77**; re-vassalization locked **5
turns**; state VASSAL→PEACE; assimilated marshals restored; Continental System dropped.

> ⚠ **v0.1 SAID** release costs "co-belligerency". **False** — release sets only the
> lord–vassal pair to PEACE; Kingdom of Italy stayed at war with Austria afterwards. The
> honest line is **forward-looking**: they will no longer answer your call to arms.
>
> **GR4 hazard:** snapshot tribute / marshals / threat **before** the mutations at
> `vassal.py:1660-1737`. Read the woken agenda **after** `invalidate_active_nations_cache()`
> at `:1674` or you get the stale dormant answer. The same function is the **rebellion**
> path (`rebellion=True`, `:1707-1731`) — the enriched copy must not narrate a voluntary
> release when the vassal revolted.

**Why A4 matters beyond flavour:** releasing Kingdom of Italy is exactly what lights the
`→ forms: Italy` watcher. The game performs its own most interesting causal link in
silence.

### IGR-B — The campaign log becomes readable *(gate Q1)* — ✅ **LANDED July 25, 2026**

> **Landing record — authoritative for what IGR-B actually became.**
> Tests `tests/test_igr_b_campaign_log_readable.py` (46). Suite **15,057**,
> ruff clean, parser eval **461/461** mock, M1–M7 green and the 40-turn
> `BASELINE_SERIES` byte-identical. **No `.gd` diff** (see below); the client
> booted clean (0 `SCRIPT ERROR`) and the collapsed rows were served by the
> real backend over HTTP and put through the client's own text transform.
>
> **The shape, as blessed:** one pure `collapse_refusal_family(events)` in
> `campaign_log.py`, called from the `GET /campaign_log` handler *after*
> `filter_campaign_log`, bucketing by `(turn, proposal_type)`. A bucket of one
> passes through as the *same object*; a bucket of N is one shallow copy of its
> first member carrying display-only `collapsed_count` / `collapsed_pairs`.
> `format_event_oneliner` grew a collapsed arm that renders the aggregate
> sentence, so the count reaches the player through the existing `display`
> string and the client needed no change at all.
>
> **⚠ THE ACCEPTANCE CASE WAS RE-SITED — the burst is turn 3, not turn 9.**
> The spec's raw table `{9:21, 11:7, 12:2, 13:3, 16:21, …}` was read off
> `world.event_log` *after* the run, by which point `MAX_EVENT_LOG_SIZE=500`
> had evicted 342 of 842 events. Those eight turns are individually correct but
> they are precisely the survivors of the cap: the true emission history is
> `{2:8, 3:69, 5:9, 6:3, 9:21, 11:7, 12:2, 13:3, 16:21, 17:7, 18:2, 19:3}`, and
> **the spec's own probe never saw turn 3 — the largest burst in the run, 3.3×
> the wave it named.** Worse, **turn 9's 21 refusals are 100% fog-filtered**
> (0 visible; the branch needs PARTIAL+ on a named party and by mid-run France
> has lost intel on the minors doing the asking), so the "≤5 events" test would
> have passed trivially on a 1-event page. Turn 3 is what reproduces the live
> review's 24/25: **26 visible rows, 23 of them refusals (88.5%)**.
> Also refuted: *"a real game with wider intel sees more survive the fog
> filter"* — the modal outcome for a burst on this run is **zero** survivors.
>
> **Measured result (live page, the frame the review observed):**
>
> | turn | rows before → after | refusals before → after | `agenda_shift` index |
> |---|---|---|---|
> | 2 | 6 → **1** | 6 → 1 | – |
> | **3 (the burst)** | **26 → 5** | **23 → 2** | **25 → 4** |
> | 5 | 2 → 1 | 2 → 1 | – |
> | 6 | 6 → 4 | 3 → 1 | 5 → 3 |
> | 12 | 4 → 3 | 2 → 1 | 3 → 2 |
> | 13 | 8 → 7 | 2 → 1 | – |
>
> **⚠ Two P1 hazards found by verifying the spec against master, both
> reproduced by hand before any code was written:**
>
> 1. **The bare `(turn, proposal_type)` key would have deleted the player's own
>    diplomacy.** It is *not* unique to refusals: `diplomatic_proposal_sent`,
>    `proposal_arrived` and `offer_lapsed` all carry a `proposal_type` from the
>    same vocabulary and all take an "always show" branch. Reproduced: a bucket
>    of `{diplomatic_proposal_sent, offer_lapsed}` sharing
>    `(3, "non_aggression")` collapsed to one row and destroyed the other — and
>    `offer_lapsed` was measured live **on turn 3, the burst turn itself**. The
>    function gates on `type` first; four tests pin it.
> 2. **In-place stamping would have corrupted every save.**
>    `filter_campaign_log` returns *originals, not copies* (its own docstring
>    says so) — the very dicts in `world.event_log`, which `to_dict` serializes
>    via `[e.copy() for e in …]`. `collapsed_count` written in place would ride
>    into the save file permanently. Hence `dict(event)`; pinned by asserting
>    `world.event_log` is element-identical and the save string contains no
>    `collapsed_*` after a `GET /campaign_log`.
>
> **The sentence** never emits a bare count when it can name the courts, and
> always accounts for every approach — either by naming all of them or by
> stating the true number. The rule is *lose nothing first, then rank by
> frequency, then count*:
>
> | shape | sentence |
> |---|---|
> | one court against a short list | `Britain rebuffs Baden, Hesse and Saxony` |
> | one court against a crowd | `9 courts rebuff Prussia` |
> | a short list on either side | `22 approaches from Prussia and Bavaria are rebuffed` |
> | crowded, but one or two courts carry ≥60% | `16 approaches rebuffed, chiefly from Prussia` |
> | genuinely diffuse | `16 approaches rebuffed among the courts` |
>
> **The frequency arm exists because the post-review pass measured the real
> shape and it is heavy-tailed, not flat:** one live page was
> `{Prussia 10, Austria 4, Denmark 1, Bavaria 1}` — four distinct askers, so
> branching on *cardinality alone* fell through to the anonymous arm and
> deleted "Prussia knocked on ten doors and was turned away at every one",
> which is the whole story, because two minors each asked once. It was also
> non-monotonic: since fog is re-evaluated at view time, the bucket gains
> members as the player's intelligence improves, so learning more made the
> sentence say less. `collapsed_pairs` already carried the multiplicity;
> only the uniquing threw it away. Pinned by
> `test_naming_is_monotonic_as_fog_lifts`.
>
> Raw nation tags are preserved deliberately — the client repairs them through
> `Utils.humanize_nation_keys_in_text`, and the NA-6 formation overrides can
> only rename a still-raw tag; baking `display_nation` prose here is the §11.8
> stage-3 dead-name hazard IGR-A hit. **Verified by executing the client's own
> transform headlessly** on the real emitted strings: `PapalStates` →
> *Papal States*, `KingdomOfItaly` → *Kingdom of Italy*.
>
> **⚠ Four further spec claims corrected.** (a) "~60 test call sites" for
> `filter_campaign_log` — it is **51**. (b) The category cites are `306`/`344`,
> not 305/343 (the substantive point stands and Q1(b) is correctly struck).
> (c) The rung is not only Trigger 5: emission site 2 is fed by **seven**
> trigger returns, and turn 3's mega-burst is 47 `open_borders` (Trigger 4) +
> 22 `defensive_alliance` — only the latter repeats on the 6-turn dedupe
> period. The O(n²) driver is the pair loop, not any single trigger. (d) The
> stated reason for preferring `(turn, proposal_type)` over
> `(proposer, proposal_type)` overstates the alternative's failure: the
> *visible* burst page carries **2–5** distinct proposers depending on how
> much the player has seen, not ~10. The decision is still right (23 → 2, and
> it degrades to the number of types, measured max 2).
>
> **DECIDED — the turn header counts collapsed rows, and stays that way.**
> `campaign_log.gd` renders `events.size()` under the word "event(s)", so a
> burst turn's header reads *"Turn 3 — 5 events"* where it used to read 26.
> The review's refuters split on this. It stays because the header has always
> meant *rows in this block* and still does — expanding shows exactly that
> many rows — the collapsed row itself states the true number one line below,
> and gate Q1(a) bought "no Godot diff" with precisely this behaviour while
> the Done-when *is* the shrunken page. Reversing it is a ~4-line `.gd`
> change (sum `collapsed_count`, append "(N approaches)") and forfeits only
> the no-Godot-diff property.
>
> **No Godot diff, deliberately.** `campaign_log.gd` reads exactly two fields,
> `category` and `display`, and has **zero** automated coverage — it is absent
> from `tools/godot_parse_check.gd` and from every pytest. Composing the
> sentence backend-side keeps the client untouched, which is what gate Q1(a)'s
> "no Godot diff" promised. The turn header's `events.size()` now reads the
> collapsed count by construction — that *is* the fix, and the sentence carries
> the number so nothing vanishes unannounced.
>
> **Post-landing adversarial review (59 agents, 6 lenses → 2 refuters each) —
> 26 raw findings, 20 survived, 8 fixed.** Every fix was reproduced by hand
> before being accepted; the frequency cliff and the blind pin were measured
> directly rather than taken on the reviewers' word.
>
> - **Four of my own tests were vacuous or inert, and I proved each one.**
>   `test_world_event_log_survives_the_whole_view_pipeline` used a hand-rolled
>   pair that the fog filter reduced to ONE, so **nothing collapsed** and the
>   save-corruption gate ran over a pipeline that never took the copy path.
>   Both AI-3 pins compared `[False]×N` to `[False]×N` on a world whose
>   `diplomatic_refusals` was `{}` — they now seed the record to a climbed
>   state and assert `any(before)` first. `test_collapsed_pairs_is_a_fresh_list`
>   appended to a list then asserted a *key* was absent, which `list.append`
>   cannot change; it now mutates a nested dict THROUGH the output and diffs
>   the input against a deep snapshot — the real aliasing gate.
>   `test_the_count_is_always_stated` asserted only that some digit existed,
>   which any wrong number satisfies; it is now
>   `test_every_arm_accounts_for_every_approach` and checks the actual integer
>   with a word-boundary match across all eight arms.
> - **Nothing pinned that the collapse runs AFTER the fog filter** — a reorder
>   would leak fogged courts into `collapsed_pairs` and into the sentence, and
>   passed 36/36. Now pinned by injecting a deliberately-fogged pair and
>   asserting neither court appears anywhere in the payload.
> - **The naming cliff** (above) — the headline, still live after my first
>   post-review patch.
> - **A short bucket now loses nothing.** One asker refused by three courts
>   rendered as "3 courts rebuff Prussia": one row saved, three names thrown
>   away. When one side is a single court and the other is short enough to
>   list, every name from the uncollapsed rows survives into the aggregate.
> - **Drive-by, pre-existing, found by the review and fixed here: 4 of the 7
>   arms of the NA-6 dead-name pin were non-binding.**
>   `test_get_endpoints_carry_the_overrides_too` sliced a fixed 2400 characters
>   after each route decorator, which overshoots four of the seven bodies into
>   the NEXT endpoint — whose own `_attach_nation_identity_overrides` satisfied
>   the assertion. **Deleting the call from `/campaign_log`, `/dispatch`,
>   `/marshal_overview` or `/status` left the pin green.** Verified by mutating
>   each call out in turn: 3/7 caught before, **7/7 after**. The scrape is now
>   bounded by the next route decorator (`_endpoint_body`), which also retires
>   the headroom bookkeeping this slice would otherwise have inherited.
> - **`collapse_refusal_family` silently returned `[]` for any non-list
>   iterable**, against its own annotation. One `list(events)`.
>
> Recorded as notes rather than fixed, each because the producer and the gate
> together make them unreachable: `design_ask` collapses under the same rule
> (0 emitted in 40 ambient turns across 4 seeds, and a bucket of one already
> passes through intact); branches 1–2 state the distinct-court count rather
> than the bucket size (needs a duplicate ordered pair, which
> `REFUSAL_DEDUPE_TURNS=6` forbids); the collapsed row keeps its anchor
> member's scalar keys (the documented summary shape); and `Ottoman` renders
> without "Empire" — a pre-existing house-wide divergence shared with
> `diplomatic_ai_ai_treaty`, which this slice *reduces* rather than introduces.
>
> **The residual stands, unfolded:** `MAX_EVENT_LOG_SIZE=500` eviction is
> producer-side and worse than the spec stated — **342 of 842 events (41%) are
> evicted by turn 21 on a zero-action run**, 90 of the 156 refusals among them.
> Not touched here, correctly: the honest lever changes `get_refused_asks`
> cardinality and therefore AI-3. Owner: its own gate (§4).

**Measured, deterministically** (20 ambient turns, `historical`, zero player actions):
19 enemy nations → **171 pairs scanned per turn**; raw emissions
`{turn 9: 21, 11: 7, 12: 2, 13: 3, 16: 21, 17: 7, 18: 2, 19: 3}` — **the wave repeats on
the ~6-turn dedupe period; it is standing, not a one-off.** Player-visible shares 48% /
57% / **63%**. This matches the live 24/25 closely, and a real game with wider intel sees
*more* survive the fog filter, not fewer.

The rung is `_evaluate_ai_ai_proposal` **Trigger 5, preemptive alliance**
(`ai_diplomacy.py:2888-2904`), gated on `threat_level > 40` — boot threat is 85, so the
instant minors' relations with France go negative it fires for every minor pair at once
(O(n²)). Refusals are **explicitly excluded** from the anti-spam counter
(`ai_diplomacy.py:2649`).

**Hard constraint:** the record is AI-3's ladder-gate substrate
(`war_council.py:500-508` reads `get_refused_asks`, threshold 2). **View-layer only.**

**✅ Gate Q1 DECIDED (§5): aggregate at the view layer, keyed `(turn, proposal_type)`.**

Shape: a new pure `collapse_refusal_family(events)` in `campaign_log.py`,
called from `main.py:2861` **after** `filter_campaign_log`, bucketing by
**`(turn, proposal_type)`**; a bucket of 1 passes through byte-identical, a bucket of N
emits one shallow copy at the **first** member's index carrying display-only
`collapsed_count` / `collapsed_pairs`.

> ⚠ **v0.1 SAID** key on `(proposer, proposal_type)`. **Measured insufficient** — a burst
> turn carries ~10 distinct proposers, so 21 lines become ~10, still most of the page.
> `(turn, proposal_type)` takes 21 → 1 and degrades gracefully (3 types → 3 lines).
>
> ⚠ **The per-category filter option is not merely weaker — it is wrong.** The buried
> dramatic line is `agenda_shift`, which is **also category "diplomacy"**
> (`campaign_log.py:305` vs `:343`), same glyph and colour. Any category filter hides the
> signal with the noise. Gate Q1 option (b) is struck accordingly.
>
> **The main implementation trap:** do **not** put the collapse inside
> `filter_campaign_log` — ~60 test call sites depend on that contract.
>
> **Residual, stated rather than hidden:** this does not relieve `MAX_EVENT_LOG_SIZE=500`
> eviction (`world_state.py:1914`), which is producer-side. The honest lever is a per-pair
> refusal cooldown, but that changes `get_refused_asks` cardinality and therefore AI-3 —
> it needs its own gate and must **not** be folded in here.

Done when: the measured worst case (turn 9) drops from ~25 events to ≤5 with the
`agenda_shift` visible without scrolling; `world.diplomatic_refusals`, `len(event_log)`
and `_ladder_climbed` are provably unchanged; `CAMPAIGN_LOG_TYPES == 140` still holds (no
new type).

### ~~IGR-C — Talleyrand's counsel rung~~ — **WITHDRAWN by the v0.3 refuter**

**This slice is struck, and so is gate Q3.** The refutation is decisive on three legs;
recording it here because the *observation* was right and only the conclusion was wrong.

1. **It is not a GR9 orphan.** §2.5-4 is the **third** surface of the exposure mechanic.
   The other two render on the shipped boot and I *saw both myself* during the review —
   `_build_france_exposure` ("The Emperor's Own Exposure") and `_build_exposure_line`
   (the per-court rows), both **PASS** on the must-see checklist. And the AI-vs-AI silence
   is already written into the blessed spec at `AI_WAR_DECISION_SPEC.md:444-458` (§8.2-1)
   with an owner, a landing slice and a tracking line: **AI-V arm (a)**. GR9 is satisfied.
2. **The proposed broadening delivers nothing in a real campaign.** Instrumenting the
   hegemon over 40 turns: the broadened rule renders **37 rows — but 0 of them while
   France is still the hegemon.** Every row is a `contain_hegemon` design, and
   `intent.py:226-229` derives its `against` from the hegemon, so under D3 a played France
   that stays the largest bloc keeps those designs pointed at the *player*, where both the
   old and new rules drop them. The "0 → ~34" headline was measured in the collapse case.
3. **It would ship incoherent copy.** The single most frequent row (25/37) renders
   Sweden's authored anti-Napoleon design — `scourge_of_the_usurper`, *"Gustav IV's
   personal anti-Napoleon zeal"* — as a design held in check **against Britain**. The
   `exposed`-only gate is currently what keeps that off screen.

**Disposition:** no work here. The rung's silence stays owned by AI-V arm (a).

<details><summary>The original (withdrawn) proposal, kept for the record</summary>

**Measured:** `exposed` occurred **0 times in 253 AI-vs-AI design-pair readings** across
3 seeds × 40 turns. Histogram (historical, 146 readings): `None` 37 / `penniless` 3 /
**`outmatched` 72** / `busy` 34. Gate (5) *is* satisfiable — 48 readings reached
`price=="fight"` — so the failure is entirely gate (6).

**The structural reason** (this is the finding): the 1805 content produces two kinds of
AI-vs-AI target and the exposure band sits in the gap. `deny`/`contain` designs derive
`against` = the hegemon, so T ≫ own and `outmatched` fires *before* the exposure check;
the only acquire pairs point at army-less minors (Hanover standing 0 permanently), so the
gate returns `None`. It is **content-unreachable**, not arithmetically dead — a
constructed Tilsit world does read `exposed` at 40k–56k Austrian strength.

Recommended shape: **broaden from "exposed only" to "any live restraint, named
honestly"** — `:493` changes from `!= "exposed" → continue` to `is None → continue`, and
each cause gets its own sentence (exposed keeps its pinned wording verbatim;
outmatched → *"X means to {design}, Sire, and has not the army for it."*; penniless →
*"the treasury will not bear a campaign"*; busy optional). **Measured effect: 0 → ~34
rendered rows** on historical (Sweden→Austria at the fight rung, turns 8–41). Boot stays
`[]`, so the D3 pin holds.

> ⚠ **v0.1 SAID** broaden to "France's own designs held in check". **Not buildable** —
> France has **no agenda deck** in `europe_1805.json` (`get_nation_intent("France")` →
> `want_id=None`), so there is no French design to hold in check; and France's exposure is
> already surfaced by `diplomatic_ledger._build_france_exposure`. Gate Q3 option (a) is
> replaced accordingly.
>
> ⚠ **v0.1 SAID** Austria "short-circuits on `busy`". **Wrong** — Austria's
> `redeem_italy` targets *France*, so it is dropped by the player-target filter at
> `diplomatic_advisory.py:487-488` and the restraint reason is never consulted. This
> matters: a fix premised on "let busy courts through" would not move Austria an inch.
>
> ⚠ **Copy-table trap (highest risk).** `war_council._SOFT_BLOCK_CAUSE` maps
> `busy → "starved"`. Reusing it would render *"the moment passed — opportunism decayed"*
> for a court blocked by `busy`/`outmatched` — reproducing the exact §0.3 lie AI-3r was
> built to kill, in a **new** surface. Add a separate phrase table keyed on
> `_restraint_block_reason`'s four outputs, beside `crisis_cause_phrase` (the same
> single-source discipline `bdeb17c` installed).
>
> **Do not open the player-target filter** at `:487-488` — that instantly reds
> `test_talleyrand_skips_player_directed_designs` and reopens a D3-flavoured decision.

</details>

### IGR-D — The carve becomes completable *(gate Q2)* — ✅ **LANDED July 25, 2026**

> **Landing record — authoritative for what IGR-D actually became.**
> Tests `tests/test_igr_d_carve_completable.py` (49). Suite **15,107/3**, ruff clean,
> parser eval **461/461** mock, M1–M7 and the 40-turn `BASELINE_SERIES` byte-identical,
> Godot parse harness EXIT=0, headless boot 0 `SCRIPT ERROR`.
>
> **Arm A — `create_client` carries.** Five seams, in order of the clause's journey:
> `PAIR_SUBSTITUTE_CARRIED_TYPES` gains the type (and it leaves
> `_PAIR_SUBSTITUTE_DROPPED_LABELS`, which would otherwise be a *new* lie);
> `_pair_substitute_seed_terms` grows a literal `ttype == "create_client"` arm emitting a
> **demand** carrying `tag` / `provinces` / `client_display_name`; `_ratify_treaty`'s
> demand→clause allowlist widens by those three keys; and a new arm in `_ratify_treaty`
> re-validates through `evaluate_create_client_eligibility` and applies.
>
> **The apply body was EXTRACTED, not copied.** `formations.apply_create_client_clause`
> now holds what was inline in `settlement_ratify`, and both routes call it. That body is
> the entire NA-6c §20.1 review — the live re-read, the already-active-tag refusal, the
> four-condition elimination gate — and a second hand-written arm would have had to
> re-earn every one of them. The settlement path is byte-identical.
>
> **Why it must ride `demands` and not `clauses`.** `_ratify_treaty` builds its clause
> list from `sweeteners` + `demands` **only**; `proposal["clauses"]` is read exactly once,
> as a bare `"open_borders" in …` string test. Seeded into `clauses` the carve would
> price, annotate, warn about estates, ratify into the treaty record — and apply nothing,
> reproducing this slice's own defect one layer down. It is also what satisfies **G4F-15
> for free**: the armistice arm empties `seed["demands"]` wholesale, so a truce still
> cannot erect a client state.
>
> **Four defects found in passing, none of which the spec named, all fixed:**
> - **The counter-offer amputated the carve every time.** `generate_counter_offer`
>   deep-copies the *player's own* proposal and deletes whichever element raises
>   acceptance most; a carve is by construction the most expensive line in any package
>   (measured **+35** removal impact against +12 for a 300g demand), and the counter's
>   summary never said so. The most common non-accept outcome silently returned a gold
>   treaty to a player who believed they had erected the Duchy of Warsaw. `create_client`
>   is now exempt from the strike list — a court that will not stomach dismemberment must
>   refuse, not quietly re-draft.
> - **The ratification summary omitted the client.** `applied_treaty_clauses` is a
>   *second* list and it is what `build_peace_ratification_summary` renders as "what was
>   actually signed".
> - **A carve-only Tilsit logged as a `white_peace`** — France dismembers Prussia and the
>   campaign log records that nothing happened. Both outcome classifiers (`_ratify_treaty`
>   and `build_peace_ratification_summary`) now count it, without inflating
>   `territory_gained`: the soil goes to the new client, not to France.
> - **A THIRD harshness dialect.** `diplomatic_defiance.calculate_proposal_harshness`
>   scored a carve at 0.0, so a peace that dismembered its target fell into the
>   "< 0.3 = too generous" arm and Talleyrand bolted a perpetual **50 g/turn** tribute
>   onto it that the player never authored.
>
> **ES-7 held.** `_enrich_proposal_summary` still carried its pre-NA-6c
> `!= "territory_cede"` guard and scanned only `sweeteners`+`clauses`, so a carve stripped
> a marshal's estate with no warning on the surface the player confirms on. It now uses
> the shared `cession_shaped_regions` extractor plus a demands pass **scoped to
> `create_client`** — a `territory_cede` demand *acquires* land, and warning on it would
> tell the player that taking a province strips his own marshal's estate.
>
> **⚠ THE PRICE WAS RETUNED AFTER MEASUREMENT, and the first cut would have shipped the
> defect in a new shape.** The real defect was **saturation**: a carve's whole cost lived
> in `harshness_penalty`, which clamps at 1.0 and caps at −40, so measured on master,
> adding a carve to any realistic Tilsit package moved the acceptance score by **exactly
> zero** — a second carve, or a third, also moved it by zero. The fix belongs on
> `deal_balance`, which does not saturate. My first number mirrored the harshness dialect
> at its ×50 identity ratio (−15/province − 7.5) and **measured out at 40 against the bar
> of 50 for a victor holding ALL of Prussia** — i.e. it made the marquee clause
> unreachable on the very route this slice exists to open. Re-derived at **−5/province
> (the table's own `territory_cede` rate) − 2.5 (half a province, the same 0.15-to-0.30
> ratio the harshness dialect uses)**: a victor holding all of Prussia lands at **54**
> (carves), one holding only Posen at **34** (does not). Blessed, in-band tunable, pinned
> by a falsifiable two-sided acceptance test.
>
> **Arm B — the rest disable the route with their reason.** New
> `pair_substitute_settlement_tier_block` reads the *same* `PAIR_SUBSTITUTE_CARRIED_TYPES`
> the carry arm does, so the two halves of the split cannot drift. It is computed at the
> option builder (where `staged_terms_for_gate` is in scope) rather than inside
> `evaluate_pair_peace_substitute_eligibility`, which takes only
> `(world, war_id, actor, target, action)` and cannot see the draft — that also avoids
> mis-filing a draft-shaped refusal into a closed taxonomy pinned by exact equality.
> **Zero new refusal codes, and zero new Godot machinery**: the `available: False` +
> `disabled_reason_display` shape is already rendered twice by
> `proposal_confirm_popup.gd` (dimmed+tooltipped button, and a "Not available now" body
> line). **Scoped to the PEACE arm** — G4F-15 already rules a truce carries concessions
> only, so losing a demand there is the stated contract, and disabling it too would leave
> a blocked player no exit.
>
> **The carry promise had THREE producers and only one was honest.** The backend
> description (fixed July 25), `proposal_confirm_popup.gd:1219` — which hardcoded
> *"Your drafted terms for X carry into the talks"* in **body text**, so the honest
> sentence only ever reached a hover tooltip — and Talleyrand's own voice line, which
> guaranteed *"Your drafted terms travel with me."* All three now defer to one
> backend-composed `carry_line`, which is additionally **arm-aware**: the armistice
> chooser stops promising a carry it drops.
>
> **THE PAYOFF (user-directed: "make the payoff for forming duchy good as well").**
> Measured on master, carving the Duchy of Warsaw was close to pure cost. The client was
> born at `CARVE_LOYALTY = 30` — **five points below `CONTRIBUTION_DISAFFECTED_BELOW`** —
> so from its first turn it refused every call to arms, was immediately eligible for an
> enemy bribe, and, with **no France↔client relation seeded at all**, nothing offset the
> −2 satellite drift: it reached open rebellion against its own creator in fifteen turns.
> Talleyrand's pitch for the clause promises *"a friend that costs us nothing to
> garrison"*. Two constants, both using the drift system's own existing levers rather
> than exempting the carve from them:
> - **`CARVE_LOYALTY` 30 → 60** (`CONTRIBUTION_LOYAL_MIN`) — the state you conjured out of
>   a conquest fights for you, which is the only reason to prefer a carve to an
>   annexation, and what the Duchy of Warsaw actually did.
> - **`CARVE_PATRON_RELATION = 40`** — seeded once, never laundered on a re-carve.
>   `40 // 20 = +2` exactly cancels the satellite drift, so a well-treated client is
>   **stable rather than a countdown**; it still slides the moment relations sour, climbs
>   when garrisoned or subsidised, and — because relations outlive vassalage — a client
>   later released to proclaim Poland stays France's friend, which is the one credit entry
>   against §11.9's partition fury.
>
> The Proclamation card now states the bargain (*"it marches when France calls, and pays
> tribute"*) rather than only the dependence, and `get_formation_watch` keeps showing the
> dormant Poland dream with `blocked_by_vassalage` — legible without becoming a promise
> the poll cannot keep.
>
> ---
>
> **✅ MUST-SEE #4 IS CLOSED — the Proclamation was sighted in-client**, screenshot
> `docs/audits/IGR_D_PROCLAMATION_2026_07_25.png`: the real Godot client, the real backend,
> the carve carried into a bilateral peace with Prussia alone, ratified on the end-turn
> tick. *A NATION IS PROCLAIMED / Duchy of Warsaw … it answers to France as a satellite
> (loyalty 60) · it marches when France calls, and pays tribute … By your hand.* Live
> `/formables` afterwards states the C→T chain honestly: *"forms when a free Duchy of
> Warsaw holds all 2 of its claimed provinces"* + *"currently a vassal of France"*.
>
> **Post-landing adversarial review (8 lenses → 2 refuters each, 39 agents) — every
> surviving finding reproduced by hand before it was accepted. 5 production defects and
> 10 test defects fixed; a 10-mutation sweep now catches 10/10.**
>
> The headline is that **the slice re-committed its own defect one surface downstream**:
> `terms_ratified` was annotated from the *submitted* proposal, so a carve the new
> eligibility gate correctly REFUSED at ratification still told the player *"France erects
> Duchy of Warsaw (Posen) out of Prussia"* over a treaty that erected nothing. Not a corner
> case — a full turn passes in transit, and this slice's own live probing hit the refusal
> twice (Prussia retook Posen once; **Russia walked into it** the next time). The summary
> now reconciles against `applied_treaty_clauses` **and names the loss** rather than merely
> omitting it.
>
> - **`subjugation` was in NEITHER set** — not carried, not labelled — so the bilateral
>   route threw it away in total silence. And the guard test could not see it: it iterated
>   the very dict the type was missing from. The replacement walks
>   `_DEMAND_ADDABLE_CLAUSE_TYPES` — what the authoring surface can actually produce.
> - **The split reopened the hole it closed for one case.** Moving `create_client` into the
>   carried set deleted its dropped-label row, but the seed only carries a carve whose
>   CARVER is the proposer — so an *ally-beneficiary* carve became the one clause dropped
>   with no word at all, under a chooser promising a clean carry.
> - **The armistice arm stopped naming what it abandons** (my early return skipped the
>   `dropped` computation) — and arm B funnels a blocked player onto exactly that arm.
> - **Talleyrand still called a dismemberment "too generous"** on the slice's OWN blessed
>   package: the carve's 0.35 minus the unconditional −0.1 per sweetener = 0.25, under the
>   0.3 bar, so the measured-acceptable Tilsit got an unauthored 50 g/turn tribute bolted
>   on. Now floored by a named `TOO_GENEROUS_HARSHNESS`.
> - **Ten of my own tests were vacuous or inert**, each proven by mutating the production
>   code and watching the test stay green: the counter-offer fix had **zero** coverage (the
>   fixture left `nation_dp` empty, so `generate_counter_offer` returned None and the test
>   asserted nothing); the landless-court test was refused by the annexation gate before
>   the elimination guard it names was ever reached; `TestG4F15StandsUntouched`
>   hand-rolled `dict(seed, demands=[])` and asserted nothing was in `[]` — a tautology;
>   **arm B's entire coverage was `inspect.getsource` substring matching that already
>   passed on master**; the eligibility re-check was indistinguishable from the pre-existing
>   live control re-read; and the pricing walk was never called by the test named for it.
> - **A real test-isolation bug found in passing:** the E2E delivery test leaked
>   `main.world` / `game_state`, and — separately — the counter-offer assertion is
>   order-sensitive (it catches its mutation alone but not after the E2E test). Both are
>   recorded; the counter fix now also carries a source pin that ambient state cannot fool.
>
> **⚠ Residual, stated not hidden: bilateral peace with a BOOT enemy is unreachable, and
> that is pre-existing.** `_ratify_treaty` applies a player-only relation floor
> (`STATE_RELATION_REQUIREMENTS["PEACE"] = -60`); France boots at −95/−100/−95 with
> Austria/Britain/Russia and relation decay explicitly skips WAR and ARMISTICE. Measured:
> a player-declared war on Prussia lands at −40, so **the reviewed case — and Tilsit —
> works**, while the three boot enemies keep the documented armistice-first route and the
> joint settlement. Not widened here: the floor re-prices every bilateral peace in the
> game and is a design gate of its own.

Unchanged from v0.1 and re-affirmed. I reached every prerequisite by real play (at war
with Prussia, Posen held and secured, gate green, clause authored) and neither route
completes: the **joint** settlement needs all four courts at 50 (they sat at −31, −24,
−18, −34); the **bilateral** route the game itself offers drops identity clauses by
design. **The Proclamation card has never been sighted in-client.**

**The historical argument (Q2 option a):** the Duchy of Warsaw was created at **Tilsit —
a separate peace with Prussia alone, while the war with Britain continued.** That is
precisely the case the engine forbids. Carving from one defeated court while other wars
run is not an edge case; it is the canonical instance of the feature.

**✅ Gate Q2 DECIDED as a split (§5):** `create_client` **carries** into the
pair-substitute peace; vassalage / liberation / forced-alliance stay settlement-tier and
the bilateral route is **disabled with a stated reason** when the draft holds one. The
G4F-15 armistice ruling stands — a truce never erects a client state.

Done when **both** arms hold: (1) a player who has beaten one court can carve from it alone,
the Proclamation fires, and must-see #4 closes with an **in-client screenshot**; (2) a draft
holding a settlement-tier identity clause shows the bilateral route disabled with its
reason, and a test pins that no identity clause is ever dropped silently again.

### IGR-E — Plunder earns its prompt *(gate Q4 — needs a blessed number)*

Plundering Nassau yielded **87 gold** against 3,085/turn income and a 5,177g treasury.
Secure was strictly correct in every situation met, so a modal that stops the game asks a
question with one right answer.

**✅ Gate Q4 DECIDED (§5): `PLUNDER_INCOME_MULTIPLIER = 4`** — blessed, in-band tunable.
Done when the falsifiable test in §5 Q4 passes: a poor early player plausibly plunders, a
rich late one does not.

### IGR-F — The small courts write one letter, not five *(no gate)* — ✅ **LANDED July 26, 2026**

> **Landing record — authoritative for what IGR-F actually became.**
> Tests `tests/test_igr_f_envoy_digest.py` (83). Suite **15,201/3**, ruff clean,
> parser eval **461/461** mock, M1–M7 and the 40-turn `BASELINE_SERIES`
> byte-identical, Godot parse harness EXIT=0 (17/17), headless boot 0 `SCRIPT ERROR`.
> A 20-mutation sweep catches **20/20** — two of my own tests were inert on the
> first pass and are recorded below.
>
> **The shape: the letter-book.** One pure `build_envoy_digest(world)` in the new
> `backend/game_logic/envoy_digest.py`, derived from the dialogue manager on every
> response and carried on the base envelope beside `pending_envoy_count`. The
> surface is the EXISTING `mailbox_panel.gd` (CanvasLayer 119) with per-row
> Accept/Decline buttons and the court's spoken line — **no PopupQueue slot** (the
> 11-key pin holds), **no campaign-log type** (140 holds), **no new dialogue dtype**
> (so none of the three Godot registration surfaces move). Answering is one new
> endpoint, `POST /mailbox/respond`.
>
> **⚠ THE PREDICATE IS NOT THE ONE THE SPEC IMPLIED — twice over.**
> - **`tier == "minor"` is wrong.** Reis Efendi is the **Ottoman** diplomat
>   (`diplomat.py:159`) and the Ottoman is authored **`secondary`**
>   (`nation_config.py:73`). A minor-only predicate would have left untouched one of
>   the two voice lines the review named as being flattened. It is `!= "major"`,
>   spelled `in ("minor", "secondary")` to match the existing `ai_diplomacy` idiom.
>   **Recorded divergence:** `diplomatic_ledger.py:342` uses `== "minor"` for vassal
>   eligibility, which puts the Ottoman on the great-power side. Different questions;
>   do not "fix" one to match the other.
> - **Tier alone is not enough at all.** A minor court suing for peace arrives on the
>   *identical* `incoming_proposal` dtype as its open-borders request. The predicate
>   is a conjunction with a POSITIVE type allowlist
>   `{open_borders, non_aggression, friendly_gift}` — never a denylist, which would
>   silently admit every future P-rung label. `opportunistic` is EXCLUDED: it reads as
>   a non-aggression pact but demands 100 g/turn in perpetuity.
> - **And it must key on `context["proposal_type"]`, never `terms["type"]`.**
>   `_build_proposal_terms` deliberately rewrites the terms type, so a digest keyed
>   there would batch a `design_purchase` province cession and a `sell_neutrality`
>   compact as routine mail. Pinned.
>
> **⚠ THE SPEC'S "3–5 per turn" IS NOT WHAT THE BOARD DOES.** Measured over 20–25
> ambient turns on the shipped `europe_1805` (two independent harnesses):
> **the maximum routine small-court deliveries in any single turn is 2**, in every run
> — `MAX_BANDWAGON_PER_TURN = 2` binds. The real measured shape is a **relentless
> 2-per-turn drip from the same seven small courts on 9–16 of 20 turns**. It is not a
> ceiling (`shared_enemy_survival` / `unknown_baseline` reasons are uncapped, and four
> non-major courts carry one at boot), and there is **suppressed demand behind it**:
> 11 of 41 generated proposals were silently discarded by the throttle, 100%
> minor-tier. So the acceptance case is sited at 2 and the 3+ case is covered
> synthetically — an acceptance test demanding ≥3 on an arbitrary turn would be
> flaky and, on the pinned run, false.
>
> **⚠ A PRE-EXISTING P1 FIXED IN PASSING, reproduced by hand before it was accepted.**
> `deliver_ai_proposal` wrote `world.incoming_proposal_popup` UNCONDITIONALLY while
> `push` makes only the FIRST arrival current — so on any multi-proposal turn the
> client rendered the LAST letter and its id-bound answer hit the W6-0 stale guard.
> Measured: three letters delivered, the response carried PapalStates (dialogue_id 3),
> the active dialogue was Bavaria (dialogue_id 1), Accept came back *"another matter
> has arrived since"*. **The multi-court surface this slice exists to fix was already
> unanswerable.** The slot now mirrors the active dialogue.
>
> **The seam that actually produces the storm is the SAFETY VALVE**
> (`main.py:837-854`), not the popup queue: it re-derives a modal from the active
> dialogue on *every* response cycle until answered — which is literally "interrupts
> a command in flight". Suppressing the slot alone does nothing. `pop()`/`_promote()`
> are deliberately untouched (four order pins depend on them).
>
> **⚠ THE DIGEST IS NOT A `_post_hud_response_routes` ENTRY, and that is the whole
> reason it works.** Every entry there returns from `_on_command_result` BEFORE
> `_display_result` — so routing the letter-book would have swallowed the output of
> whatever command the player had just typed, replacing a storm of modals with a
> surface that eats your orders. It follows the NA-6b discipline instead: stashed on
> arrival, raised only from `_return_control_to_player` / the `_on_command_result`
> tail, behind the Proclamation; latched per turn (derived fresh every response, so
> without the latch a closed panel re-opens on the next one — an infinite modal);
> and blanked on the `enemy_phase` response so the end-turn report is read first.
> `_on_mailbox_panel_closed` now hands control back, and every non-opening branch of
> `_on_mailbox_list_result` does too — a raised-but-never-opened digest would
> otherwise leave the terminal locked with nothing on screen to unlock it.
>
> **Per-row Accept is legal only because the endpoint activates server-side.**
> `handle_diplomatic_dialogue_response` refuses any `dialogue_id` that is not the
> current top, and queued rows are reachable only through `activate_mailbox_item`.
> Doing that in two client calls would re-open the very race the W6-0 binding
> forbids. `POST /mailbox/respond` resolves the id from the `mailbox_id` the player
> clicked, so the binding holds by construction. The endpoint is **scoped to rows the
> letter-book owns** — it can never become a way to accept a consequential treaty
> with one unconsidered click.
>
> **Answering N letters raises no result modals.** Three accepts would otherwise
> raise three `proposal_result` popups — the same storm one surface downstream. The
> outcome rides the response `message` and is printed inline.
>
> **Two of my own tests were inert and both are fixed** (proven by mutation):
> `test_answering_raises_no_result_modal` passed under a mutation that ignored the
> suppression flag, because the demotion failsafe nulled the popup anyway — it now
> also asserts `digest_row_result is None`, which is what distinguishes them; and
> `test_an_unknown_row_is_refused_honestly` could not tell a vanished letter from a
> too-weighty one, since both refusals set `digest_row_failed` — it now pins the
> message. **A drive-by fix rides along:** `test_nation_agendas_formables.py:1310`
> scraped a fixed 200 characters after `_on_proclamation_dismissed` and de-bound the
> moment another control-returning branch was added ahead of the re-enable — the same
> false-satisfy shape IGR-B's review found in the NA-6 dead-name pin. Now bounded by
> the next function.
>
> ---
>
> **✅ VERIFIED LIVE IN THE CLIENT** (spec §3 requires it for IGR-F specifically) —
> screenshot `docs/audits/IGR_F_LETTER_BOOK_2026_07_26.png`. Real Godot client, real
> backend, `europe_1805`, turn 2. Five things checked on screen, in order:
>
> 1. **Prussia's modal fired first and alone.** A major power's routine `open_borders`
>    ask still gets its own DIPLOMATIC ENVOY popup with Hardenberg's line and the full
>    Accept / Counter / Reject / Not Now arms. Great-power traffic is visibly untouched.
> 2. **The command's own output was NOT swallowed.** After answering Prussia the
>    terminal read *"Responding to Prussia's proposal: reject / You have rejected
>    Prussia's proposal"* and only THEN did the letter-book raise — the whole reason it
>    is not a route entry.
> 3. **THE SMALL COURTS WRITE (2)** — *"Ottoman and Portugal write. Answer them here.
>    Unanswered letters lapse when the turn ends, and a court left waiting will not
>    raise the matter again for some seasons."* Both letters render in full with their
>    own voices — **Reis Efendi's "an old admirer of whatever endures" and Araujo's
>    "would far rather reach an understanding than be caught standing in its path"** —
>    their terms, and their own Accept / Decline.
> 4. **Inline Accept works.** One click signed *PEACE → OPEN_BORDERS with Ottoman*, the
>    row vanished, the header became **(1)** / *"Portugal writes."*, the envoy badge went
>    2 → 1, and **no result modal appeared**.
> 5. **Nothing is lost and nothing loops.** Clicking the letter BODY opened the full
>    envoy popup *with the Counter arm* exactly as the row hint promises; dismissing and
>    typing another command did **not** re-raise the panel (the per-turn latch), and the
>    envoy badge reopened it with both rows and buttons intact.
>
> **One defect found by playing it, fixed in-slice:** the panel's authored rect is a
> CEILING for `Utils.clamp_centered_panel`, and at 600×400 the taller letter rows
> clipped the second letter behind a ~40px scroll strip. Raised to 960×720 (scene-local;
> the panel is not shared) and the subtitle given `autowrap_mode`. Re-verified live at
> 2560-wide: both letters fully readable without scrolling.
>
> **Residuals, stated not hidden.** (a) If a small court's letter is the ACTIVE
> dialogue and a great power writes later the same turn, the great power's modal
> waits until the letter is answered — but it is listed in the same panel, one click
> from opening in full, and on every measured turn the majors were delivered first
> anyway. (b) `coalition.py:1513` silently removes every live proposal from a court
> joining a coalition, with no `offer_lapsed` record — pre-existing, and the reason
> the client re-FETCHES rather than mutating rows in place. (c) `pending_envoy_count`
> over-counts for the "will lapse" warning because it includes persistent settlement
> offers; the digest emits its own `lapsing_count` rather than inheriting the lie.

~~3–5~~ **A measured 2** near-identical Open Borders / Non-Aggression / Gift-of-Friendship
proposals per turn from the small courts, each a blocking modal that interrupts a command
in flight. The per-nation voices are among the best writing in the game — Reis Efendi's
*"an old admirer of whatever endures"*, Consalvi's *"her friendship rather than her fear"*
— and volume is flattening them. Batch routine small-court proposals into one digest with
per-row accept/decline, keeping the voice line on each row. Great-power and settlement
traffic unaffected.

### IGR-G — Two legibility fixes *(gate: yes — see §5 note)*

**G1 — the settlement authoring viewport.**

> ⚠ **v0.1 SAID** a fixed small `custom_minimum_size` or competing `size_flags`. **Both
> refuted** — the scene authors a generous **320px** floor and the correct `EXPAND_FILL`.

The real cause is two-part: `proposal_confirm_popup.tscn`'s `PanelContainer` has a fixed
**720×520** design rect that `Utils.clamp_centered_panel` treats as a *ceiling*
(`utils.gd:447` `minf(design.y, …)`) — so the settlement screen renders 720×520 on a
2560×1440 monitor — and `_relax_child_minimums` (`utils.gd:502-505`) distributes the
248px excess **proportional to headroom**, which charges the largest floor the largest
share. `PerCourtScroll` holds 70% of the headroom, absorbs ~175px, and lands at ~145px ≈
6 rows. **The region the player needs most is the one the relax pass robs hardest,
precisely because it declares the largest floor.**

Fix: raise the *ceiling* (settlement-scoped, not a blanket enlargement — the scene is
shared by ~12 dialogue types) and make the relax pass weight-aware so the primary content
yields last. **Do not** touch `custom_minimum_size = Vector2(0, 320)` — pinned verbatim
at `tests/test_settlement_gate4_leg1_fixes.py:501-503`.

**G2 — map piece stacks.** Spread logic *does* exist (`_marshal_slot_offset_2d`,
`map_renderer_base.gd:1331-1348`, two ranks above 2) but slot spacing is **30px against a
~35px visible figure**, so pieces overlap at *every* zoom — geometry, not zoom. The
unreadable part is the **name labels**: a 13px vertical stagger across a 60px span with
~40–60px-wide names, and they live in `force_layer` under `world_layer`, so they **scale
with the camera** at a fixed 11px face (province labels do not — `map_label_layer.gd`
draws in screen space with clamped faces). At contain-fit that is ~7–10 effective px on
top of the overlap. **No aggregation exists anywhere.**

Cheap fix = widen spacing to ~38–40 + a third rank above 4, and above 3 co-located
marshals draw **one** stack label (*"Ney +4"*) instead of N. The "+N" tin-plaque badge is
a separate, art-bearing increment.

---

## 3. Acceptance

- Suite green and ruff clean per commit; the pre-commit hook is the gate.
- **Any `.gd`/`.tscn` slice boots the engine once and greps `SCRIPT ERROR`** and
  regenerates the parse harness (EXIT=0) — the standing XR-1 rule.
- **IGR-B, IGR-D and IGR-F are verified live in the client**, not just by test: this
  review found five defects that every test was green through.
- **Byte-identity gates** for the view-layer slices — `test_combat_sweep_metrics.py`
  M1–M7 and the 40-turn `BASELINE_SERIES`. A move there means the change leaked into the
  simulation and the slice is wrong.
- IGR-D closes with an **in-client screenshot of the Proclamation card**.
- `BUG_FIXES.md` IGR-1..4 and `DESIGN_REFINEMENT.md` IGR-D1..3 struck through with their
  landing commit as each slice lands.

---

## 4. Deferrals (GR9)

| Item | Why not here | Owner |
|---|---|---|
| Beats 2/3/7 never firing | Structural, already measured (`AI_WAR_DECISION_SPEC.md` §8.2) | AI-V arm (a) |
| "The Polish Question" label unsighted | Reachable the moment IGR-D lands | IGR-D's live pass |
| Congress beat 6 unsighted | Campaign ended at turn 9; needs ~T15+ | Any longer playtest |
| Modal stacking (a queued envoy over the settlement I clicked) | Observed once, not reproduced | Re-check in IGR-F's live pass |
| `MAX_EVENT_LOG_SIZE` eviction by refusal bursts | Producer-side; the fix changes AI-3 cardinality | Its own gate — **not** IGR-B |
| Marshal name labels scaling with the camera | A re-home out of `force_layer` into a screen-space layer | Its own row after IGR-G |

### 4.1 Found in passing — routed, not owned here

The verification fleet surfaced two defects unrelated to the review, both routed to
`BUG_FIXES.md`:

- **IGR-X1 (P1, crash).** `enemy_ai.py:2039` does `del marshal._recovery_destination`,
  permanently removing the attribute; `marshal.py:1485` then reads
  `self._recovery_destination` directly in `to_dict()` → **`AttributeError` on any
  save/autosave** after an AI marshal completes recovery. Reproduced in a 20-turn ambient
  run. `world_state.py:9233-9234` already uses the safe `hasattr`+assign-`None` form;
  `enemy_ai.py` does not.
- **IGR-X2 (P3).** `WorldState.get_region_intel` (`world_state.py:1937-1943`) lazily
  **inserts** an UNKNOWN `RegionIntel` on read, so `filter_campaign_log` — a pure-looking
  read path — mutates `world.intel`. An in-session `GET /campaign_log` perturbs the
  world's intel key set.

---

## 5. The gate — ✅ **HELD AND BLESSED July 25, 2026**

> **THIS SECTION IS THE GATE RECORD AND IS AUTHORITATIVE.** The user asked for
> recommendations, then directed "put in answers" — a delegated grant. All three live
> questions are decided **at the spec's recommendations**, with **one amendment the user's
> request prompted: Q2 lands as a SPLIT, not the binary the spec offered.** Q3 was struck
> before the gate (§2, IGR-C withdrawn) and needed no decision.
>
> | | Decision |
> |---|---|
> | **Q1** | **(a)** — aggregate at the view layer, keyed `(turn, proposal_type)` |
> | **Q2** | **(a) scoped to `create_client`** + **(b) for every other identity clause** |
> | ~~Q3~~ | struck pre-gate — IGR-C withdrawn |
> | **Q4** | **(a)** — plunder = province income **× 4**, in-band tunable |
>
> **The build may proceed on all slices.** The full options tables are preserved below so
> the reasoning behind each decision stays auditable.

### Q1 — ✅ DECIDED **(a)**: aggregate, keyed `(turn, proposal_type)`

| | Option | Effect |
|---|---|---|
| **a** | **Aggregate at the view layer, keyed `(turn, proposal_type)`** *(recommended)* | Measured 21 → 1 line. No new event type, no schema change, no Godot diff |
| ~~b~~ | ~~Per-category filter / demotion~~ | **STRUCK on evidence** — the buried payload (`agenda_shift`) shares category "diplomacy" with the noise, so any category filter hides the signal too |
| c | Suppress AI-AI refusals from the view entirely | Cheapest; loses a real signal about who is isolated |

**DECIDED (a).** *"Nine courts rebuffed Austria"* is a story; twenty-four lines are not.

> **Rider carried into the build:** this does **not** relieve the `MAX_EVENT_LOG_SIZE=500`
> eviction — the bursts are ~4% of the ring buffer every ~7 turns, so real history
> (battles, captures) still gets pushed out. That is producer-side, and throttling the
> producer changes `get_refused_asks` cardinality → AI-3's ladder gate. **It must not be
> folded into IGR-B.** Owner: its own gate, after IGR-B lands.

### Q2 — ✅ DECIDED: **(a) scoped to `create_client`, plus (b) for the rest**

| | Option | Effect |
|---|---|---|
| **a** | **Carry them** — extend the pair-substitute carry-over to translate `create_client` (and vassalage / liberation) *(recommended)* | Tilsit becomes possible; the Proclamation becomes reachable in a normal campaign. Cost: the bilateral scorer must price an identity clause, and the armistice arm keeps excluding them (the G4F-15 ruling stands) |
| b | **Steer back** — disable "Make peace with X only" when the draft holds an identity clause, naming the joint route | Small and honest, but leaves the marquee feature gated behind beating four great powers at once |
| c | Leave as is | `bdeb17c` already stopped the lie; the feature stays hard to reach |

**DECIDED — the split, not the binary.** The spec offered a/b/c; the gate takes **(a) for
`create_client` only, and (b) for every other identity clause**:

- **`create_client` CARRIES** into the pair-substitute peace. It is the marquee clause, it
  is the one blocking the Proclamation, it has the direct historical warrant (**Tilsit** —
  the Duchy of Warsaw was carved from Prussia *alone* while the British war ran), and it is
  the closest identity clause to an existing bilateral term (a territory cede plus a flag),
  so its pricing can lean on machinery that already exists.
- **Vassalage / liberation / forced-alliance stay settlement-tier**, and the bilateral
  route is **disabled with a stated reason** when the draft holds one — never dropped
  silently. This is option (b) applied to exactly the clauses (a) does not cover.

**Why the split beats either pure option.** Pure (a) means teaching the bilateral
acceptance scorer to price *every* identity clause — a balance surface one review cannot
size responsibly. Pure (b) leaves the Proclamation gated behind beating four great powers
simultaneously: this review satisfied every prerequisite by real play (at war with Prussia,
Posen held and secured, gate green, clause authored) and still could not finish it. A
feature most players will never complete is not really shipped.

**Unchanged by this decision:** the **G4F-15 ruling stands** — the *armistice* arm keeps
carrying concessions only. A truce that erects a client state is not a truce.

**Definition of done for IGR-D is now two-armed:** (1) a player who has beaten one court
can carve from that court alone and the Proclamation fires — closed by an **in-client
screenshot**; (2) a draft holding vassalage/liberation shows the bilateral route disabled
with its reason, and a test pins that no identity clause is ever dropped silently again.

### ~~Q3. What becomes of the "designs held in check" counsel?~~ — **STRUCK, no decision needed**

Withdrawn with slice IGR-C (see §2). The rung is not an orphan — the exposure mechanic's
other two surfaces render at boot and were verified PASS in the review, and the AI-vs-AI
silence already has an owner in `AI_WAR_DECISION_SPEC.md` §8.2-1 (AI-V arm (a)). The
broadening was measured to yield **0 rows while France remains the hegemon**, and would
have rendered Sweden's anti-Napoleon design as held in check against Britain.

**Nothing is asked of the user here.**

### Q4 — ✅ DECIDED **(a)**: plunder = province income **× 4**

| | Option | Effect |
|---|---|---|
| **a** | **Scale to the province** — ~3–5 turns of its income | Nassau pays ~450–750g instead of 87g — enough to matter early, never enough to fund a war |
| b | Re-cut as stability-vs-authority rather than gold | Removes the balance question; changes what the prompt is *about* |
| c | Leave it | Accept that Secure is always correct and the prompt is flavour |

**DECIDED (a), `PLUNDER_INCOME_MULTIPLIER = 4`** — a **blessed number, in-band tunable**;
any change to the *shape* (e.g. moving to option b) escalates.

**The falsifiable acceptance test**, so the number can be judged rather than argued:

> A turn-3 player holding under ~2,000g should plausibly choose **Plunder**; a turn-20
> player holding over ~20,000g should not. If both still always Secure, the multiplier is
> too low — **not** the design.

**Recorded dissent, so it is not lost:** option **(b)** is arguably the better *design* —
it deletes the balance-number problem entirely and makes the prompt about what kind of
ruler you are rather than arithmetic. (a) was taken because it is in-band tunable and
matches how this project has handled blessed numbers. If the acceptance test above fails
twice at different multipliers, **re-open at (b) rather than tuning a third time.**

### Gate note on IGR-G

**G1 and G2 also want a decision**, though not a numbered question: G1 re-weights a layout
helper shared by every centre-anchored popup, and G2 is a **third** tuning pass over map
furniture whose visual sign-off the user has kept open since U5. Recommend landing
IGR-A/B/C first, then bringing G1 and G2 to the user **with screenshots**.

---

## 6. Build order

~~`IGR-A` (gate-free, four items)~~ ✅ **LANDED July 25, 2026** → ~~**pause for review**~~ ✅ →
~~`IGR-B` (Q1)~~ ✅ **LANDED July 25, 2026** → ~~`IGR-D` (Q2, ends with the live
Proclamation sighting)~~ ✅ **LANDED July 25, 2026** → ~~`IGR-F`~~ ✅ **LANDED July 26, 2026**
→ **▶ `IGR-E`** (Q4) → `IGR-G` (after the user sees screenshots). **IGR-C is withdrawn.**

`IGR-D` sits late deliberately: it is the only slice touching the settlement engine, and
it wants the polish slices landed so its live pass is clean.
