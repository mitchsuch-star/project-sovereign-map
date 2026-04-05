# Design Refinement

> **Design items and addons for evaluation.** Work here begins after `BUG_FIXES.md` is clear and playtesting confirms stability.
>
> **Last Updated:** April 5, 2026

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Player Feedback (Wave 3 remaining) | 7 | Ready for implementation |
| Territorial Promises (Wave 3) | 1 | Needs design gate |
| Gold Sink Options (B4) | 1 | Needs design gate |
| Wave 4 — New Features | 17 | Needs per-item approval |
| Wave 5 — Game Review Findings | 8 | Needs design gate |
| Jealousy System | 1 | Needs design gate |
| **Total** | **35** | |

---

## Ready for Implementation

These refine existing systems. No design gate needed.

### R119: Nations Remember Betrayal
- **Category:** Player Feedback
- **Summary:** Escalating betrayal tracking — nations penalize repeated broken agreements.
- **Details:** New `world.betrayal_history` dict. 1st offense -10, 2nd -20, 3rd+ -30 + AI hard reject. Half penalty for witness nations. Redemption: 20 honored treaty turns removes oldest betrayal.
- **Files:** `diplomacy.py`

### R131: Cooldown Pre-Check Warning
- **Category:** Player Feedback
- **Summary:** Warn player of proposal cooldowns before opening negotiation dialogue.
- **Details:** Pre-check cooldown before dialogue opens. Show remaining turns + Talleyrand message.
- **Files:** `diplomatic_executor.py`

### R129: Override Feedback in Dispatch
- **Category:** Player Feedback
- **Summary:** Add feedback when diplomatic override actions succeed/fail.
- **Details:** Success: +2 trust + dispatch note. Failure: +1 concern boost + dispatch note. Fix timing bug at diplomatic_defiance.py:741.
- **Files:** `diplomatic_defiance.py`, `dispatch.py`

### R128: Sabotage Consequence Feedback
- **Category:** Player Feedback
- **Summary:** Track and report sabotage outcomes with Talleyrand feedback.
- **Details:** Track in `world.sabotage_history`. Dispatch note next turn. Trust +3 if Talleyrand was correct.
- **Files:** `diplomatic_defiance.py`, `dispatch.py`

### R132: Vassal Loyalty Transparency
- **Category:** Player Feedback
- **Summary:** Real-time vassal loyalty deltas and trend tracking.
- **Details:** Lower warning threshold to 30. Show delta when |change| >= 2. Store `prev_loyalty`. Trend arrow in ledger.
- **Files:** `dispatch.py`, `vassal.py`, `diplomatic_ledger.py`

### R17d: DP Breakdown Display
- **Category:** QoL
- **Summary:** Show DP source/cost components in ledger.
- **Files:** `diplomatic_ledger.py`

### R17e: Relation Trend Arrows
- **Category:** QoL
- **Summary:** 3-turn history showing direction of relationships in ledger.
- **Files:** `diplomatic_ledger.py`

### R17f: Mission Progress Projection
- **Category:** QoL
- **Summary:** Estimated completion turn for active missions.
- **Files:** `diplomatic_ledger.py`

---

## Needs Design Gate

### R151: Territorial Promise Clauses
- **Category:** Diplomacy Feature
- **Summary:** New clause type — nations promise territorial cessions they don't yet control. Enables "France promises to help Prussia take Saxony in exchange for peace."
- **Details:** New `territorial_promise` clause, acceptance bonus, obligation tracking, reputation penalty if broken. Historically accurate to Napoleonic diplomacy.
- **Gates needed:** Obligation mechanics, AI understanding of promises, betrayal consequences.
- **Files:** `diplomacy.py`, `ai_diplomacy.py`

### Jealousy System (v3.1 spec)
- **Category:** Marshal Feature
- **Summary:** Glory Ladder targeting, personality expressions, escalation, confrontation popups.
- **Details:** Full spec at `docs/JEALOUSY_SPEC.md`. Core design settled. Top of ladder: +1 all core stats while #1. Defeats cost glory. DO NOT CODE WITHOUT USER APPROVAL.

---

## Wave 4 — Decide Gate (Per-Item Approval)

These are new feature designs. Each needs individual approval before implementation.

