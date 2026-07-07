# CR-5 Implementation Brief — Personality-Biased Disambiguation

> **⏩ SAFE HALF + PHASE 3 LANDED.** Safe half: master `f999329`→`a438614` (July 6, 2026). **Phase 3 — the lethal attack-on-arrival gate — LANDED at master `de6d740` (July 7, 2026):** the fortification/terrain-aware gate mechanism is built, tested (90 CR-5 tests, full suite 11,673 green), and adversarially audited (5 findings fixed). **Only Phase 4 remains** (flip the aggressive arm on + wire it in `main.py` + rider (d)). The aggressive→attack arm is still gated OFF (`delegation.AGGRESSIVE_ATTACK_ARM_ENABLED = False`) so no delegation verb can trigger an ungated battle today; Phase 4 flips it behind the guardrail-(d) sign-off. **Read Appendix B first** — it is now a turnkey Phase-4 checklist.
>
> **Status:** Pre-implementation methodology + voice-craft bar. Drafted July 6, 2026.
> **Normative authority:** `docs/COMMAND_ROBUSTNESS_SPEC.md` §6 is the *what* (blessed scope, July 5, 2026). **This brief is the *how*** — the recommended top-code-quality implementation methodology, the verified seam map, and the marshal-voice register baseline. Where this brief and §6 disagree, §6 wins; fix the drift.
> **Scope:** CR-5 only. CR-5b (Flavor Echoing) is a separate owned slice; its boundary is defined in §7 below.
> **Anchor caveat:** line numbers drift. Anchors below were verified against live code on July 6, 2026 (marked ✅) or are inherited from the pre-build audit and must be re-confirmed in Phase 0 (marked ⚠). Prefer the file+symbol reference over the exact line.

---

## 0. Thesis — what "top code quality" means for THIS slice

CR-5 is a **contract-encoding, de-risking slice**, not a feature-invention slice. §6 already did the hard design work (the three-way split, the cut rows, the guardrails). So quality = **zero drift from the blessed contract + the smallest possible code surface + four proven invariants**, and — because there is no documented marshal-voice standard yet — **CR-5 also sets the marshal-voice register baseline** (a down payment on DEF-1).

Three load-bearing truths reshape the naive reading of the slice:

