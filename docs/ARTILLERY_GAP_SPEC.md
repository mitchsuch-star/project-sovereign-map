# Artillery Arm — Filling the Gap (Spec)

> **Status:** ✅ **LANDED July 13, 2026** (user-directed: "all nations and bench, artillery more scarce, majors have more available; check that recruiting a marshal requires manpower; make the starting state favor France a bit and realistic"). What shipped + the two conscious divergences are in the **Landing note** directly below; the original proposal (§1–§9) is kept for reference.
> **Owner:** this doc. **Prerequisite eval:** the July 13, 2026 artillery reachability finding (below).
> **Golden rules in play:** GR5 (enemy AI uses the same systems), GR6 (LLM never touches mechanics — N/A here), GR8 (scale-ready), GR9 (no open-ended deferrals — every option below has a landing + measurement).

## Landing note (July 13, 2026)

**Shipped — the arm is reachable, scarce, majors-favoured, and France-first:**
- **Arm-aware manpower commission** (the "check required manpower" ask, done for all three arms). `recruitment.candidate_arm` / `corps_requirement` route a commission to its ARM-appropriate pool: infantry→infantry (5,000, unchanged), cavalry→**cavalry** pool (5,000 — fixes the pre-existing "cavalry drawn from infantry"), artillery→**artillery** pool (`RECRUIT_ARTILLERY_CORPS=3000`, the scarce arm). `check_commission` gates on that pool and `commission_marshal` draws from it. The authored artillery flag rides through `create_marshal_from_data` untouched; `build_recruitment_payload` now carries `arm`/`artillery`/per-arm `pools`; the validator gained an `artillery` boolean + cavalry/artillery mutual-exclusivity check.
- **Content — a gunner on every commissioning bench:** France **Marmont** (reflagged — his "artillery savant" bio is now true) **+ Senarmont**; Austria **Smola**; Russia **Kutaisov**; Prussia **Holtzendorff**; Britain **Shrapnel**.
- **Scarcity = the pools.** Artillery pools are authored small (France 10k, majors 5–6k, Britain 4k, minors 500–2k) and a battery costs 3,000, so majors raise guns readily and thin pools shut a battery out until they regenerate — "more scarce, majors have more available" falls out of the data, no new mechanic.
- **France favoured (realistic).** France fields artillery **first** (10k pool, 2× any other major), **most** (two gunners), and **cheapest** (4,500 vs 5,000–5,500) — French artillery superiority modelled as capacity + depth + price.
- Tests: `tests/test_artillery_arm.py` (14 — reachability, arm-aware draw/gate for all three arms, pool-gated scarcity, both-sides AI parity, mutual-exclusivity) + `test_marshal_recruitment.py` extended. Suite **13,075 / 3 skip**, ruff clean. The artillery COMBAT mechanics (bombardment, +damage, fort degradation, the triangle) are **unchanged** and already covered by `test_bombardment.py`/`test_artillery.py`; this pass only made the arm reachable, so no constant retune was needed.

**Two conscious divergences from a literal reading (flagged for the user):**
1. **"all nations" → all nations that can commission (the 5 bench powers).** The 15 minors have no `marshal_pool` bench at all, so they cannot raise artillery (or any marshal) — which is also historically right (minor states did not field independent grand batteries), and their tiny artillery pools would gate a battery anyway. Literal all-20 would mean authoring 15 new minor benches — a separate expansion, available on request.
2. **France's favour is on the BENCH, not an active starting battery.** An active artillery marshal at turn 1 would add ~4,000 men to France and shift a **blessed ES-3 economy anchor** (turn-1 upkeep 236g→252g) plus cascade into ~8 count/balance pins. Rewriting a blessed balance number as a side effect of an artillery build is not something to bury, so France's edge rides the bench (depth + price + pool) instead. If you want France to literally start with a battery on the board, it's a one-line add that shifts the France upkeep anchor ~16g — say the word.

**Open follow-ups (GR9-homed):** the Commission-bench card can show the arm (the payload now carries `arm`/`artillery`; a small Godot read); minor-nation benches for literal all-20; portraits for the five gunners (they use the gold-monogram fallback today).

---

## 1. Problem — the artillery arm is dead content in 1805

There are three unit arms — infantry, cavalry, artillery — with a full rock-paper-scissors around them (bombardment cracks forts, cavalry overruns guns, infantry squares stop cavalry, artillery breaks squares). **In the shipped 1805 campaign the artillery corner is unreachable.**

| Pool | Infantry | Cavalry | Artillery |
|---|---|---|---|
| Standing roster (21 marshals) | 20 | 1 (Murat) | **0** |
| Commission bench (17 candidates) | 16 | 1 (Paget) | **0** |
| **Whole campaign (38)** | **36** | **2** | **0** |

