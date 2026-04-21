# MP v2.4.3 - Block 3: Bloc Naming and Post-Block-2 Closure Gate

> **Source:** post-audit design follow-up after the comprehensive Memory and Pressure review. Blocks 1/2 close contract and substrate gaps; Block 3 is the next closure pass in sequence before the remaining v2.4.3 implementation continues. It owns the bloc-legibility decision and also absorbs the specific post-Block-2 follow-through items that were deferred but still need to land.
>
> **Ships as:** scoped spec + implementation closure block now.
>
> **Pre-merge gate for:** the post-Block-2 v2.4.3 implementation pass. Sequence is Block 1 -> Block 2 -> Block 3 -> remaining B-Hegemony / B-B1-lite / B-B3 / B-B4 / B-B7 / C-lite work. This is **not** a prerequisite for starting Blocks 1/2; it is the next gate after they land.
>
> **Depends on:** Block 1 and Block 2 routing being current in `STATUS.md`, plus `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.4.3, `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` B-Hegemony + C-lite, `docs/COMMITMENTS_PRESENTATION_SPEC.md` v0.5.1, `docs/DIPLOMAT_VOICE_BIBLE.md`.
>
> **Total effort if adopted:** ~1 focused spec pass, ~1 implementation session, ~8-12 tests.

---

## Scope summary

| Severity | Count | Dimension |
|----------|-------|-----------|
| BLOCKER | 1 | Terminology split (`bloc` != `coalition`) |
| HIGH | 3 | Activation gate, deterministic naming taxonomy, surface ownership |
| MAJOR | 4 | Voice contract, implementation constraints, tests, playtest gates |
| MINOR | 2 | Copy examples, scale fallback hygiene |

This block still centers the bloc-legibility pass, but it is no longer purely narrow. It now also owns the specifically deferred post-Block-2 closures that were never actually completed elsewhere.

That does **not** mean Block 3 owns the entirety of `C-lite`, `B-B4`, or `B-B7`. It owns the enumerated deferred pieces below so they are no longer living in handoff limbo.

---

## Execution mode

Treat Block 3 as a **scoped closure block**, not as an open-ended brainstorm. A fresh session should leave this block with two things resolved:

1. **Bloc naming decision for v2.4.3.**
   Either adopt the naming layer and record it in the live docs, or explicitly decline it and close that part of the block on purpose.
2. **Deferred post-Block-2 follow-through.**
   The enumerated `C-lite` / `B-B4` / `B-B7` / composite-floor leftovers below are now owned by Block 3 and should be implemented or explicitly descoped here rather than left implied for a later session.

Block 3 is **not done** if it only generates discussion or merely re-lists deferred work. Its output should leave the docs and queue in a materially cleaner state.

### Expected outputs

If Block 3 is **adopted**, the pass should leave behind:

- a presentation-spec update in `docs/COMMITMENTS_PRESENTATION_SPEC.md` that owns the `33%` / `50%` / `60%` bloc-label contract and surface routing
- an implementation-plan update in `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` that places the derived-helper/test work in the correct follow-on slice
- a voice-bible update in `docs/DIPLOMAT_VOICE_BIBLE.md` that covers the named-bloc reveal beat and its crisis restatement
- a `STATUS.md` note confirming Block 3 was adopted and naming any remaining post-Block-3 implementation that is still open

If Block 3 is **declined**, the pass should leave behind:

- a `STATUS.md` note that no additional bloc-naming layer is required for v2.4.3
- a short close-out note in this document explaining why the baseline hegemony/beats/headline surface was judged sufficient
- the remaining owned follow-through items still resolved or explicitly descoped here, since they no longer belong to some vague future owner by default

Regardless of the naming decision, the pass should also leave behind:

- implemented or deliberately descoped closure of the owned deferred items listed below
- updated routing in `STATUS.md` so the next session does not have to guess what Block 3 already consumed versus what remains after it

### Definition of done

Block 3 can be considered closed only when all of the following are true:

- the docs explicitly say whether bloc naming was adopted or declined for v2.4.3
- `bloc` versus `coalition` terminology is protected across the affected docs
- the `33%` / `50%` / `60%` activation behavior is either canonized or deliberately rejected
- implementation ownership is clear: this block may authorize later code work, but it must not quietly create a new mechanic or save surface
- the deferred items listed below are either closed in Block 3 or explicitly descoped in writing with a reason

### Closure states

Close Block 3 as **ADOPTED** only when:

- `docs/COMMITMENTS_PRESENTATION_SPEC.md` owns the bloc-label threshold/surface contract
- `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` names the follow-on implementation owner and test expectations
- `docs/DIPLOMAT_VOICE_BIBLE.md` covers the reveal/crisis voice beats
- `STATUS.md` says Block 3 was adopted and points the next session only at the work still remaining after the owned deferred items were consumed here

Close Block 3 as **DECLINED** only when:

- `STATUS.md` explicitly says no additional bloc-naming layer is required for v2.4.3
- this document carries a short written reason for declining the feature expansion
- the owned deferred items are still closed or deliberately descoped, rather than vanishing behind the bloc-naming decision

### Verification bundle

Before closing Block 3, perform a short doc-level audit:

- grep for player-facing `coalition` usage in the affected diplomacy docs and confirm it is reserved for the formal anti-hegemon war structure
- confirm the same threshold story appears everywhere relevant: `33%` noticed, `50%` named reveal, `60%` hardened camps
- confirm `STATUS.md` and this document agree on whether Block 3 is still open, adopted, or deliberately declined
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

**Required surfaces once proper naming is adopted:**

- **Balance of Europe headline:** first-class owner of the bloc label.
- **`balance_of_europe_shifted` beats:** `50%` is the reveal moment; `60%` is the hardened-camps restatement.
- **Proposal preview warnings:** use the bloc name once unlocked so treaty friction reads politically.
- **Nation badges / ledger rows:** members of the hegemon bloc may display the proper label once it unlocks.
- **Coalition declaration copy:** if war coalition forms, the copy should contrast the coalition against the named hegemon bloc.

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

**Fail condition:** if playtest shows repeated confusion between "named bloc" and "formal coalition," keep bloc naming headline-only and defer member badges / broader warning use.

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

Treat this as the **third audit/design gate in the v2.4.3 queue**, immediately after Block 2 and before the remaining implementation slices. If adopted, it gives us a clean chance to lock bloc-legibility language before B-Hegemony / C-lite prose hardens in code. If the team later decides the baseline beats/headline are already enough, this block can still be closed quickly with a deliberate "no additional bloc naming needed" call rather than being forgotten.
