# MP v2.4.3 - Block 3: Adopted Bloc Naming and Post-Block-2 Closure Gate

> **Status:** SUPERSEDED — April 20, 2026. This work order's design contract has been folded back into the owning specs; the audit doc is retained for historical context only, not as a live gate.
>
> **Where the canonical content lives now:**
> - **Bloc-naming contract (D1-D4, D9, D10):** `COMMITMENTS_PRESENTATION_SPEC.md` §8.1a (terminology guard, `33 / 50 / 60` activation gate, hegemon→label taxonomy with fallback, required surface owners, worked-copy examples, implementation constraint, playtest feel gates).
> - **Voice register per band (D5):** `DIPLOMAT_VOICE_BIBLE.md` "Bloc-naming voice contract" subsection + existing `Balance of Europe beat` notes in each diplomat's register section. Minimum live coverage table already lists `hegemony_beat_*_{noticed,alarming,crisis}` per foreign court.
> - **Implementation helper (D6):** `RELIABILITY_IMPLEMENTATION_PLAN.md` Slice B-Hegemony (`describe_hegemon_bloc(world, hegemon, share)` — derived, no new save surface).
> - **Test gate (D7):** folded into B-Hegemony test list (threshold-band beats, label taxonomy, fallback, crisis persistence) and C-lite test list (headline render, threshold-beat copy, warning-family routing).
> - **Spec-level Balance-of-Europe hooks:** `RELIABILITY_COMMITMENTS_SPEC.md` §7.3 threshold-crossing contract + §11.1 headline composition — both now cite §8.1a for the label layer.
>
> **April 21 supersession note:** the original decision list below still says member badges / row stamps are deferred. That is historical text only. The live April 21 owner docs (`COMMITMENTS_PRESENTATION_SPEC.md` §8.1a.4, `RELIABILITY_COMMITMENTS_SPEC.md` §11.1, `RELIABILITY_IMPLEMENTATION_PLAN.md` Slice E-Cards, and `STATUS.md`) put Nations-tab row stamps in shipped v2.4.3 scope.
>
> **Former post-Block-2 closure items (CF1-CF4) are folded back into their parent slices:**
> - CF1 (C-lite): Balance-of-Europe payload in `build_diplomatic_ledger`, `commitments_notice_*` template family, `notification_bar.gd` icon map, full `resolve_named_diplomat(...)` wire-up — owned by Slice C-lite in `RELIABILITY_IMPLEMENTATION_PLAN.md`.
> - CF2 (B-B7): Make Amends emitters + `reparations_cooldown` — owned by Slice B-B7.
> - CF3 (B-B4): DG-4 call-to-arms emitters + `END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION` — owned by Slice B-B4.
> - CF4 (B-B1-lite + B-B4): Composite-floor regression tests — owned by Slice B-B4 per the B-B1-lite merge-ordering gate.
>
> **Routing:** no Block 3 consumption pass is required before the remaining implementation slices. Each slice above carries its own CF items; the B-B1-lite ↔ B-B4 merge-ordering gate remains in force.
>
> The content below is the original work-order text, preserved for historical context. It is not a live gate.

---

## Scope summary

| Severity | Count | Dimension |
|----------|-------|-----------|
| BLOCKER | 1 | Terminology split (`bloc` != `coalition`) |
| HIGH | 3 | Activation gate, deterministic naming taxonomy, surface ownership |
| MAJOR | 4 | Voice contract, implementation constraints, tests, playtest gates |
| MINOR | 2 | Copy examples, scale fallback hygiene |

This block still centers the bloc-legibility pass, but it is no longer purely narrow. The core design choice is already made, and the block now owns the specifically deferred post-Block-2 closures that were never actually completed elsewhere.

That does **not** mean Block 3 owns the entirety of `C-lite`, `B-B4`, or `B-B7`. It owns the enumerated deferred pieces below so they are no longer living in handoff limbo.

---

## Locked decisions

The following decisions are no longer open:

