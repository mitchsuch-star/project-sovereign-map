# MC-V — Personality-Kit Assurance + Enemy-AI-per-Personality Evaluation (July 10, 2026)

> **Status:** LANDED July 10, 2026. The eval addendum the gate memo §6.7 required. Companion to `docs/MARSHAL_CONTENT_PASS_SPEC.md` §10 (MC-V landing record) and the routed findings in `docs/BUG_FIXES.md` §"MC-V Enemy-AI Personality Findings".
> **Pins:** `tests/test_mc_personality_assurance.py` (30). Seam-level enemy-side ability pins are owned by `tests/test_marshal_content_mc1b_t1_abilities.py` (memo §6.2); this eval adds the both-sides assurance + observed AI-decision layer.
> **Method:** a four-lens code audit (personality-grant seams / enemy-AI decision tree / enemy-side ability GR5 paths / test idioms) grounded seam-by-seam against master `b2eba27`, then codified as regression pins.

---

## 0. Verdict in one line

Every personality **combat mechanic** is GR5-clean — it reads `self.personality` (or an ability name on the combatant) and fires identically for a player-nation and an enemy-nation marshal through the shared `get_attack_modifier` / `get_defense_modifier` / `resolve_battle` / `_execute_recruit` paths. But at the **decision layer** the enemy AI expresses only **two** archetypes: `_get_effective_personality` aliases literal→cautious for every AI-controlled marshal, so enemy literals (Mack, Buxhowden) play as cautious clones; and three literal grants (Precision Execution, the ambiguity combat buff, the 1-AP order discount) never reach an enemy marshal because their only invocation is player-gated. Nothing is silently broken — the asymmetries are all either by-nature (trust/AP/scouting are player economies) or documented design (literal→cautious). They are pinned as known behavior and routed for a decision at the MC exit review / Jealousy gate.

---

## 1. Half (a) — personality-kit assurance (both sides)

**Confirmed BOTH-SIDES (pinned as a standing regression gate):**

| Kit | Grant | Seam | Both-sides proof |
|---|---|---|---|
| Aggressive | +15% base attack (+5% aggr-stance, +5% drill) | `personality_modifiers.get_attack_modifier_for_personality`, folded at `marshal.py:927` | reads `self.personality`; `combat.py:352` calls `attacker.get_attack_modifier` with no side branch |
| Aggressive | recklessness +5/10/15/20% + escalation + turn-start auto-charge | `marshal.py:711/936`, `combat.py:837`, `world_state.py:8619` (iterates all marshals) | gate = `is_reckless_cavalry` (cavalry ∧ aggressive) on `self` |
| Cautious | −10% bad-odds attack / +10% outnumbered defense / +5% defensive-stance | `marshal.py:1022` → `get_defense_modifier_for_personality` | `combat.py:498` calls `defender.get_defense_modifier` with no side branch |
| Cautious | counter-punch free attack | grant `combat.py:650/669/684`; consume `combat_executor.py:2446`; AI reaches it `enemy_ai.py:1665` | grant + consume both key `personality=='cautious'` on the combatant |
| Cautious | fortify +3%/turn, +5% instant, cap 12% (aggr cap 8%) | `personality_modifiers` helpers; growth `world_state._process_tactical_states` (ungated loop) | helpers are pure functions of the personality string |
| Literal | Immovable +15% defense while holding | `get_defense_modifier_for_personality` (`hold_position_defense_bonus`) | reads `self.holding_position` + `self.personality` |

**PLAYER-ONLY IN EFFECT (pinned as known behavior; routed MC-V-1):**

- **Literal Precision Execution (+1 all skills) and the ambiguity combat buff (+15% atk/def).** The buff FUNCTION `meta_executor._apply_grouchy_ambiguity_buff` is GR5-clean (operates on any `marshal`), but its **only** caller is `executor.py:1254`, gated on `is_player_action_check`. There is no enemy-AI invocation anywhere. An enemy literal marshal that takes a full AI turn carries no Precision Execution (pinned: `test_precision_execution_never_reaches_enemy_literal_via_ai`).
- **The literal 1-AP strategic-order discount.** `strategic_executor.py:1135` computes `strategic_cost = 1` for literal symmetrically, but only the player command path charges AP; enemy strategic execution runs with `_strategic_execution=True` and bypasses AP entirely. No enemy-side surface exists (the player-facing 1-vs-2 AP discount is pinned).
- **Literal completion +5 trust / cautious +1 scout range / cavalry restlessness −3 trust** — player-only by the nature of trust and scouting (the enemy is omniscient and never scouts). Not combat grants; noted for completeness, not routed.

**Dead constants (no consumer):** the personality trust-bonus constants in `personality_modifiers.py:31-75` (`attack_order_trust_bonus`, `successful_attack_trust_bonus`, `fortify_defend_trust_bonus`, …) have **zero** readers in a full-tree grep. No behavior to pin. Routed as cleanup (MC-V-3).

---

## 2. Half (b) — enemy-AI-per-personality evaluation

**Per-personality verdict:**

