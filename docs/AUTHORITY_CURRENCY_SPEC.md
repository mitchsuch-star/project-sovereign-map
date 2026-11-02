# Authority as a currency — the push and the pull (row AU)

**Status:** QUEUED November 1, 2026 by the user's word — **after row RE ("Affairs of State") and before S15 (the deploy)**: `docs/PRE_DEPLOY_PLAN.md` §2, `docs/ROADMAP.md`, `docs/STATUS.md` ▶ NEXT UP. **Nothing here is built. The gate (§4) runs first, in its own session; the build follows the user's rulings and is sized there.** This file is the row's owner (Rule 9): the brief, the survey of what authority is today, the gate's questions and the done-when.

## §0 The word

The user, November 1, 2026, at RE-H's review: *"we have to make authority a usable currency as well, assure that gets hit, it should be a push and pull — mark that for next after events; other uses for auth, even if it's events."*

Read as three asks:
1. **A currency** — standing is something the Emperor *spends on purpose*, not only a figure that erodes when he answers his marshals badly.
2. **It gets hit** — the pulls land on the measured boards in every campaign, so a Decline priced at three standing is a real price and a letter's "standing 100 → 97" is felt.
3. **Push and pull** — every sink has a source and every source a sink; the events ("Affairs of State", the moments, the Edicts) are a legitimate home for both.

## §1 What authority is today (the survey, November 1, 2026)

- **The store.** `AuthorityTracker.authority`, 0–100, starts at 100 (`backend/models/authority.py`, built against the "always trust the marshals" exploit). The affairs' grip floor is 71 and the aura's full line 85 (`moments.AUTHORITY_GRIP_FLOOR`, `affairs.bites`). The AI courts carry their own authority with `reforms.AI_AUTHORITY_FLOOR` 30 (Building Blocks: the same store, their values).
- **The pulls — what takes it.** The excessive-trust penalty on objections (−2 / −3 per ten-turn window, `check_excessive_trust`); an outnumbering loss or a capital lost (−5, once per battle); jealousy's refusals and petitions (−3 / −5, `jealousy.py`); the moments' and the affairs' Declines (−3 / −5 / −8, never below the floor — `moments._plan_authority`); laws priced in authority (`reforms.CURRENCIES`); the Decree priced in authority (RE-2).
- **The pushes — what gives it.** Balanced or firm answers to objections (+1 a response past five); an outnumbered win or a capital taken (+5); the imperial designs' rewards (Naples, `imperial_designs.py`); the Fontainebleau promise (`jealousy.py`); the Temple of Glory (1,500 gold for +3 — "a winner sits at 100").
- **What it does.** Obedience ×1.1 at 80 and above, ×0.9 under 50; trust gains halved under heavy trusting; defiance −10 % at 80 and above, +10 % under 50; the severity modifier; the threshold events at 70 / 50 / 30 (`SYSTEMS_REFERENCE.md` "Authority System").
- **Where the player reads it.** The dispatch's standing line, the letters' priced buttons ("standing 100 → 97"), the ledger.

## §2 The problem, measured

Every scripted and commanded board of the affairs' measure sits at **100 for forty turns** (`RECURRING_EVENTS_SPEC.md` §22.1 — the reason `bites` exists: a −5 at 100 is cosmetic, so the Arch-Chancellor's letter waits for a France below 85, and the Haiti letter had to be excused from that wait to appear at all). The passive board loses standing only by lapse (75 → 72 at T9 in `BASELINE_SERIES`'s attribution). The pulls are rare; the pushes are automatic (+1 for answering well) or a gold purchase. Authority is therefore **neither spent nor felt**: a price in standing is cheap at 100, invisible under the aura line, and nothing invites the Emperor to spend it deliberately.

## §3 The brief

- **Pushes — what standing buys.** Acts the Emperor takes *by authority alone*; candidates for the gate: overrule an objection without the trust cost; a decree by fiat where a law costs gold (`reforms.CURRENCIES` already prices some laws in authority — widen the catalogue); a court's compliance or a client's levy by prestige; a marshal's commission or a crown by the Emperor's word; a third button on a letter — "by my authority" — beside gold and refusal.
- **Pulls — what takes it, so it gets hit.** The events' Declines as today, plus consequences the player chose: a promise broken, a battle lost that he insisted on, a lie in the Moniteur caught out, a Senate remonstrance, a long absence from Paris. The aura line 85 is crossed **by design** in every campaign, not only by lapse.
- **Regrowth — the pull's answer.** Victories and treaties, the Temple, time at court, the coronation-class moments — so standing moves in a band and comes back by play, never by waiting alone.
- **The display.** The figure where the price is quoted and where it moves (the top bar or the dispatch's line — the gate decides); the dent shown on the morning it lands.
- **Building Blocks.** The AI courts' authority takes the same sinks and sources at their own values (`AI_AUTHORITY_FLOOR`); no France-literal in the engine.

## §4 The gate — first, in its own session

The S14c pattern: researchers (what Napoleon's standing historically bought and cost — the Senate and the plebiscites, the Legion of Honour, the Moniteur and the bulletins, the Tuileries court and the dukedoms; and the sycophancy exploit the tracker was built against), three designers, judges, the orchestrator's synthesis, then the user's rulings with recommended defaults.

**Questions for the user:** **Q1 the band** — where should standing live over forty turns (recommended 70–95, the aura line 85 crossed in every campaign); **Q2 the pushes** — which three acts standing buys first; **Q3 the pulls** — which consequences take it beyond the Declines; **Q4 regrowth** — how it comes back; **Q5 the display** — where the figure lives and how the dent shows; **Q6 the courts** — the same sinks and sources at their values.

## §5 Done-when (Rule 9)

- The gate record (§4's rulings) filled in this file; the build sized there (the estimate before the gate: the gate 0.5, the build 1.5–2.5 sessions).
- **The instrument:** the standing trace over forty turns on the measured arms (the sweep's passive board, the commanded arms, the roads — `tools/_affairs_measure.py` and `tools/ai_v_sweep.py` already carry the seeds) shows the band crossed, with at least one push and one pull observed per campaign; the letters' quotes land their full price above the floor on those arms.
- **Pins** named at the gate; `BASELINE_SERIES` re-pinned with its attribution if the series moves; the alarm untouched.
- **STATUS:** its own ▶ NEXT UP line from the gate's session; the rules in `SYSTEMS_REFERENCE.md` (a new §); the finds in `BUG_FIXES.md` §AU with the census's pillars.
