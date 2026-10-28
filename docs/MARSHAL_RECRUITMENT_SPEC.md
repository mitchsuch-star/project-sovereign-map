# Marshal Recruitment — "The Marshalate"

> **Status:** ✅ **LANDED July 11, 2026** as the final phase of the Jealousy v3.2 build (user direction: "add recruiting marshals for france and enemies as last phase of this or a new spec"). Gate authority: the same July-11 full-auth grant recorded in `docs/JEALOUSY_SPEC.md` §0.
> **Tests:** `tests/test_marshal_recruitment.py` (34) + 5 golden-corpus rows (`jv32-*`).

## 1. What it is

Nations with an authored candidate pool can **commission new marshals mid-campaign**. France reaches for its historical bench (Mortier, Grouchy, Suchet, Oudinot, Augereau, Marmont); the great powers reach for theirs (Austria: Schwarzenberg/Hiller/Liechtenstein · Russia: Bagration/Bennigsen/Dokhturov · Prussia: Blücher/Scharnhorst/Yorck · Britain: Wellesley/Paget). Pool presence is the feature gate.

**The courts' benches (S14k, October 28, 2026 — the user: "they should get armies or the ability to make them"; `SYSTEMS_REFERENCE.md` §160).** Every court that fought in the period now has a bench: the secondaries' (SF-RR4 — Spain, Sweden, Bavaria), and Portugal (Silveira), Saxony (Le Coq), Hesse (Emil), Hanover (Wallmoden, Alten), Holland (Janssens), the Kingdom of Italy (Fontanelli), Switzerland (Wattenwyl, Bachmann), and the one-general courts' second men — Denmark (Christian August), Naples (Philippsthal), the Ottomans (Alemdar, Yusuf Ziya). Saxony and Portugal also boot with their 1805 field corps (Zezschwitz, Bernardim Freire). **Sardinia and the Papal States keep their capital garrisons only** — neither fielded an army in the period — so no pool, no recruit. A save from before S14k gains the benches on load (`save_manager._backfill_court_benches`).

Player and AI share ONE executor path (**GR5**): `economy_executor._execute_recruit_marshal`, an **ADMIN_ACTIONS** verb (1 admin AP) like recruit/build.

## 2. The commission

- **Costs:** the candidate's authored gold price + 1 admin AP + an initial corps of **`RECRUIT_MARSHAL_CORPS` (5,000)** men drawn from the nation's **infantry manpower pool**. All three checks refuse honestly (message names the missing resource). The corps then pays normal strength-based upkeep (ES-3) — a new marshal is a standing cost, not free strength.
- **Arrival:** the nation's capital; if the capital has fallen, the richest still-held homeland province; no soil → refusal ("no soil on which to raise his corps").
- **Relationship seeds** apply **symmetrically** to marshals already in service (MC-3 convention). Pool-to-pool edges (Blücher↔Scharnhorst) are authored on BOTH entries so arrival order doesn't matter.
- The pool entry is consumed; a live-roster name collision refuses ("already serves").

## 3. Authoring contract (`marshal_pool` scenario key)

```json
"marshal_pool": { "France": [ {
    "name": "Grouchy", "personality": "literal",
    "skills": {"tactical": 7, ...}, "tactical_skill": 7,
    "trust": {"value": 75}, "cost": 4500,
    "biography": "...", "relationships": {"Murat": -1},
    "cavalry": false
} ] }
```

- Candidates are scenario-marshal entries WITHOUT `location`/`strength` (spawn-derived) plus a required positive-int `cost`.
- **The MC-4 personality boot guard extends to the pool:** a candidate authoring a retired/unknown personality hard-fails validation, and `create_marshal_from_data` raises at commission.
- Validator: `validate_scenario` checks the whole block (name presence, roster collision, cost, skill keys/ranges, seed ranges; seeds may reference roster ∪ pool names). See `MODDING_FORMAT.md`.
- Serialized on `WorldState.marshal_pool` (entries removed as commissioned; save-compatible with `.get()` default `{}`).