- **Aggressive — fully realized.** Lower attack threshold (0.7 vs 1.3), advance-toward-enemy (P7), drill-for-shock (P6), earlier turn order (−10 priority), +15 against-odds strategic bonus, capital-assault-while-encircled, 0.8 homeland recapture. It plays its label. No finding.
- **Cautious — moderately realized.** Higher attack threshold (1.3), defensive-stance/fortify reflex (P3/P5/P8), fall-back-when-threatened (P7). But it does **not husband force** — it still assaults garrisons and advances after one idle turn. "Declines bad field odds" is true; "preserves the overall army" is not. Net-new behavior, not a bug. Informational (MC-V-4).
- **Literal — collapsed.** `enemy_ai._get_effective_personality` (`:398`) converts literal→cautious for every AI-controlled marshal, *before* any table lookup. So `ATTACK_THRESHOLDS["literal"]`, `MOOD_VARIANCE["literal"]`, `BASE_SCORES["literal"]`, and the `decay_config["literal"]` row are **dead code** for enemy marshals. The shipped roster gives **Mack** (Swabia), a Bavarian, and a Russian the `literal` type; every one plays as a generic cautious clone. This is documented design in the docstring ("losing literal buffs IS the consequence of going autonomous"), but that rationale was written for *autonomous player* marshals — it was never a decision about scenario-authored enemy literals, and it sits in tension with MC-4's "personality = character, zero exceptions" canonization on the enemy side. **Headline routed finding (MC-V-2).**
- **Economy — personality-blind.** `_pick_admin_action` / `execute_admin_phase` choose recruit/build/repair/endow purely on treasury and strength shortfall — no personality read. May be acceptable (recruitment is a nation-level, not marshal-character, action). Informational (MC-V-5).

**Dead table rows (MC-V-3):** `balanced`/`loyal` rows persist in the four AI constant dicts (`ATTACK_THRESHOLDS`, `MOOD_VARIANCE`, `BASE_SCORES`, `ENCIRCLEMENT_TOLERANCE`) after MC-4 retired both types; combined with the dead `literal` rows (MC-V-2), four of five rows never drive distinct behavior for a shipped personality. Cleanup candidate — but note MC-4 deliberately kept the runtime `balanced` fallback as a save-compat floor; `.get(personality, default)` already covers a missing row, so deletion is behavior-neutral.

**Personality-differentiation pins (all deterministic):** `_get_effective_personality` aliasing (enemy literal → cautious; player literal preserved unless autonomous); the mood-adjusted attack threshold ordering (aggressive < 1.0 < cautious, and enemy literal == enemy cautious); and one observed full-turn divergence — at ratio 0.9 an aggressive enemy attacks (the French target bleeds) while a cautious OR literal enemy declines (`test_aggressive_seeks_battle_where_cautious_and_literal_hold`).

---

## 3. Enemy-side MC-1 abilities — the AI exercises them live

All three key off `marshal.ability["name"]` on the combatant, with **no** `is_player_action` / `player_nation` gate, and the AI runs every action through the same executor (`enemy_ai.py:768` combat, `:4713` admin). Seam pins are owned by mc1b (§6.2); MC-V pins the enemy-controlled / AI-path angle:

- **Habsburg Resolve (Charles, rout threshold 15).** On any enemy-phase battle Charles loses, his personal threshold keeps him on the field in the (15, 25] morale band where a non-Charles cautious defender routs. No reachability caveat (a front-line Austrian army takes battle damage). Pinned: `test_enemy_charles_holds_where_others_rout`.
- **The Old Fox (Kutuzov, pursuit + attrition halved).** Fires when AI Kutuzov is the routed defender (pursuit 5,000 → 2,500, halved *after* the attacker's bonus) and on both his voluntary and forced retreats (march attrition ×0.5). Caveat: the pursuit-halving is only *observable* against an attacker that actually owns a pursuit ability (by design — otherwise `pursuit_damage == 0`). Pinned: `test_enemy_kutuzov_pursuit_halved_when_player_routs_him`, `test_enemy_kutuzov_retreat_attrition_halved`.
- **Shorncliffe System (Moore, recruit morale floor 60).** The AI recruit action dict `{"action":"recruit","marshal":"Moore"}` carries into the same `_execute_recruit`; the floor applies (30k@100 + 10k@60 → 90). Caveat (live-frequency only, not a gating bug): the AI recruits only for a marshal *below* its strength threshold, and island-bound Moore must be shipped to the Continent and bloodied before Britain's admin phase ever targets him. Pinned: `test_shorncliffe_floor_on_ai_recruit_dict`.

---

## 4. Routed findings (→ `docs/BUG_FIXES.md` §"MC-V Enemy-AI Personality Findings")

| ID | Pri | Finding | Disposition |
|----|-----|---------|-------------|
| MC-V-2 | P3 (design) | Enemy literal AI is behaviorally identical to cautious (`_get_effective_personality` alias); enemy literals never play as themselves | Gate decision at the MC exit review / Jealousy v3.1 gate: give literal a distinct enemy profile, OR formally accept a two-archetype enemy AI and delete the dead rows |
| MC-V-1 | P4 | Literal Precision-Execution / ambiguity buff / 1-AP discount never reach an enemy literal (player-gated invocation) | Accept (enemy literals route through the AI decision path, not the command parser) or wire an AI-side equivalent — decide with MC-V-2 |
| MC-V-3 | P4 | Dead `balanced`/`loyal`/`literal` rows in the 4 AI constant dicts + 6 dead trust-bonus constants in `personality_modifiers.py` | Behavior-neutral cleanup; keep the `balanced` fallback per MC-4 save-compat |
| MC-V-4 | P4 | Cautious enemy AI declines bad field odds but does not husband overall force (still assaults garrisons / advances after 1 idle turn) | Net-new behavior, not a bug; candidate for a future AI depth pass |
| MC-V-5 | P4 | Enemy economy/recruitment is personality-blind | Likely acceptable (nation-level action); noted |

None is a forced fix — MC-V is an assurance + evaluation slice (route, don't fix), consistent with the §8 capstone discipline. The headline decision (MC-V-2) belongs to the MC exit review or the Jealousy v3.1 gate.