**Reachability trace (why it can never appear):**
1. **Roster + bench:** zero `"artillery": true` in `europe_1805.json`. The only artillery-flagged marshal in the entire codebase is **Drouot** (`marshal.py:1870`) — a legacy-Waterloo template absent from 1805.
2. **Commission factory:** `recruitment.build_recruitment_payload` (`recruitment.py:249`) and the commissioned-marshal construction read **`cavalry` only** — there is no `artillery` key read anywhere in `recruitment.py`. An authored `"artillery": true` on a bench candidate would be silently dropped.
3. **Recruit action:** `economy_executor._execute_recruit` (`economy_executor.py:318`) only *reinforces a marshal's existing arm*, so artillery troops can only be added to a marshal who is already artillery. Nobody is.

**The infrastructure is already built and stranded.** Every nation has an authored **artillery manpower pool** in `EUROPE_MANPOWER_POOLS` (France 10,000; majors 5,000–6,000; down to 500 for minors) that **regenerates every turn** (`get_artillery_regen_rate`) and is **never touched**. `combat.py` has artillery's +50% damage, bombardment (+50% / −15 morale, fort degradation), the cavalry counter, overwatch suppression, and the can't-move-and-fire penalty. `enemy_ai.py` has `_score_artillery_position` and square/artillery detection. **The whole system is wired and waiting for a single input: a marshal who carries the arm.**

## 2. What it costs to leave it dead

- **No siege dimension.** Nothing cracks fortifications by fire — forts degrade only through assault. Bombardment is a documented, tested action that no one can perform.
- **The tactical triangle collapses to two corners.** With no artillery, an infantry square is a *free, risk-free* counter to cavalry — the one cavalry marshal (Murat) is neutralized by any square with zero downside, and the AI's "no enemy artillery → safe to square" branch is *always* true.
- **`TACTICAL_TRIANGLE_SPEC.md` ships a mechanic players can't reach.** GR9: a system with no reachable input should be either made reachable or formally retired. This spec chooses *make reachable*.

## 3. Design goals