- **ADOPT deterministic bloc naming for v2.4.3.** The hegemon-side camp should be named so the player feels Europe hardening into camps rather than merely reading a hidden penalty.
- **Use the `33 / 50 / 60` staging already described below.** `33-49%` is descriptive only, `50-59%` unlocks the proper name, and `60%+` reuses that proper name in crisis language.
- **Keep the naming layer on existing high-value surfaces only.** Block 3 owns the Balance-of-Europe headline, `balance_of_europe_shifted` threshold beats, proposal-preview warnings, and coalition-declaration contrast copy.
- **Defer member badges / ledger-row bloc stamps.** They are not required to close Block 3 and should not expand scope unless a later playtest pass explicitly asks for them.
- **Keep the implementation derived and cheap.** One helper, no new serialized bloc identity, no new membership mechanic.
- **Do not descope the owned post-Block-2 follow-through items by default.** CF1-CF4 are mandatory Block 3 closure items unless this document and `STATUS.md` record a written descoping reason.

No further go/no-go design decision is needed for bloc naming in this phase. The remaining work is implementation and verification.

---

## Execution mode

Treat Block 3 as a **scoped closure block**, not as an open-ended brainstorm. A fresh session should leave this block with two things resolved:

1. **Implement the adopted bloc-naming contract for v2.4.3.**
   Wire the deterministic naming layer into the live docs/code paths that own the Balance headline, threshold beats, proposal warnings, and coalition declaration contrast.
2. **Deferred post-Block-2 follow-through.**
   The enumerated `C-lite` / `B-B4` / `B-B7` / composite-floor leftovers below are now owned by Block 3 and should be implemented or explicitly descoped here rather than left implied for a later session.

Block 3 is **not done** if it only generates discussion or merely re-lists deferred work. Its output should leave the docs and queue in a materially cleaner state.

### Expected outputs

- a presentation-spec update in `docs/COMMITMENTS_PRESENTATION_SPEC.md` that owns the `33%` / `50%` / `60%` bloc-label contract and surface routing
- an implementation-plan update in `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` that places the derived-helper/test work in the correct follow-on slice
- a voice-bible update in `docs/DIPLOMAT_VOICE_BIBLE.md` that covers the named-bloc reveal beat and its crisis restatement
- a `STATUS.md` note confirming the bloc-naming call is already made and naming any remaining post-Block-3 implementation that is still open

The pass should also leave behind:

- implemented or deliberately descoped closure of the owned deferred items listed below
- updated routing in `STATUS.md` so the next session does not have to guess what Block 3 already consumed versus what remains after it

### Definition of done

Block 3 can be considered closed only when all of the following are true:

- the docs explicitly say bloc naming is adopted for v2.4.3
- `bloc` versus `coalition` terminology is protected across the affected docs
- the `33%` / `50%` / `60%` activation behavior is canonized across the affected docs
- implementation ownership is clear: this block may authorize later code work, but it must not quietly create a new mechanic or save surface
- the deferred items listed below are either closed in Block 3 or explicitly descoped in writing with a reason

### Closure state

Close Block 3 as **CLOSED (ADOPTED CONTRACT EXECUTED)** only when:

- `docs/COMMITMENTS_PRESENTATION_SPEC.md` owns the bloc-label threshold/surface contract
- `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` names the follow-on implementation owner and test expectations
- `docs/DIPLOMAT_VOICE_BIBLE.md` covers the reveal/crisis voice beats
- `STATUS.md` says Block 3 was adopted and points the next session only at the work still remaining after the owned deferred items were consumed here

### Verification bundle

Before closing Block 3, perform a short doc-level audit:

- grep for player-facing `coalition` usage in the affected diplomacy docs and confirm it is reserved for the formal anti-hegemon war structure
- confirm the same threshold story appears everywhere relevant: `33%` noticed, `50%` named reveal, `60%` hardened camps
- confirm `STATUS.md` and this document agree that bloc naming is already adopted and Block 3 is now executing that contract
- confirm the owned deferred items are either explicitly completed here or explicitly descoped here

---

## Owned Post-Block-2 Scope

These items were explicitly deferred by Block 2 and were never actually finished elsewhere. Block 3 now owns them. The labels below show where they originated, but the responsibility to close them sits here unless this document explicitly descopes them again with a reason.

### CF1 - Former `C-lite` presentation follow-through

Still required before calling the wider v2.4.3 diplomacy pass presentation-complete:

- Balance of Europe payload block in `build_diplomatic_ledger`
- `commitments_notice_*` template family
- `notification_bar.gd` icon map extension
- `resolve_named_diplomat(...)` full wire-up beyond the current stub

### CF2 - Former `B-B7` apology-loop follow-through

Still required before the Make Amends lane is functionally complete:

- Make Amends emitters
- `reparations_cooldown`

### CF3 - Former `B-B4` defensive-refusal follow-through

