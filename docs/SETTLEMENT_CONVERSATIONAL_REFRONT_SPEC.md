# Settlement Conversational Re-front Spec

**Status:** DRAFT v0.1 — **DESIGN GATE. NEEDS APPROVAL. DO NOT CODE WITHOUT USER APPROVAL.**
(Follows the same gate convention as `JEALOUSY_SPEC.md`.)

**Date:** May 28, 2026
**Owner / sequencing:** Next-up priority for the Peace Deals / Imperial Settlement arc.
**Builds on (reuse, do not rebuild):** `DIPLOMACY_SPEC.md` (bilateral proposal + terms-guidance flow), `SETTLEMENT_UI_CLEANUP_SPEC.md` (clause model, acceptance scorer, scoped draft store, ratification gate), `DIPLOMAT_VOICE_BIBLE.md` (settlement voice families).
**Supersedes as the player-facing front door:** the raw SC-5R-2 settlement editor form, which becomes the opt-in deep tier (see §6).

> This is a high-level **vision** spec. Its job is to lock the coherent model before any implementation. Detailed control-state matrices, payload schemas, and per-dial deltas are deferred to a v0.2 written only **after** this vision is approved.

---

## 1. Why this exists — the divergence

The SC-5R-2 settlement editor set out to fix a narrow bug (empty/no-clause common peace) and chose a "structured editor, no raw JSON" approach. In doing so it reimplemented only the **deepest, rawest tier** of the existing diplomacy flow — granular clause assembly — and shipped it as the **front door and the only door**, stripped of the three things that make that tier usable in normal diplomacy:

- no Talleyrand-proposed baseline (you face a blank form),
- no intent dials (Harsher / More generous),
- no live acceptance while authoring,
- pickers that are not valid-by-construction (e.g. a `liberation` clause defaults to *France liberates France from France* and is only rejected at Submit).

The invalid-combo bug found during Gate 4 smoke is a **symptom**: a naked raw form with no baseline and no guidance lets the player assemble contradictions. The cure is to restore the conversational spine that bilateral diplomacy already has.

**The machinery to do this right already exists** (see §5). This is mostly wiring, not net-new systems.

---

## 2. The coherent vision (one sentence)

> **A common-peace settlement is authored through the same conversational, Talleyrand-mediated flow as a bilateral peace proposal — extended to cover more than one enemy court at once.**

A settlement is simply *"a peace proposal that can name several courts."* Same spine, same verbs, same live acceptance feedback, same valid-by-construction guarantee — only the scope is multi-party.

**Thematic identity — a peace conference.** A multi-party settlement is, in effect, a **peace conference**: France and several courts at one table, each with its own grievances, holdings, and price. Bilateral peace is the degenerate one-court case of the same conference. The experience should evoke a negotiated congress, not a form submission.

