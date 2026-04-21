# MP v2.4.3 - Block 3: Bloc Naming and Alignment Legibility Gate

> **Source:** post-audit design follow-up after the comprehensive Memory and Pressure review. Blocks 1/2 close contract and substrate gaps; Block 3 is a future-facing fun/legibility gate for whether hegemony reads as political drama rather than a hidden debuff.
>
> **Ships as:** spec/design gate now; implementation later only if B-Hegemony + C-lite baseline lands cleanly and playtest still wants more bloc legibility.
>
> **Pre-merge gate for:** v2.4.3 fun sign-off after Block 1, Block 2, B-Hegemony, and C-lite. This is **not** a prerequisite for starting Blocks 1/2.
>
> **Depends on:** `docs/RELIABILITY_COMMITMENTS_SPEC.md` v2.4.3, `docs/RELIABILITY_IMPLEMENTATION_PLAN.md` B-Hegemony + C-lite, `docs/COMMITMENTS_PRESENTATION_SPEC.md` v0.5.1, `docs/DIPLOMAT_VOICE_BIBLE.md`.
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

This block is intentionally narrow: **name and surface the existing hegemon-side diplomatic camp more clearly**. It does **not** add a new mechanic, a new diplomacy store, or a new war-state.

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

Treat this as a **post-baseline fun gate**, not as a prerequisite for Blocks 1/2. If B-Hegemony ships and the mechanic is legible but still feels too numeric, Block 3 is a clean way to add political drama without reopening the core math. If playtest already shows that the named-court beats and Balance of Europe headline are enough, this block can remain parked without harming the core v2.4.3 contract.