Still required before the direct bilateral DG-4 call-to-arms lane is fully surfaced:

- DG-4 call-to-arms emitters
- `END_REASON_FAMILY_DEFENSIVE_REFUSAL_TERMINATION`

### CF4 - Former `B-B1-lite` + `B-B4` composite-floor regression net

Still required before acceptance-floor logic can be considered safely covered:

- Composite-floor tests handed off by Block 2 / T8

### CF5 - Audit monitoring only

These are **not** new Block 3 implementation items, but they stay listed here so they are not mistaken for forgotten work:

- Non-diplomacy-adjacent tests such as `test_enemy_ai.py` / broader `test_turn_manager.py` remain outside the active blast radius unless later slices touch them; pass-4 marked them clean.

### Owned-scope close condition

Before v2.4.3 is called ready beyond Block 3, each owned item above should be either:

- closed in Block 3, or
- deliberately descoped in `STATUS.md` with a written reason.

---

## BLOCKER

### 1. D1 - Never name peace-time blocs as coalitions

The biggest failure mode is conceptual confusion. The player must be able to distinguish:

- **Bloc / alignment / system / circle / interest:** a peace-time diplomatic clustering around a hegemon
- **Coalition:** the formal anti-hegemon war structure in `coalition.py`

If the hegemon-side camp is surfaced as a "coalition," the player will reasonably read war as already declared.

**Contract:**

- Reserve `coalition` for the formal anti-hegemon hostile structure only.
- Hegemon-side copy uses `bloc`, `alignment`, `system`, `circle`, or `interest` depending on surface.
- Never show "French Coalition," "British Coalition," etc. for the hegemon-side camp.

**Verify:** any future grep of player-facing strings should show `coalition` only on the anti-hegemon war side, not on hegemon-bloc labels.

---

## HIGH

### 2. D2 - Proper-name activation gate

Proper bloc names should not appear the moment a nation barely crosses the visibility threshold. The player should first sense the *gravitation*, then hear the *name*.

**Activation rule:**

- **`33-49%` share:** descriptive phrase only, no sticky proper name yet.
- **`50-59%` share:** proper bloc name unlocks across eligible surfaces.
- **`60%+` share:** same proper name persists; crisis copy intensifies.
- **Below `33%`:** no bloc-naming layer at all.

**Rationale:** `33%` is the "noticed" beat, not yet the "Europe has named this system" beat. `50%` is the right dramatic threshold for the proper-noun reveal.

**Implication for `balance_of_europe_shifted`:**

- `33%` beat uses descriptive language like *"a French-led alignment is taking shape"*.
- `50%` beat is the proper naming moment.
- `60%` beat reuses the proper name and makes the camps feel hardened.

### 3. D3 - Deterministic naming taxonomy

Do not let LLM prose invent bloc names ad hoc. Name selection must be deterministic and authored.

| Hegemon | Proper bloc name (`50%+`) | Descriptive phrase (`33-49%`) | Adjective stem |
|---------|----------------------------|-------------------------------|----------------|
| France | `French System` | `French-led alignment` | `French` |
| Britain | `British Interest` | `British-led alignment` | `British` |
| Austria | `Vienna System` | `Austrian-led alignment` | `Austrian` |
| Prussia | `Berlin Alignment` | `Prussian-led alignment` | `Prussian` |
| Saxony | `Saxon Circle` | `Saxon-led alignment` | `Saxon` |
| Fallback / future nation | `{Nation} Alignment` | `{Nation}-led alignment` | best available adjective, else nation name |

**Rules:**

- One hegemon -> one authored proper label.
- Labels are derived from the hegemon, not from a variable member list.
- No member-list-generated names like *"Franco-Bavarian League"* in v0.1.
- No ideology names, congress names, or continent-spanning "orders" yet.

### 4. D4 - Surface contract

Bloc naming should ride the surfaces that already exist. Do not invent a new UI family for this block.

**Required surfaces in Block 3:**

- **Balance of Europe headline:** first-class owner of the bloc label.
- **`balance_of_europe_shifted` beats:** `50%` is the reveal moment; `60%` is the hardened-camps restatement.
- **Proposal preview warnings:** use the bloc name once unlocked so treaty friction reads politically.
- **Coalition declaration copy:** if war coalition forms, the copy should contrast the coalition against the named hegemon bloc.

**Explicitly deferred out of Block 3:**

