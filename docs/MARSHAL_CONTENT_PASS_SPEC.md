# Marshal Content Pass (1805 Roster Depth)

> **Status:** DRAFT v0.1 — July 2, 2026. **NEEDS USER DESIGN GATE before implementation** (the ability set is a design decision). The MC-0 display-bug fix may land independently as a bug fix.
> **Origin:** July 2, 2026 re-staging audit — this gap was previously UNOWNED (Golden Rule 9). The shipped 21-marshal 1805 roster authors only name/nation/location/strength/personality/movement/biography; everything that makes marshals *people* is defaulted.
> **Vision anchor:** Marshals ARE the game ("talk to your generals", the Grouchy Moment, personality over randomness). A campaign where Ney has no Bravest of the Brave, every skill is a flat 5, and no marshal has a relationship with any other is mechanically playable but characterally empty — and it silently disables the substrate Jealousy v3.1 needs.

---

## 1. Ground truth (audited July 2, 2026)

Via `create_marshal_from_data` (`backend/models/marshal.py:1357-1385`), every 1805-scenario marshal boots with:

- **`ability = {"name": "None"}`** — zero functioning wired abilities in the shipped campaign. Ney's "Bravest of the Brave" (`combat.py:251`) and Davout's "Counter-Punch Mastery" (`marshal.py:888-891`) key off ability NAME, which scenario-Ney/Davout lack. The other wired names (Drouot, Wellington, Blucher, Uxbridge) are legacy-Waterloo-only marshals absent from the roster.
- **Flat default skills (all 5s)** — the 6-skill system provides no differentiation for the whole campaign.
- **Trust 70, zero authored relationships (all Professional)** — the coordination/objection/relationship substrate runs untextured; Jealousy v3.1's drama has no fuel.
- **Display bug (MC-0):** `marshal_overview._build_ability` gates on marshal NAME (`marshal_overview.py:28/:138`), so 1805 Ney/Davout report `ability_active=True` with ability name **"None"** in the management screen.
- Personality skew: **14 cautious / 3 aggressive / 4 literal** (was 14/4/3 until two July 5, 2026 CR-5-gate reassignments — Soult `cautious → literal` and Massena `aggressive → cautious` — see MC-4 + `COMMAND_ROBUSTNESS_SPEC.md` §6.1/§6.8); `balanced`/`loyal` remain unimplemented placeholders (ADDING_CONTENT.md:94-95; ARCH plan finding #29).
- Biographies are the one complete axis (21/21 authored).
- Design target already on record: `docs/ADDING_CONTENT.md:1567-1576` (1805 Roster Planning Notes — ~10-12 wired abilities across the roster) + candidate inventory in `docs/archive/SPECIAL_ABILITIES_EVALUATION.md`.

## 2. Slice plan

| Slice | Scope | Gate |
|-------|-------|------|
| **MC-0 (bug fix, independent)** — ✅ **LANDED July 4, 2026** | `marshal_overview._build_ability` now gates on a REAL ability name (`name not in ("", "None")`), not just the marshal name — so 1805 Ney/Davout (booted with `ability={"name":"None"}`) correctly report no active ability instead of an active ability literally named "None"; legacy marshals with genuine wired abilities still display. Matches the mechanics (combat wiring keys off the ability name too). The optional Ney/Davout ability restoration was deliberately NOT done here — authoring abilities into the roster is the gated MC-1 decision. `tests/test_marshal_content_mc0_ability_display.py`. | None |
| **MC-1** | Ability set design gate: pick ~10-12 wired abilities for the 21-marshal roster from the SPECIAL_ABILITIES_EVALUATION candidates (which marshals, which mechanics, wiring per the ADDING_CONTENT checklist). | **USER DESIGN GATE** |
| **MC-2** | Author skills/trust per marshal (historical differentiation — Davout's discipline, Murat's cavalry dash, Mack's… Mack-ness); registry/scenario authoring via `create_marshals_from_data`; per-marshal pin tests. | Rides MC-1 gate |
| **MC-3** | Author starting relationships (the historical web: Lannes↔Murat rivalry, Davout's aloofness, Soult's ambition) + enemy-side texture where it matters (Charles↔Mack). Prerequisite for the Jealousy v3.1 gate — its tuning must be re-derived against this roster shape (the spec's §9b still assumes the retired Waterloo pairs). | Rides MC-1 gate |
| **MC-4** | Personality coverage decision: implement `balanced`/`loyal` (trigger tables, V2 evaluators, AI behavior) or re-author the skewed roster within the existing three types. ROADMAP Phase 10's "evaluate before 1805" note — the condition arrived. **Two assignments already pulled forward** at the July 5, 2026 CR-5 gate (§6.8 sign-off; `europe_1805.json`): Soult `cautious → literal` (to give the player a commandable literal marshal; pinned by `test_cr5_literal_arm_player_reachable`) and Massena `aggressive → cautious` (his holding-front role made an inferred attack dangerous; pinned by `test_cr5_signoff_massena_cautious_not_aggressive`). MC-4 inherits current distribution **14 cautious / 3 aggressive / 4 literal** and should not re-litigate Soult or Massena without cause. Logged for MC to weigh: the panel judged Davout the *best* literal fit (cautious is the residue of Soult owning the literal slot), and Bernadotte's real trait — political unreliability — has no personality type (→ MC-3 trust/relationships). Note: literal's objection-trigger set is thin (MC-1/MC-2 own deepening it). | User decision |

## 3. Interactions

- **Jealousy v3.1:** MC-3 is effectively a prerequisite; the Jealousy gate should be sequenced after this pass, with a v3.2 addendum re-deriving scenario impact against the real roster.
- **Voice:** marshal voice tiers stay Phase 8.5 scope; this pass is data/mechanics authoring, not voice.
- **Golden rules:** all authoring flows through existing factories (`create_marshals_from_data`) — no parallel authoring path; serialization enforcement applies to any new field.