1. **Make the arm reachable** on both sides (GR5) with the smallest, safest change.
2. **Historical fidelity.** 1805 corps carried *integral* artillery; a *dedicated* gun formation is the Artillery Reserve / grand battery (Sénarmont at Friedland, Drouot's Guard reserve). So artillery should enter as its **own formation**, not by re-flagging a combined-arms corps commander.
3. **Use the stranded infrastructure** — the existing artillery manpower pools and regen, not new fields.
4. **Balance-safe & measured.** Reintroducing gun-cracking of forts and square-breaking is a real shift; land it in a measurable slice and escalate constants at a gate.

## 4. The one required code fix (prerequisite for every option)

Whatever content scope is chosen, the commission path must learn the artillery arm. This is small and self-contained:

1. **Commission construction reads the arm.** Wherever the commissioned `Marshal` is built (`economy_executor._execute_recruit_marshal` → `create_marshal_from_data`), pass `artillery=candidate.get("artillery", False)` alongside the existing `cavalry`. `marshal.py.__init__` already raises if both are set (mutual exclusivity), so authoring both hard-fails at boot — good.
2. **Display payload reads the arm.** `recruitment.build_recruitment_payload:249` adds `"artillery": bool(candidate.get("artillery", False))` next to `cavalry`, and the Generals/Commission card shows the arm (so "shown = applied").
3. **Artillery corps draws from the artillery pool.** A commissioned artillery marshal raises its starting corps from the nation's **artillery** manpower pool (already provisioned) at an artillery-appropriate size — proposal: **3,000** (guns + crews are smaller than a 5,000-man infantry corps). New constant `RECRUIT_ARTILLERY_CORPS = 3000` beside `RECRUIT_MARSHAL_CORPS`.
4. **Validator.** `modding/validator.py` marshal_pool schema accepts `artillery: bool` (mutually exclusive with `cavalry`); the existing MC-4 personality guard is untouched.
5. **AI parity (GR5):** the P1.75 commission rung (`recruitment.get_ai_commission`) already takes the first affordable bench candidate — confirm it will pick an artillery candidate and that `enemy_ai` values a standing artillery marshal (the scoring already exists). Add a both-sides test.

New-action checklist: **not** a new action — `recruit_marshal` already exists; this extends it with the artillery arm. Tests: `test_marshal_recruitment.py` gains artillery-commission coverage; a new `test_artillery_arm.py` pins reachability + both-sides parity + corps-from-artillery-pool.

## 5. Content — who fills the arm

### 5a. Generals who already fit the bill

| Marshal | Where | Fit | Action |
|---|---|---|---|
| **Marmont** | France bench | **Strong** — his bio already reads *"artillery savant"*; a trained artillerist who commanded the guns at Marengo. The flavor/mechanics mismatch the eval flagged. | Flag `"artillery": true`. Zero new content — just make the bio true. |
| Drouot | (legacy Waterloo only) | Canonical artillery marshal, but not in 1805. | Reference only; do not import. |

No **active** 1805 marshal is a natural dedicated-artillery fit — every standing corps (Ney, Davout, Soult…) is combined-arms by design (§3.2). So the active seed, if any, should be a *new* Artillery Reserve marshal, not a reflag.

### 5b. Bench additions (per option below)

Historical dedicated-artillery commanders available to author onto benches:
- **France:** Marmont (reflag), and/or **Sénarmont** (the Friedland massed battery), **Éblé** (artillery + bridging).
- **Russia:** **Kutaisov** (young artillery general, Borodino).
- **Austria:** **Smola** (artillery reserve commander).
- **Prussia:** a generic **Artillery Reserve** candidate (no marquee 1805 name).
- **Minors:** a generic Artillery Reserve candidate if their pool warrants it (most minor pools are 500–2,000 — enough for one small battery).

Each bench artillery candidate = the same schema as any pool candidate + `"artillery": true`, artillery-weighted skills (high `tactical`/`defense`, low `shock`), a period cost, and symmetric relationship seeds.

## 6. Balance & measurement

Introducing artillery changes two things materially: **forts become crackable by fire**, and **squares gain a hard counter**. Both are *intended* (they restore the designed triangle), but they need a look before they stand:

- **Measurement slice:** after the commission path + Marmont reflag land, run a scripted probe — (a) an artillery marshal bombards a fortified province → confirm fort degradation lands at a sane rate (not one-shot, not negligible); (b) artillery vs. an infantry square → confirm the square is punished but not deleted; (c) cavalry (Murat) vs. artillery → confirm guns are vulnerable when charged. Record the numbers.
- **Escalation:** the artillery damage / bombardment / fort-degradation constants live in `combat.py`; if the probe reads off, escalate the constants at a follow-up gate rather than shipping a fort-melting or pea-shooter arm.
- **AI (GR5):** verify the AI both *commissions* artillery when affordable (P1.75) and *uses* it (the `_score_artillery_position` path). An 8-turn AI probe should show at least one major fielding guns unprompted.

## 7. Scope options — the gate decision

All three include the §4 code fix. Pick the landing depth:

| Option | Content | Balance risk | When artillery appears |
|---|---|---|---|
| **A — Bench-only (recommended first landing)** | Reflag **Marmont** as artillery + add **one** artillery candidate to each major's bench (France/Austria/Russia/Prussia). | **Low** — artillery is *commissioned*, never standing; the AI fields it only after paying for it; historically clean (grand batteries are raised). | Only after a player/AI commissions it. |
| **B — Bench + one active seed** | Option A **+** seed **one active Artillery Reserve marshal for France** (and mirror for AI majors) so the arm is present at turn 1 and the AI starts with it. | **Medium** — the triangle goes live immediately; forts crackable from turn 1. | Turn 1, both sides. |
| **C — Broad** | Option B **+** artillery candidates on **every** bench incl. minors, so any nation can field guns. | **Higher** — widest surface; every minor's pool becomes live. | Turn 1 for majors, commissionable for all. |

**Recommendation:** **Option A first** — it unblocks the whole subsystem with the least balance exposure and the cleanest history (guns are *raised*, not standing), and it immediately makes Marmont's bio honest. Then, once §6 measurement is green, fast-follow **Option B's active seed** so the AI fields artillery from turn 1 and the triangle is live in ordinary play. Ambitious end-state, staged landing.

## 8. Open questions for the gate

1. **Which option (A / B / C)?** (Recommend A now, B next.)
2. **Active seed identity (if B/C):** a named **Sénarmont** as France's Artillery Reserve, or a generic *"Réserve d'Artillerie"* formation? (Recommend the named Sénarmont — matches the marquee-name treatment of the recruitment bench.)
3. **Artillery corps size:** confirm **3,000** (smaller than the 5,000 infantry corps) drawn from the artillery pool.
4. **Bench cost band** for artillery candidates (proposal: 4,000–5,500, in line with the existing specialist bench).

## 9. Landing checklist (once a scope is blessed)

- [ ] §4 code fix (commission reads `artillery`; corps from artillery pool; payload + card; validator; AI parity).
- [ ] §5 content per the chosen option (Marmont reflag is in every option).
- [ ] §6 measurement probe + recorded numbers; escalate constants if needed.
- [ ] `test_artillery_arm.py` (reachability, both-sides parity, corps-from-artillery-pool, mutual-exclusivity guard) + `test_marshal_recruitment.py` extension.
- [ ] Godot boot-smoke (the Commission card now shows an artillery arm) — standing `.gd`-touch rule if the card code changes.
- [ ] STATUS/ROADMAP + `SYSTEMS_REFERENCE.md` (§ tactical triangle now reachable) + `MODDING_FORMAT.md` (`artillery` pool key documented).