- **Nation badges / ledger rows:** do not add bloc stamps there in this pass. Keep the naming layer concentrated on the headline, threshold beats, warnings, and declaration contrast.

**Headline examples:**

- `33-49%`: *"France leads a widening French-led alignment (37%)."*
- `50-59%`: *"The French System commands 52% of Continental power."*
- `60%+` with brewing war: *"The French System commands 61%; hostile courts are hardening into camp against it."*
- `DECLARED`: *"Britain's coalition marches against the French System."*

**Non-goal:** retroactively renaming every old campaign-log row. This block is about live legibility, not archive polish.

---

## MAJOR

### 5. D5 - Voice and period-register contract

Bloc naming only helps if the diplomats sound like statesmen, not UI tooltips.

**Voice rules:**

- `33%` beat: descriptive phrase, no overcommitment, no capitalized system-name yet.
- `50%` beat: one named diplomat or chancery line introduces the proper name.
- `60%` beat: same speaker family or an escalated rival court makes the camps feel continental.
- No modern jargon: forbid `meta`, `sphere control`, `stack`, `synergy`, `faction lock`, or naked percentage-speak in the actual line.

**Desired feel by court:**

- Castlereagh names systems as institutional facts.
- Hardenberg names camps as tests of honor and alignment.
- Metternich names arrangements and consultations.
- Einsiedel names the fear of small courts being forced to choose.

### 6. D6 - Implementation constraint: derived helper, no new save state

This block should stay cheap.

**Contract:**

- Add one derived helper such as `describe_hegemon_bloc(world, hegemon, share)`.
- Helper returns only presentation data, e.g. `label`, `descriptive_label`, `adjective`, `is_proper_name_unlocked`.
- Do **not** add a serialized `bloc_names`, `bloc_identity`, or `alignment_store` field.
- Do **not** add a new membership mechanic; membership still derives from existing bloc helpers / treaty state.

### 7. D7 - Test gate

If this block is implemented, the minimum regression net should cover:

- `33%` uses descriptive phrasing only; no proper bloc label yet.
- `50%` unlocks the correct authored proper name.
- `60%` keeps the same name and intensifies the copy, rather than renaming again.
- Unknown / future hegemon falls back to `{Nation} Alignment`.
- Proposal warnings use the same label family as the Balance of Europe headline.
- Coalition-facing copy still says `coalition`, not `bloc`, on the war side.
- No new serialization surface is introduced.
- Save/load behavior is unchanged because labels are derived, not stored.

Estimated coverage: **~8-12 tests** across ledger, warning, and template-routing helpers.

### 8. D8 - Playtest gate

This block should land only if it clears these feel checks:

- The player can answer, at a glance, **what camp is forming** and **who it is forming around**.
- The `50%` beat feels like a reveal, not a redundant restatement of what the player already inferred.
- Players do **not** confuse the named bloc with an already-declared war coalition.
- The naming layer increases drama without making the map feel over-labeled or gamey.

**Fail condition:** if playtest still shows repeated confusion between "named bloc" and "formal coalition," keep the proper name on the Balance headline + threshold beats only and re-open proposal-warning wording before ship. Member badges are already deferred by decision.

---

## MINOR

### 9. D9 - Worked-copy examples

These are examples of the intended tone, not final committed prose:

- `33%` noticed: *"Vienna notes that a French-led alignment is beginning to take shape."*
- `50%` alarming: *"London names it plainly now: the French System is gathering dependents."*
- `60%` crisis: *"Berlin judges the French System nearly complete; Europe will soon have to choose."*

### 10. D10 - Scale fallback hygiene

This naming pass should still hold at larger rosters:

- At 5 nations, authored labels are enough.
- At 13-20 nations, fallback labels must remain readable for un-authored powers.
- Do not add member-list-based compound names until a later Europe-scale pass proves they are needed.

---

## Out of scope

- New bloc mechanics, bloc claims, or bloc obligations
- Any separate peace / congress / conference system
- Renaming the formal coalition mechanic
- AI behavior changes beyond using the surfaced label in existing warnings / beats
- New serialized diplomacy stores
- A second anti-hegemon "soft coalition" system

---

## Recommendation

Treat this as the **third closure block in the v2.4.3 queue**, immediately after Block 2 and before the remaining implementation slices. The bloc-legibility decision is already made: adopt deterministic bloc naming on the constrained surface set above, close the owned post-Block-2 items here, and then let the remaining implementation continue without another design-go/no-go pass.