## 4. The AI rung (GR5)

`enemy_ai._pick_admin_action` **Priority 1.75** (after the ES-7 reward rung, before builds): commission the FIRST authored candidate (authored order = quality order) when

- at war, OR preparing its own design at `coerce`+ (AI-5), OR **called to arms** — another court's design priced at `coerce`+ against it, or Europe's reading of France naming it the target at `coerce`+ (S14k K3, `recruitment.court_called_to_arms`: armed neutrality, Switzerland in 1805, 1809 and 1813), AND
- it is not **a satellite serving its lord's war by its contingent** — a client whose every enemy is its lord's sends its men under the lord's flag (VD-C) and commissions nothing of its own; its bench is for a war of its own (S14k K4, `recruitment.satellite_serves_by_contingent`), AND
- standing roster `< AI_RECRUIT_MAX_STANDING` (3), AND
- treasury ≥ cost + `AI_RECRUIT_TREASURY_BUFFER` (1000), AND
- the shared `check_commission` gate passes (manpower, soil).

A court with no general at all runs this one rung through EA-7's `execute_commission_only` (its whole turn is skipped otherwise), so a bench is what gives a marshal-less court the ability to raise its first corps.

Austria replaces a lost Mack with Schwarzenberg; Russia calls up Bagration; Britain builds its expeditionary command. Live-verified in the 8-turn probe (Britain fielded Paget and Wellesley unprompted).

## 5. Player surfaces

- **Typed:** `commission Grouchy` / `recruit marshal Suchet` / `appoint Mortier to the marshalate`. Mock keyword branch runs BEFORE the troop-recruit branch and carries the `_mentions_pension` guard (corpus rows pin the family, incl. the negative guards).
- **UI:** the Generals screen (G) gains a **Commission a Marshal** view — candidate cards with `█░` skill bars, personality, biography, price/corps chips, honest availability (the same `check_commission` verdict the executor runs), and a [Commission] button issuing the typed command. Data rides `GET /marshal_overview` → `recruitment` block (`recruitment.build_recruitment_payload`).
- **Word of enemy commissions** reaches the player as a fog-ruled dispatch event (`enemy_marshal_commissioned`, partial_on_nation) + campaign log (`marshal_commissioned`, player-court entries only) + notification (`MARSHAL_COMMISSIONED`) for the player's own.

## 6. Systems ties (why it lives with Jealousy)

- **Glory ladder:** a commissioned marshal enters at 0 glory — nobody resents an unproven man (ties don't trigger); HE may develop grievances upward. His seeds can start him Rival with a peer (hair-trigger threshold — Grouchy arrives already cold toward Murat).
- **MC-2 skill tiers:** Rally/Intendance/Steward derive from his authored command/administration automatically (Suchet admin 9 = thrifty the day he arrives).
- **ES-7 expectations:** `battles_won` 0 → expectation 0; his duchy comes later — more marshals = more men who will one day want estates (the Cost of Success compounds).
- **W6-7 fates:** capture/death created roster attrition with no recovery path; the pool is the recovery path, both sides.

## 7. Constants (in-band tunable)

`RECRUIT_MARSHAL_CORPS = 5000` · `RECRUIT_MARSHAL_AP = 1` (admin) · `AI_RECRUIT_MAX_STANDING = 3` · `AI_RECRUIT_TREASURY_BUFFER = 1000` · authored costs 2,500–6,000g (the minor courts' 2,500–3,500).

## 8. Deliberately out (owned)

- **No marshal DEATH mechanics change** — the pool replenishes rosters; the fates pipeline (W6-7) is untouched.
- **No pool regeneration / era unlocks** — the bench is finite by design; a future content pass may add dated arrivals (owner: a future Marshal Content addendum gate, if ever).
- **No poaching / defection** — cross-nation recruitment is a Jealousy-gate-descendant idea at most; not promised anywhere player-facing.