### Principles
1. **Talleyrand is the spine, not a bolt-on.** Every tier is mediated by his voice and a recommendation.
2. **Never a blank form.** You always start from a sensible, valid, context-aware draft.
3. **Steer by intent, see the cost live.** You push (harsher) or yield (more generous) and watch acceptance move in real time — per court and overall.
4. **You can never author the illegal.** You can push on what is *allowed*; when something isn't, you're told why rather than discovering it at Submit.
5. **Multi-party is first-class.** Coverage, per-court acceptance, and cross-court trade-offs are part of the conversation, not an afterthought.
6. **The player requests; the advisor suggests — never random.** Specific terms (which region is ceded, how much gold, which clause) are **requested by the player** with full agency, exactly as in a bilateral peace. Talleyrand **suggests** logically from each court's desires and holdings and the military picture (`NATION_DESIRE_PROFILES` + war state) and explains *why* — but the system never randomly assigns or silently auto-fills a term. A suggestion is a starting point you can accept, change, or replace, not an imposition. (Territory and gold are requestable terms, not system-rolled outcomes.)
7. **Every conference feels novel — not a carbon copy per war score.** Two conferences should rarely read the same. Novelty comes from **situational specificity** (which courts are at the table, what each covets and holds, relationships, betrayal memory, coalition posture — a large enough input space that situations rarely repeat) and from **conversational texture** (Talleyrand's per-conference read; per-court voice via the Voice Bible families), **not** from randomness and **not** from a rote `war_score → fixed template → identical screen` mapping. Mechanics stay deterministic per Golden Rule #6 — acceptance scoring and term effects are reproducible for a given full situation; "novel" is a property of input-richness and presentation, never of randomized outcomes. Any future variation for repeat situations must be **bounded and presentation-only**, never touching the scored result.

---

## 3. The three-tier flow (mirror of bilateral diplomacy)

| Tier | Bilateral diplomacy today | Settlement re-front (this spec) |
| --- | --- | --- |
| **1 — Propose** | Talleyrand drafts smart terms (`generate_suggested_terms`, 5-stage, nation-aware, economically capped) | Talleyrand drafts a baseline settlement for the whole covered set — valid for every court by construction |
| **2 — Steer by intent** | `Send as suggested` / `Harsher terms` / `More generous`, each re-scoring acceptance live | Same verbs over the settlement package — applied to the **whole table by default or to a single focused court** ("press Prussia," "ease Britain") — with **per-court + overall acceptance** updating live. Talleyrand may also lead with a targeted posture recommendation; his targeting is advice/voice only |
| **3 — Push on specifics** | `Adjust terms` — guided step-by-step builder | The existing structured clause editor, now the **opt-in deep layer**, with **valid-by-construction** pickers |

The default path is Tiers 1→2 (propose, then nudge). Tier 3 is the power-user surface for players who want to hand-shape a specific clause — but it inherits the same validity guarantee, so the liberation-style nonsense can't be built there either.

---

## 4. The multi-party dimension (what is genuinely new vs. bilateral)

This is the heart of "works like other peace but allows multi-party":

1. **One settlement, a set of covered courts.** A settlement names `covered_enemy_participants` within a single war. Courts not covered stay at war.
2. **Per-court acceptance, never a blended number.** Each covered court has its own pressure, losses, and objectives, so each has its own acceptance. The conversation surfaces *per-court* readings ("Britain will sign; Prussia will not unless you concede X"), plus an overall "does this settlement carry" summary.
3. **Coverage is part of the conversation.** Adding or dropping a court ("make peace with Prussia too?") re-draws the baseline, each court's terms, and who remains at war — and Talleyrand reasons about whether widening the net is wise.
4. **Cross-court validity.** Valid-by-construction spans the whole set: the same region can't be promised to two courts, a non-covered court can't be bound, and a clause's `from`/`to` must be real participants on the right side.
5. **Talleyrand reasons across the table,** not clause-by-clause in isolation — he weighs the package against each court and flags the binding constraint.

Bilateral peace is then just the n=1 case of this same model.

---

## 5. Reuse map (this is mostly wiring)

| Need | Existing machinery to build on |
| --- | --- |
| Baseline draft (Tier 1) | `generate_suggested_terms` pattern + the existing concession-baseline generator — **generalized beyond losing-side-only** to propose for any side, any number of covered courts |
| Live acceptance (Tier 2) | `calculate_common_peace_acceptance` (already per-settlement) wired into the editor the way `calculate_acceptance` feeds the bilateral proposal flow (`acceptance_breakdown`) |
| Intent dials (Tier 2) | the `modify_harsh` / `modify_generous` redraft-and-rescore pattern, adapted to operate on the settlement package (and/or per court) |
| Voice + recommendations | `DIPLOMAT_VOICE_BIBLE.md` settlement families (already authored) + the named-diplomat resolver |
| Deep editor (Tier 3) | the SC-5R-2 `settlement_editor_popup`, with pickers refiltered to be valid-by-construction |
| Draft persistence | scoped `pending_settlement_drafts_by_key` + the non-destructive `suspend_settlement_editor` close (unchanged) |
| Ratification gate | the existing fresh-rescore `confirm_settlement` gate (unchanged) |

---

## 6. What changes / what stays

- **Front door changes:** blank raw form → Talleyrand-proposed baseline + intent dials + live per-court acceptance.
- **The structured picker editor stays** — but becomes **Tier 3** ("push on specifics"), reached on demand, with **valid-by-construction pickers** (this absorbs the liberation/invalid-combo class of bug and the deferred `DWL-SET-SC5R-3` inline-merge-conflict follow-up).
- **Backend clause/validation/ratification contracts stay.** We feed them from the conversational front instead of a naked form; the validator remains the source of truth, and pickers mirror it.
- **Incoming AI offers** (the SC-5 / SC-30 path) read naturally as the inbound side of the same model and should converge on the same per-court presentation.

---

## 7. Non-goals (this pass)

- Not redesigning the clause set, acceptance math, or ratification mechanics.
- Not building AI-side settlement agency — **Slice G stays a separate, later item.**
- Not specifying exact dial deltas, control-state matrices, or payload schemas — those land in v0.2 after this vision is approved.
- Not removing Tier 3; the goal is to *front* it with guidance, not delete the power-user surface.

---

## 8. Open questions for approval

1. **Dial scope:** do `Harsher` / `More generous` operate on the whole settlement, per side, per covered court — or offer both whole-package and per-court? *(Discussion lean: **both** — whole-table by default + per-court when a court is focused, via progressive disclosure; Talleyrand may lead with a targeted posture as voice/advice only, never LLM-decided mechanics. Tier 2 stays court-level; clause-level precision stays in Tier 3. Confirm and lock in v0.2.)*
2. **Coverage editing:** conversational ("also make peace with Prussia?") vs. the existing covered-enemies checklist vs. both.
3. **Tier-3 exposure:** is the raw editor always one click away ("Edit terms"), or gated behind an "advanced" affordance so the default experience stays conversational?
4. **Per-court acceptance display:** how much detail in Tier 2 (a band per court? top blocker per court? full component breakdown only in Tier 3?).
5. **Losing-side framing:** the existing concession baseline becomes the Tier-1 baseline for the losing side — confirm it generalizes cleanly to multi-party (different courts may want different concessions).
6. **Novelty sourcing:** which inputs feed the per-conference texture (court desires, betrayal memory, coalition posture, relationships, holdings), and is any *bounded, presentation-only* variation wanted for repeat conferences in the same situation — strictly never touching the scored mechanics?
7. **Request affordance for territory/gold:** confirm the player requests specific regions/amounts through the Tier-3 surface (mirroring bilateral "Adjust terms"), with Tier-1 advisor suggestions pre-filling the logical default that the player can override.

---

## 9. Gate & sequencing

- **Immediate next action — finish this spec, then audit it.** Resolve the §8 open questions into a **v0.2** (detailed control-state, payloads, per-dial behavior, tests), then run a coherence/completeness **audit** of the spec — before any implementation code or final approval.
- **This is the next-up priority** for the settlement arc (ahead of Slice G, which remains blocked and separate).
- **Design gate:** NEEDS APPROVAL. On approval → write v0.2 (detailed control-state, payloads, per-dial behavior, tests) → implement in slices:
  - Slice 1 — Tier 1 baseline (generalize the suggested-terms / concession generator to multi-party, any side).
  - Slice 2 — Tier 2 intent dials + live per-court acceptance wired into the front surface.
  - Slice 3 — Tier 3 valid-by-construction editor (folds in `DWL-SET-SC5R-3`).
- **Gate 4 manual smoke re-runs** against the re-fronted flow once Slices 1–2 land.
- **Interim de-risk (optional, independent):** the cheap picker-filtering band-aid (disable Add Clause when a clause type has no valid target; filter role pickers so self-referential combos can't be authored) can land on its own to unblock the current Gate 4 pass without waiting for the full re-front. It is strictly a symptom patch; the re-front is the cure.

---

## 10. Worked example — war with three courts

France is in one coalition war against **Britain + Prussia + Austria**. France's leverage differs per court: winning decisively vs Prussia, roughly even vs Austria, behind at sea vs Britain. This is the peace conference the model is built for.

**Tier 1 — Talleyrand proposes one baseline, calibrated per court (illustrative numbers):**

```
SETTLEMENT — War of the Third Coalition          Talleyrand proposes:
  Prussia   request Silesia + 200g indemnity        Prussia  78%  will sign
  Austria   status-quo peace (no demands)           Austria  56%  leaning yes
  Britain   white peace                             Britain  62%  will sign
                                          OVERALL:  this peace carries
```
Talleyrand explains *why* per court (Prussia broken and able to pay; Austria wary, so ask little; Britain only wants off the Continent). Every clause is a **suggestion the player can change**, and every clause is legal by construction. Nothing was randomly assigned — the suggested regions/amounts come from each court's desires and holdings.

**Tier 2 — steer by intent, watch each court react live.** Clicking *Harsher* redrafts and **re-scores per court**: Prussia falls to ~44% (now refuses), Austria ~29% (refuses), Britain ~16% (hard reject). One dial, three different consequences, shown before committing.

**Coverage lever (multi-party only).** The player can **drop Britain** from the conference; Britain stays at war while Prussia + Austria settle. Talleyrand reads the consequence ("Britain stands alone on the Continent and may sue for terms themselves").

**Tier 3 — request specifics for the swing court.** Austria is the wobbler. The player opens the deep editor for Austria, **requests** a smaller border region instead of the suggested one and adds a gold sweetener France pays → Austria climbs 56% → ~71%. Pickers only offer regions Austria actually holds; Austria's land cannot be promised to Prussia (valid by construction).

**Ratify.** Final review shows the per-court outcome and applies each pair's peace transition.

**Why per-court, not blended:** a single averaged number would hide that the same package is generous to Britain and ruinous to Prussia. The conference scores each court independently so the player can see — and shape — exactly where the peace holds or breaks.

**Why it feels novel each time:** the next conference has a different set of courts with different desires, holdings, grievances, and coalition posture, plus Talleyrand's situation-specific read — so it reads fresh without any randomness in the underlying mechanics.