| ID | Item | Summary |
|----|------|---------|
| R22 | Marriage Alliances | Dynastic bonds: +20 rel, block war 5 turns, 3 DP |
| R32 | Peace Conferences | Multi-nation negotiations, 3 DP, +15 acceptance |
| R117 | Advisory Actionability | Advisory ends with executable options |
| R123 | Economic Strategy AI (P9) | Gold > 600 triggers subsidy offers, trade pressure |
| R124 | Diplomatic Isolation AI (P10) | Split enemy alliances with generous terms |
| R133 | Point of No Return Event | One-time Talleyrand popup at threat 40 |
| R28 | Talleyrand Voice Bank | 5-8 variants per situation type |
| R127 | Nation-Specific Intelligence | Per-nation personality lines in advisory |
| R24 | Treaty Signing Ceremonies | Talleyrand ceremony text on ratification |
| R25 | Vassal Personality Events | 3-4 random loyalty-gated events per game |
| R26 | Continental System Buff | Backend exists, needs player command + creative rebalance |
| R27 | Secret Treaties | Hidden treaties, 10%/turn discovery chance |
| R33 | Puppet Rulers | Named rulers with personality, events |
| R35 | Player Counter-Offer Terms | Player specifies clauses (Godot popup) |
| R36 | Personal Summits | Face-to-face meetings, +15 acceptance 3 turns |
| R59 | Literal Personality Triggers | Audit and wire unwired triggers |
| R118 | Enhanced Acceptance Preview | Top 3 positive/negative components + Talleyrand hints |

---

## Gold Sink Options (B4 Balance — Design Gate)

**Priority:** MEDIUM | **Phase:** Pre-EA refinement

Gold accumulation is a known design gap (~700g/turn income vs ~250g upkeep). Manpower-gated recruitment means gold piles up with no meaningful spending options. This section tracks candidate gold sinks for evaluation.

**Forced march REJECTED** — trivializes cavalry's 2-region movement advantage, which is cavalry's core identity.

### Leading Candidate: Province Development
- **Cost:** Variable (200-500g per investment)
- **Effect:** Invest gold in controlled region to boost supply cap, income, or repair war damage faster
- **Design appeal:** Creates invest-now-vs-save tension, rewards holding territory, ties gold to strategic positioning
- **Needs:** Investment tiers, per-region cooldown, diminishing returns formula, AI investment priority

### Other Candidates (evaluate after Province Development)

| Option | Cost | Effect | Notes |
|--------|------|--------|-------|
| Diplomatic gifts/bribes | 200g | +5 relation (once/turn/nation) | Gold becomes diplomacy tool |
| Mercenary garrisons | 400g | Defensive garrison without stationing marshal | Frees marshals for offense |
| Recruitment bounties | 300g | Double manpower regen for 1 turn | Accelerates rebuilding |

---

## Enemy AP Rebalancing (Deferred — Post Full Map)

**Priority:** LOW | **Phase:** After full 1805 map implementation

Enemy AI action budget (currently 4 paid AP per nation) may need rebalancing once the full map is implemented with all nations, regions, and marshal counts at scale. Current 4-nation, 19-region map doesn't stress the action economy the same way a full campaign will. Revisit AP values, per-nation scaling, and aggregate action counts after full map playtesting.

---

## Wave 5 — Game Review Findings (Design Gate)

Cross-system findings from comprehensive review. Needs design gate as a batch.

| ID | Item | Summary |
|----|------|---------|
| R152 | Authority System UI Visibility | Authority impact not visible enough to players |
| R153 | Literal Personality Triggers | Personality-specific event triggers |
| R154 | Combat Morale Spiral | Morale death spiral needs circuit breaker |
| R155 | AI Proposal Personality Voice | AI proposals lack personality flavor |
| R156 | Diplomacy Strategic Optionality | Diplomacy feels optional vs military path |
| R157 | Talleyrand Voice Depth | Talleyrand responses feel monotone |
| R158 | NL Parser Confidence Feedback | Show parse confidence to player |
| R159 | Information Screen Teaching | Screens don't teach mechanics |

---

## Source Documents (Archived Reference)

| Document | Items Moved Here |
|----------|-----------------|
| `docs/DIPLO_REFINEMENT.md` | Wave 3-5 open items, all R-IDs |
| `docs/DIPLOMACY_DESIGN_FIXES.md` | Design discussion items |
| `docs/JEALOUSY_SPEC.md` | Jealousy pointer (spec kept as-is) |