1. **It is NOT prompt-copy-only.** The live LLM only fires *below* the 0.7 confidence gate; a confident mock parse of a delegation verb funnels straight to `attack` and never reaches the prompt you'd edit. The real work is the **mock degrade** (§1).
2. **The personality bias is invisible from a single command.** So the **deterministic, character-naming attribution copy IS the feature** (Acceptance #7), not decoration.
3. **The lethal seam is the attack-on-arrival strategic-execution bypass** — fortification-blind and objection/AP-skipping. It must close *before* the aggressive arm merges (§Phase 3).

Fable-level here means: the risky arm cannot merge without its guardrail, the invisible feature cannot ship without its legibility copy, every cut item is held out by an explicit boundary test, and the new copy is indistinguishable in register from the objection system already in the game.

---

## 1. The reframe: CR-5 is not prompt-copy-only (verified)

The command-parse pipeline has ONE parse entry both paths flow through, but the fast/mock parser **always runs first** and the live LLM is consulted **only for low-confidence parses**:

- `LLMClient.parse_command` skips the LLM on "mock mode, high confidence, no game_state, or meta command" ✅ ([llm_client.py:322](../backend/ai/llm_client.py) header + `LLM_FALLBACK_CONFIDENCE_THRESHOLD` gate at [:362](../backend/ai/llm_client.py)).
- The threshold is **0.7**; mock action-only confidence is **0.8**, which clears it ✅ ([llm_client.py:1253](../backend/ai/llm_client.py)). The file's own header comment records this exact trap ("0.8 action-verb confidence otherwise cleared the 0.7 gate").
- **Consequence:** in the shipped default (`LLM_MODE=mock`) and any confident live parse, editing the prompt table changes *nothing*. Prompt copy alone does not move the default player experience.

**Therefore the real change is the mock degrade:** a marshal-addressed *delegation verb* must drop to low confidence so it routes to the CR-2 "ask" clarification instead of the `attack` funnel. CR-2 already built the exact lever — marshal-aware confidence lowering via `UNRESOLVED_ADDRESS_CONFIDENCE` ✅ ([llm_client.py:1257-1264](../backend/ai/llm_client.py)). CR-5's mock work *extends this seam*; it does not invent one. **The mock never produces the bias — it degrades to ASK.**

**Collision to flag:** `deal with` is currently a **diplomatic keyword** ✅ ([llm_client.py:1379](../backend/ai/llm_client.py): `"deal with", "talk to", "speak to", "negotiate with"`). A marshal-addressed `deal with Wellington` must not mis-route into the diplomatic parser (guardrail e). This is a real, pre-existing hazard, not a hypothetical.

---

## 2. Verified seam map

| Seam | Anchor | CR-5 change | Owning test | Acc# |
|---|---|---|---|---|
| LIVE prompt table | `## Personality Rules` ✅ [prompt_builder.py:365](../backend/ai/prompt_builder.py); `FEW_SHOT_TEMPLATES` ✅ [:137](../backend/ai/prompt_builder.py); personality reaches prompt via marshal-format ✅ [:533-541](../backend/ai/prompt_builder.py) | Expand generic block into the §6.2 delegation-verb table (intent-verb only) | LIVE-tier corpus matrix | 1,2 |
| MOCK degrade | `_parse_with_mock` ✅ [llm_client.py:654](../backend/ai/llm_client.py); CR-2 confidence lever ✅ [:1257-1264](../backend/ai/llm_client.py) | Marshal-addressed delegation verb → low confidence → CR-2 ask (never the `attack` funnel) | Guardrail (e) mock test | 3 |
| Diplomatic-keyword collision | `deal with` ✅ [llm_client.py:1379](../backend/ai/llm_client.py) | Ensure marshal-addressed delegation does not mis-route to diplomacy | Guardrail (e) no-mis-route | 3 |
| Personality lookup | `marshal.personality` (plain `str`) ✅ [marshal.py:238](../backend/models/marshal.py); compared `== "aggressive"` ✅ [:646](../backend/models/marshal.py) | Read at parser level via `world.get_marshal(name).personality`; treat anything outside `{aggressive,cautious,literal}` (incl. `balanced` default) as ASK | Arm-mapping tests | 1 |
| temp-0 pin | `temperature=0.3` at ✅ [providers.py:424](../backend/ai/providers.py) **and** [:767](../backend/ai/providers.py); commented send ✅ [:825](../backend/ai/providers.py) | ⚠ **Phase 0 must confirm which path reaches the API body**, then pin it to `0`; assert in the CR-1 harness | temp==0 assertion | guardrail (b) |
| Golden-Rule-6 enforcement | `validate_parse_result` ✅ [validation.py:188](../backend/ai/validation.py) | Bias sets ONLY `action`; strip/reject any non-action field | Non-action-fields-unchanged test | guardrail (a) |
| Lethal attack-on-arrival bypass | `_strategic_execution: True` at 8 sites ✅ [strategic_executor.py:817/860/919/965/981/1030/1337/1473](../backend/commands/strategic_executor.py); adjacent-path gate ⚠ `executor.py` `evaluate_situation` | Tag inferred orders; route inferred attack-on-arrival through one fortification-aware bad-odds gate; explicit typed orders stay gate-free | Lethal one-modal test | guardrail (c) |
| Ordering | CR-4 `resolve_context_references` **before** parse ✅ [main.py:1135](../backend/main.py); CR-2 `build_*_clarification` **after** ✅ [main.py:1301/1400](../backend/main.py) | Attach CR-5 without disturbing this order | Ordering regression | — |
| Literal-arm ask surface | CR-2 `command_clarification` ✅ [clarification.py](../backend/commands/clarification.py) | Route "ask" into the existing LOCAL_PLANNING surface — no parallel question path | Literal-routes-to-CR2 test | — |
| Player-reachability pins | `test_cr5_literal_arm_player_reachable` + `..._massena_aggressive_is_his_character` ✅ [test_europe_1805_scenario.py:165/180](../tests/test_europe_1805_scenario.py); Soult=`literal` ✅ [europe_1805.json:97](../godot-client/project-sovereign/assets/maps/europe_1805.json) | Do not edit personality data to defuse a mechanic | Both pins green (baseline gate) | guardrail (d) |

---

## 3. Phase plan

### Phase 0 — Freeze the contract-to-code map (no code)
- Transcribe §6.1–6.8 into a checklist keyed to Acceptance Criteria 1–8, **verbatim** (paraphrase is the drift vector).
- Re-confirm every ⚠ anchor above against live code — especially **which `temperature` reaches the API body**, and the `executor.py` `evaluate_situation` gate the strategic path bypasses.
- Freeze the **allowlist** (§6.2: `deal with, handle, see to, take care of, sort out, attend to, do something about` + inflections) and the **denylist** (`march/advance to/head to/proceed to/pursue/chase/hunt/support/reinforce/link up`) already owned by the fast parser + CR-3 remaps. Double-ownership is a defect (Acc #4).
- Confirm CUT/re-homed items stay OUT: the literal "continues standing order" row, `cover/watch/keep an eye on`, the autonomous Grouchy Moment.
- Author the **marshal-voice register baseline** (§4) as a written artifact and record it as a **DEF-1 down payment** (Golden Rule 9 — home + landing).
- Design the **delegation-inferred order tag** (the discriminator for the Phase-3 gate) on paper.

**Exit:** written `seam→change→test→acceptance#` map covering all 8 criteria + guardrails (a)–(e); allowlist/denylist + inferred-order tag frozen; register baseline written and homed. Zero code changed.

### Phase 1 — Test-harness-first + land the safe pinned checkpoints
- **Baseline gate:** both pins green (`test_cr5_literal_arm_player_reachable`, `..._massena_aggressive`). Any red is a hard stop.
- **Land temp-0 standalone** (guardrail b): body change + `temperature==0` assertion. Cheapest determinism win, isolated.
- **Land rider (d) "words become the record"** as its own STATUS-rowed mock-safe slice: read CR-4's stored `raw_input`, quote verbatim in `campaign_log.format_event_oneliner` + battle-report attribution (pure string ops, no LLM). Test asserts verbatim in **both** surfaces **and** a **negative** assertion that it does NOT parrot an explicit `attack Wellington`.
- **First-use hint** (§6.7): static Berthier copy, once per campaign, never on explicit verbs — or record the drop explicitly in §6.7 (Golden Rule 9).
- **Write these as RED tests now** (feature-absent, not error): guardrail (a) non-action-fields-unchanged; guardrail (e) mock delegation → CR-2, no diplomatic mis-route, and neutral/balanced/loyal/unset → ALWAYS ask; excluded-ownership regression (Acc #4); ordering regression (CR-4 before / CR-2 after); one-modal legibility **incl. the lethal fortified-superior-force case**; the LIVE-tier corpus matrix (same utterance × personality → Ney=attack / Davout=scout / Soult=ask).

**Exit:** pins green; temp-0 + rider (d) + first-use-hint landed (or hint drop recorded); all guardrail/ordering/legibility/corpus tests exist and fail for the *right* reason. No interpretation code yet.

### Phase 2 — Implement the NON-BATTLE arms (cautious + literal), both seams
- **LIVE prompt table:** expand the `## Personality Rules` block into the §6.2 table verbatim, scoped this phase to cautious (scout/hold/fortify) + literal (ask). State the `if adjacent…else…` splits as **INTENT-LEVEL only** — the LLM emits the intent verb; the deterministic executor resolves attack-vs-`MOVE_TO`-vs-scout from geography (Golden Rule 6). Add live-roster few-shots. Do **not** list denylist verbs here.
- **MOCK degrade:** marshal-addressed delegation verb drops to low confidence → CR-2 ask. Mock never produces the bias.
- **Literal/neutral ask** routes into the existing CR-2 `command_clarification` LOCAL_PLANNING surface — no parallel path. Deterministic template from resolved target + known personality.
- **Cautious soft note:** non-blocking LOCAL_PLANNING note with one-tap reissue, reusing CR-2 per-option command strings. Honest copy (the scout still burns AP + a turn).
- **Craft review pass #1** (non-battle copy) against §4 + §5.

**Exit:** cautious + literal LIVE corpus rows green; mock degrades to CR-2 with no diplomatic mis-route; guardrails (a)/(e)/ordering/excluded still green; the aggressive corpus row + one-modal legibility tests stay RED.

### Phase 3 — Close the lethal seam (prerequisite for the aggressive arm)
- **Tag delegation-inferred orders** distinctly from explicitly-typed ones — explicit `attack Wellington` and typed strategic orders stay **gate-free**; only a personality-inferred aggressive resolution carries the tag.
- **Route the tagged attack-on-arrival through the same bad-odds gate as the adjacent case.** Today the non-adjacent path runs via `_strategic_execution: True`, bypassing the objection/`evaluate_situation` gate **and** AP cost.
- **Make the odds fortification/terrain-aware** — read the same modifiers the adjacent `evaluate_situation` path uses (the loose ~0.7 raw strength ratio is fortification-blind).
- **One modal, never two:** if the marshal objects, the objection **is** the gate; the CR-2 confirm fires **only** for the aggressive-suicidal no-self-objection case. Tiers are battle-starting vs not, not reversible vs irreversible.
- Turn the lethal Phase-1 test green.

**Exit:** inferred tag distinguishes inferred from explicit; both adjacent AND attack-on-arrival route through one fortification-aware gate; exactly-one-modal holds; lethal test green; explicit typed orders regression-assert gate-free. Only now is the aggressive arm eligible to merge.

### Phase 4 — Merge the aggressive arm + adversarial self-review
- Enable aggressive → attack / move-to-engage / attack-on-arrival in the prompt table; turn the Ney→attack LIVE corpus row green; confirm the full §6.5 set (1–8).
- **Craft review pass #2** (battle-starting copy) against §4 + §5. Every inferred surface **names the marshal's character** (Acc #7) — deterministic template, never LLM echo (that's CR-5b).
- **Adversarial audit** (feed each finding back as a new failing test before fixing): Golden-Rule-6 leak (grep the diff for any path setting `strategic_score/ambiguity/trust/outcome`); double-ownership; two-modals; attack-on-arrival end-to-end through the strategic executor; mock/live parity; scope-boundary (no cut/re-homed leak; rider (d)/CR-5b not folded into the parse seam); pin regression.
- **Live-API probe** (`LLM_MODE=anthropic`) the four §6.2a before-state commands — confirm they resolve per personality instead of collapsing to attack.

**Exit:** all §6.5 criteria pass; both craft passes signed off; adversarial pass produced no un-tested regression; full suite + ruff + parser_eval green under the pre-commit hook.

### Phase 5 — Land + post-landing audit
- Commit directly to master (single-dev workflow); let the pre-commit hook gate ruff + full pytest — **never `--no-verify`**. `Co-Authored-By` trailer.
- Update changed-behavior docs same day: `COMMAND_ROBUSTNESS_SPEC.md` §2/§6 (LANDED + SHA), rider (d) STATUS row, `docs/STATUS.md` Next Steps (CR-5 → CR-5b), `CLAUDE.md` Current Phase line, and this brief's status. If the inferred-order tag added a serialized field: `to_dict`/`from_dict` with `.get` default, `SAVE_FORMAT_REFERENCE.md`, run `test_serialization_enforcement.py`.
- **Emit the Codex audit prompt targeting master AT the CR-5 commit SHA** covering the four invariants: CR-4-before/CR-2-after ordering; Golden Rule 6 at `validate_parse_result`; the one-modal fortification-aware attack-on-arrival gate; excluded-verb ownership.
- **Record the CR-5b entry-gate handshake:** CR-5b is the RESPONSE seam; its entry gate is a designed **non-parroting** mock fallback. Never fast-follow. Record the parked "mechanical delegation incentive" gap (owned by CR-6/CR-7) per Golden Rule 9.

**Exit:** CR-5 on master with green pre-commit gate; docs updated; Codex audit emitted by SHA; CR-5b named next with its entry gate intact.

---

## 4. Marshal-voice register baseline (CR-5's DEF-1 down payment)

**Finding:** the Voice Bible is foreign-diplomats-only; VISION gives the three personality *archetypes* but no register detail; full marshal-voice systematization is deferred to **DEF-1**. The executors, however, already contain a de-facto house style (audited July 6, 2026). CR-5 conforms to it and writes down the baseline — recorded as a DEF-1 down payment.

**The eight rules:**

1. **Berthier narrates in third person; the marshal is the subject** (present tense). First person only inside single-quoted marshal speech — e.g. `Ney refuses outright: 'We outnumber them! Let me attack!'` ([strategic_executor.py](../backend/commands/strategic_executor.py)).
2. **"Sire" to the Emperor; display names for marshals/targets** (via `display_names`). Never an internal key, personality string, or action enum in player text.
3. **Personality = *what*, trust tier = *how*.** Personality controls the concern raised (aggressive→battle, cautious→safety, literal→clarity); the existing trust-tier prefix ladder controls respect (`refuses outright` / `challenges the order` / `firmly objects` / `respectfully raises concerns`). **Do not invent a parallel tone system.**
4. **Register per arm:** aggressive → imperative/exclamatory, contempt for delay; cautious → hedged, measured, periods, a concrete reason; literal → deferential, awaiting instruction, takes no initiative.
5. **1–2 short clauses, period-military diction** (give battle, reconnoiter, fortify, reinforce). No modern slang, no purple prose.
6. **Name the reading.** Because the bias is invisible from one command, every inferred line makes the interpretation explicit (`Ney reads this as…`). This is legibility (Acc #7), not flavor.
7. **Words become the record — conditionally.** Quote the player's verbatim phrase in log/report **only when an interpretation occurred**. Never quote back an explicit order (that's the parroting failure mode).
8. **Deterministic floor, generative ceiling.** CR-5 ships the template floor. CR-5b may enrich via LLM but **may never override register** — a register-violating line is dropped for the template. (This is the Voice Bible's own diplomat rule, inherited for marshals. Register is load-bearing.)

**Anti-patterns (the DON'Ts, for craft-pass rubric):** new tone system; implicit interpretation (invisible ship); parroting an explicit order; first-person outside a quoted objection; purple prose; internal-key leakage; a parallel ask-UI instead of CR-2; LLM echo inside CR-5.

---

## 5. Copy palette (exemplars — a palette, not brittle single strings)

| Surface | Exemplar A | Exemplar B |
|---|---|---|
| **Aggressive → attack** (Ney/Massena/Murat/Lannes) | `Ney needs no second invitation — he takes "deal with Wellington" for a call to battle and attacks.` | `Ney reads your order as you knew he would, Sire: 'Leave Wellington to me!' — he attacks.` |
| **Cautious → scout note** (Davout) — non-blocking + reissue | `Davout, cautious as ever, reads this as reason to look before he leaps — he moves to scout. It will cost a turn. [No — order the assault]` | `Ever careful, Davout will reconnoiter before committing his men. [No — attack now]` |
| **Literal → ask** (Soult) — routes to CR-2 surface | `Soult will not presume your meaning, Sire. "Deal with Wellington" — give battle, or observe? [Attack] [Scout]` | `Soult awaits your intent, Sire: is Wellington to be attacked, or watched? [Attack] [Scout]` |
| **One-modal bad-odds** (aggressive inferred attack into fortified superior force — the lethal seam) | `Ney reads this as an assault, Sire — but Wellington stands fortified and in greater strength. He'll charge on your word. [Confirm the attack] [No — hold]` | `Massena is eager, but the odds are cruel: they are dug in and stronger. [Confirm] [No — hold]` |
| **Rider (d) — the record** (log + battle report) | Log: `On your order "deal with Wellington," Ney gave battle at Mont-Saint-Jean.` | Negative case (explicit `attack Wellington` typed): **no quote-back** — `Ney attacked Wellington at Mont-Saint-Jean.` |

**Single-modal discipline:** if the marshal *self-objects* (a cautious one would), the objection **is** the gate — no extra confirm. Only the aggressive-who-won't-object suicidal case gets the bad-odds modal.

---

## 6. Code structure for testability

- **One copy home** — a `describe_delegation(marshal, arm, action, target, player_phrase)` helper (fold into `clarification.py` or a small `delegation_voice.py`), keyed by arm, reusing `display_names` + the existing trust-prefix helpers. No scattered f-strings across executors.
- **Tests assert the craft, not just the wiring:**
  - (a) the acting marshal's display name appears;
  - (b) the "reads…as" interpretation phrase appears (legibility, Acc #7);
  - (c) rider (d) — the player's verbatim phrase appears in log **and** report;
  - (d) **negative** — an explicit `attack X` produces **no** quote-back;
  - (e) grep the output for internal keys / `MOVE_TO` / personality strings → none leak;
  - (f) the literal-arm ask resolves through the CR-2 `command_clarification` LOCAL_PLANNING surface, not a bespoke path.

---

## 7. CR-5 / CR-5b boundary

- **CR-5** = deterministic templates establishing the marshal-voice baseline (§4). No LLM echo.
- **CR-5b (Flavor Echoing)** = the generative layer on top. It inherits a *proven* pattern — the Voice Bible's "mock template is the floor; LLM enriches but never overrides register; drop-and-fallback on violation." Its entry gate is a **non-parroting mock design** (rule 8 above). Keeping echo *out* of CR-5 is what keeps this boundary clean. **Never fast-follow CR-5b onto CR-5.**

---

## 8. Risk register

| Risk | Mitigation |
|---|---|
| **Prompt-copy-only illusion** — confident mock parse (≥0.8) never reaches the LLM; default `mock` players see no change | Fix the mock degrade explicitly (marshal-addressed delegation → low confidence → CR-2 ask); assert via guardrail (e). Both seams land. |
| **Attack-on-arrival hole shipped open** — delegated Massena/Murat silently commits a suicidal assault on a fortified force via `_strategic_execution:True` | Phase 3 is a hard prerequisite for the aggressive arm; the lethal test is the merge gate; make odds fortification-aware. |
| **`deal with` mis-routes to diplomacy** — it is already a diplomatic keyword ([llm_client.py:1379](../backend/ai/llm_client.py)) | Guardrail (e) asserts a marshal-addressed delegation verb does not hit the diplomatic router. |
| **temp-0 assumed a no-op** — `temperature=0.3` may or may not reach the API body | Phase 0 confirms the live path; add `temperature: 0` to it; assert `temperature==0` in the CR-1 harness. |
| **Invisible ship** — bias imperceptible from a single command | Named-personality attribution is Acc #7 with its own test + two craft passes. |
| **Ordering break** — CR-5 attached at the wrong seam | Ordering regression test pins CR-4-before / CR-2-after before interpretation code lands. |
| **Double-ownership** — claiming denylist verbs collides with fast parser + CR-3 remaps | Excluded-ownership regression test (Acc #4) as tripwire. |
| **Golden-Rule-6 leak** — bias sets `strategic_score/ambiguity/trust/outcome` | Strip/reject at `validate_parse_result`; test asserts non-action fields unchanged. |
| **Two modals stack** — objection + CR-2 confirm double-prompt | Objection-first; confirm only on the no-self-objection suicidal case; assert exactly one modal. |
| **Pin regression via character edits** — recasting Massena/Soult to defuse the mechanic | Both pins are the Phase-0 baseline gate; personality = character, handle danger with guardrails. |
| **Scope creep** — re-importing cut rows / Grouchy Moment / folding CR-5b into the parse seam | Scope-boundary audit asserts each stays out. |
| **Silent obligation drop** — first-use hint test doesn't yet exist | Ship the hint or record the drop in §6.7 (Golden Rule 9). |

---

## 9. Definition of Done (matches CR-0..CR-4 rhythm)

- [ ] §6.2 verb table encoded as prompt copy in `## Personality Rules` (Acc #1).
- [ ] Same utterance × personality → distinct action asserted in the CR-1 golden corpus at the **LIVE tier** (Ney→attack, Davout→scout, Soult→ask) via `parser_eval.py` (Acc #2).
- [ ] Mock never produces a silent wrong bias — degrades to CR-2, no diplomatic mis-route (Acc #3).
- [ ] Excluded verbs regression-asserted (Acc #4).
- [ ] Guardrails (a)–(e) each have a passing test; (d) personality-type freeze signed off with a SHA **before** the aggressive→attack arm merged (Acc #5).
- [ ] Rider (d) has its own STATUS row + passing mock test (verbatim in both surfaces; negative no-parrot-on-explicit) (Acc #6).
- [ ] Every inferred-resolution surface names the acting marshal's personality, asserted in a test (Acc #7).
- [ ] Delegation first-use hint fires once per campaign, never on explicit verbs (asserted) — or its drop explicitly recorded in §6.7 (Acc #8).
- [ ] Both pins green: `test_cr5_literal_arm_player_reachable` + `test_cr5_signoff_massena_aggressive_is_his_character`.
- [ ] The lethal attack-on-arrival test green; exactly-one-modal asserted across adjacent + on-arrival seams; explicit typed orders regression-assert gate-free.
- [ ] Full `pytest` + `ruff check backend/` green through the pre-commit hook (no `--no-verify`); live-API probe confirms the four §6.2a before-state commands resolve per personality.
- [ ] Marshal-voice register baseline (§4) recorded as a DEF-1 down payment (home + landing).
- [ ] Docs updated same-day (COMMAND_ROBUSTNESS_SPEC §2/§6, STATUS.md, CLAUDE.md Current Phase, this brief; SAVE_FORMAT_REFERENCE + serialization test if a field was added).
- [ ] Codex audit prompt emitted targeting master at the CR-5 commit SHA; CR-5b recorded as next with its non-parroting-mock entry gate intact; mechanically-optional gap recorded (CR-6/CR-7).

---

## Appendix — verification log (July 6, 2026)

Verified ✅ against live code: the 0.7/0.8 mock-confidence gate and CR-2 confidence lever; `deal with` as a diplomatic keyword; `marshal.personality` as a plain `str`; the 8 `_strategic_execution:True` sites; `validate_parse_result` at [validation.py:188](../backend/ai/validation.py); the CR-4-before/CR-2-after ordering in `main.py`; both CR-5 pins; Soult=`literal` in `europe_1805.json`; the `## Personality Rules` block + `FEW_SHOT_TEMPLATES` + personality-format path in `prompt_builder.py`.

Needs Phase-0 re-confirmation ⚠: which `temperature=0.3` reference actually reaches the API request body (`providers.py:424` vs `:767`, with a commented send at `:825`); the exact `executor.py` `evaluate_situation` gate the strategic path bypasses; the §6 acceptance-criteria numbering (this brief mirrors the pre-build audit's read of §6 — reconcile against the spec's own numbering in Phase 0).

---

## Appendix B — Phase 3/4 handoff (July 6, 2026 — the SAFE HALF is landed)

**Read this first if you are the session picking up the lethal seam.**

### What already shipped (master `f999329` → `a438614`)

Phase 0 (frozen seam map) + the entire **non-battle half** of CR-5, landed and live-playtested:

| Landed | Behavior |
|---|---|
| temp-0 parse pin (guardrail b) | `providers.py` `_make_parse_request` body carries `temperature: 0` |
| Deterministic **ASK arm** | literal / neutral / mock → a two-option ASK (`Attack` / `Scout`) on the shipped CR-2 `command_clarification` popup; overrides any live-LLM guess for a literal marshal. Literal titles "SOULT ASKS:"; neutral/interim stays "BERTHIER ASKS:" |
| Deterministic **cautious arm** | a cautious delegation is re-issued as `scout <enemy LOCATION>` (the LLM proved too flaky + mis-resolves targets) + a character-naming soft note with a typed reissue |
| §6.2 **prompt table** (AC-1) | `prompt_builder.py` `## Personality Rules` (advisory — routing is deterministic) |
| §6.7 **first-use hint** (AC-8) | once-per-campaign, serialized `WorldState.delegation_hint_shown` |

Phase-0 anchor corrections already applied/known: `evaluate_situation` lives in **`objection_v2.py:1075`** (not `executor.py`); the fortification-aware helpers are `objection_v2.py` `evaluate_cautious` / `_check_attack_target_fortified` (`:936-999`); the 8 `_strategic_execution:True` sites are confirmed; temp-0 drift D-3 fixed.

### THE FAILSAFE — why the lethal hole cannot ship by accident

`delegation.AGGRESSIVE_ATTACK_ARM_ENABLED = False`. While False, `route_arm()` sends **every** aggressive delegation to ASK (no ungated battle). The RED tripwire `test_aggressive_degrades_to_ask_until_gate_lands` asserts BOTH that the flag is `False` AND `route_arm("aggressive", True) == "ask"` — so **flipping the flag turns that test RED and the pre-commit hook BLOCKS the commit.** You cannot enable the aggressive arm without consciously updating that test, which is the built-in reminder to do the gate work first. A defensive comment also sits at the seam itself (`strategic_executor.py`, the `personality == "aggressive"` branch).

### Phase 3 — ✅ LANDED (master `de6d740`, July 7, 2026)

The gate MECHANISM is built + tested + audited. **Do NOT rebuild it — Phase 4 REUSES these primitives.** What shipped:

| Primitive | Where | Contract |
|---|---|---|
| **The tag** | `StrategicOrder.delegation_inferred: bool = False` (`marshal.py`) — serialized (`to_dict`/`from_dict`/`SAVE_FORMAT_REFERENCE`), `test_serialization_enforcement` green | ONLY tagged orders are gated; explicit typed orders keep today's raw-ratio behavior. **Phase 4's whole job is to SET this flag on the orders it creates.** |
| **The odds** | `objection_v2.inferred_attack_favorable(marshal, enemy, game_state) -> bool` (single source) | Mirrors combat.py's defender effective strength: region **terrain** (`TERRAIN_DEFENSE_BONUS`) + region **fortification building** (`0.25`) folded as strength, plus personal fortify `defense_bonus` (approximates its casualty-channel effect). `True` = favorable/auto-commit; `False` = route to the confirm. Pure superset of the legacy raw 0.7 ratio. |
| **The copy** | `delegation.describe_inferred_bad_odds(marshal, enemy) -> str` | Names the marshal's reading (Acc #7), mock-safe, no LLM. |
| **The per-turn gate** | `strategic.py StrategicOrderProcessor._inferred_attack_gate(marshal, target, game_state, allow_reroute=False)` | Returns a `contact_bad_odds` interrupt (sets `pending_interrupt` + `last_contact_*`) when a tagged order faces bad odds, else `None`. `allow_reroute` off at co-located/arrival seams (no `go_around`), on only mid-path. |
| **The first-step gate** | `strategic_executor._handle_first_step_blocked` aggressive branch | Tagged orders use `inferred_attack_favorable` + the named copy; explicit orders keep the raw ratio. |
| **Coverage** | **9 auto-attack seams** gated: first-step-blocked, MOVE_TO attack-on-arrival, 4 PURSUE sites, 2 blocked-path sites. Failsafe (`AGGRESSIVE_ATTACK_ARM_ENABLED=False`) + tripwire test intact. | Nothing PRODUCES a tagged order yet — Phase 4 does. |

Audit lessons already baked in (don't re-discover them): the odds fold region-fort **and** terrain **and** personal fortify; co-located gates omit `go_around` + set `last_contact` (no modal loop); the gate is single-source. 90 CR-5 tests pin all of this.

### Phase 4 — the ONLY remaining work (turnkey)

**Prereq (human):** re-confirm the guardrail-(d) personality-type freeze (§6.3d / §6.8) — this is the sign-off that the 7 marshals' types are correct *before* a vague order can start a real battle. Recorded done July 5; re-confirm at merge.

1. **Flip the failsafe.** `delegation.AGGRESSIVE_ATTACK_ARM_ENABLED = True` (`delegation.py:218`). Then **rewrite** the RED tripwire `test_aggressive_degrades_to_ask_until_gate_lands` (it goes RED by design) → assert the flag is `True` AND `route_arm("aggressive", True) == "aggressive"`.
2. **Wire the aggressive arm in `main.py`** — the CR-5 router block (~`main.py:1235`, alongside the `_arm == "cautious"` / `elif _arm == "ask"` branches). Add `elif _arm == "aggressive":`. **Keep it DETERMINISTIC** (the cautious arm's re-parse pattern is the template — the live LLM proved too flaky). **THE KEY INTEGRATION POINT:** the aggressive arm must produce a **strategic order tagged `delegation_inferred=True`** — a bare one-shot `attack` does NOT create a StrategicOrder and so is NOT gated (and an aggressive marshal won't self-object on the normal combat path). So route it as an **`attack <target>` that the strategic parser upgrades to `MOVE_TO`+`attack_on_arrival` (or `PURSUE`)**, then **set `delegation_inferred=True` on the resulting `marshal.strategic_order`** (post-execution, or thread a `command["_delegation_inferred"]=True` flag the strategic executor copies onto the order). Without the tag set, the Phase-3 gate never engages. Use the `DelegationMatch.target` (attack target) from `detect_delegation`.
3. **Rider (d) "words become the record"** (a delegation→battle path now exists): stamp the raw phrase on the inferred order (reuse `original_command` or add a field), quote it verbatim in `battle_report` attribution + `campaign_log.format_event_oneliner` battle one-liner. **NEGATIVE test:** an explicit `attack Mack` produces NO quote-back. Own STATUS row + own test (spec §6.4).
4. **LIVE-tier corpus rows** (`tests/data/parser_golden_corpus.json`): same utterance × personality → Ney→attack / Davout→scout / Soult→ask.
5. **Adversarial self-review + live-API probe.** Grep the diff for any Golden-Rule-6 leak (a delegation setting `strategic_score`/`ambiguity`/`trust`); assert exactly-one-modal end-to-end through the strategic executor; mock/live parity; scope-boundary. Live-API probe (`LLM_MODE=anthropic`) the four §6.2a before-state commands. Then **Phase 5** (docs same-day: spec §6 + STATUS + CLAUDE.md + this brief; Codex audit prompt targeting master at the Phase-4 SHA; record CR-5b next with its non-parroting-mock entry gate).

### Design calls the safe half + Phase 3 MADE (honor or revisit — also in STATUS.md)

- **Routing is DETERMINISTIC**, the prompt table advisory (a live probe showed the LLM mis-resolves both the action AND the target for delegation verbs — "take care of Kutuzov" → attack for cautious Davout, mis-scouted to Algarve). Phase 4 should keep the aggressive arm deterministic too. Revisiting = reintroducing the flakiness the clamp removed.
- The **cautious/scout target is the enemy's LOCATION**, not his name (the scout executor reaches a place). A pre-existing `scout <marshal>` mis-resolution bug is filed as a separate task.
- The **literal ASK is marshal-voiced** ("SOULT ASKS:").
- **Phase 3 odds call:** personal fortify `defense_bonus` IS folded (as a strength-boost approximation of its casualty effect) — required so the spec's own example ("42k vs a *fortified* 54k → bad odds") holds. The region fortification building (0.25) + terrain are folded exactly as combat does. Don't "simplify" this away without breaking the spec example.

### Files Phase 4 will touch
`delegation.py` (flip the flag) · `main.py` (the `elif _arm == "aggressive":` branch — tag the created order) · `strategic_executor.py` / `strategic.py` (only if the tag needs threading onto the order) · `battle_report.py` + `campaign_log.py` (rider d) · `test_command_robustness_cr5_personality_disambiguation.py` (rewrite the tripwire, add end-to-end aggressive tests) + `tests/data/parser_golden_corpus.json`. **The gate primitives (`inferred_attack_favorable`, `_inferred_attack_gate`, the tag, the copy) are DONE — reuse, don't rebuild.**
