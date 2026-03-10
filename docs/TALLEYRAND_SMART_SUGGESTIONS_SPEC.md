# TALLEYRAND_SMART_SUGGESTIONS_SPEC.md — v1.0

> **Purpose:** This is a standalone spec for review. After approval, save to `docs/TALLEYRAND_SMART_SUGGESTIONS_SPEC.md` and implement.

---

## 1. Problem Statement

In Project Sovereign Map (Napoleonic strategy game), the player's diplomat **Talleyrand** suggests treaty terms when the player initiates diplomacy. Currently, `generate_suggested_terms()` in `backend/game_logic/diplomatic_templates.py:1208` builds terms using only two variables:

- `war_score` — France's military advantage (-100 to +100)
- `relation` — bilateral relation value

**Result:** Every deal for a given war_score looks identical regardless of target nation. Proposing peace to rich Britain looks the same as proposing peace to broke Saxony. The existing code ignores:

1. **Nation economics** — Saxony (200g treasury) vs Britain (1500g treasury)
2. **Territorial desires** — Prussia covets Saxony, Austria wants Bavaria back
3. **Existing acceptance bonuses** — `SPECIAL_BONUSES` dict in `diplomacy.py:128` gives +10 for offering Saxony to Prussia, +8 for Bavaria to Austria, +10 for protection to Saxony — but `generate_suggested_terms()` never checks this dict
4. **Smart territory ranking** — `rank_cession_candidates()` at `diplomatic_templates.py:1314` ranks regions by adjacency/emptiness/income — but is never called by auto-suggestions
5. **Diplomat personality** — hawk (Castlereagh), schemer (Metternich), dove (Einsiedel) — no effect on suggested terms
6. **Explanatory commentary** — Talleyrand never explains WHY specific terms were chosen

**Goal:** Make every deal feel crafted by a master diplomat who understands each nation's desires, economics, and strategic position. Add `talleyrand_commentary` to explain reasoning.

---

## 2. Game Data Reference

### 2a. Nations (starting state)

| Nation | Gold | Regions (starting) | Income | Diplomat | Personality |
|--------|------|---------------------|--------|----------|-------------|
| France | 800g | Paris(300), Belgium(100), Lyon(200), Milan(150), Marseille(150), Brittany(50), Bordeaux(50), Normandy(100) | ~1100g | Talleyrand | schemer, skill 10 |
| Britain | 1500g | Netherlands(50), Waterloo(50), Hanover(100) | ~200g | Castlereagh | hawk, skill 7 |
| Prussia | 800g | Berlin(300), Rhineland(100) | ~400g | Hardenberg | hawk, skill 6 |
| Austria | 600g | Vienna(300), Bavaria(100), Bohemia(150), Tyrol(100) | ~650g | Metternich | schemer, skill 9 |
| Saxony | 200g | Dresden(100), Saxony(150) | ~250g | Einsiedel | dove, skill 4 |

Source: `backend/models/world_state.py:108` (gold), `backend/models/region.py:328` (REGIONS_DATA), `backend/models/diplomat.py` (diplomats)

### 2b. Existing Acceptance Bonuses (`diplomacy.py:128`)

```python
SPECIAL_BONUSES = {
    "Prussia": {"territory_saxony": 10},      # +10 if Saxony offered
    "Austria": {"territory_bavaria": 8},       # +8 if Bavaria offered
    "Britain": {"continental_system_lifted": 15},  # NOT WORKING — ignore
    "Saxony": {"protection_promised": 10},     # +10 if protection promised
}
```

These bonuses are checked in `calculate_acceptance()` at `diplomacy.py:704` but **never leveraged** when building suggested terms.

### 2c. Sweetener/Demand Values (`diplomacy.py:207`)

```python
SWEETENER_VALUES = {
    "gold_lump": 1/100,      # +1 per 100g
    "gold_per_turn": 3/100,  # +3 per 100g/turn
    "ap_per_turn": 18,       # +18 per AP (recently buffed from +8)
    "territory_cede": 8,     # +8 per region
    "protection": 5,         # +5 flat
    "open_borders": 3,       # +3 flat
}
SWEETENER_CAP = 40
```

### 2d. Game Situation Buckets (`diplomatic_dialogue.py:254`)

`get_game_bucket(target_nation, world)` returns one of 8 strings:
- At war: `winning_comfortably` (>30), `winning_slightly` (>0), `stalemate` (>-10), `losing_slightly` (>-30), `losing_badly`
- At peace: `friendly` (>20 relation), `neutral` (>-20), `hostile`

### 2e. Existing `rank_cession_candidates()` (`diplomatic_templates.py:1314`)

Already exists, never used by auto-suggestions. Ranks player regions for cession:
- Border regions adjacent to target nation first
- Empty regions (no buildings) preferred
- Cheaper regions preferred
- Capital excluded
- Returns `[[region_name, reason_text], ...]` sorted best-to-cede first

### 2f. AI Nation Desires (`ai_diplomacy.py:60`)

```python
NATION_DESIRES = {
    "Prussia": [territory(Saxony), territory(any), gold_lump(500)],
    "Austria": [open_borders, protection, gold_per_turn(100)],
    "Britain": [gold_lump(800), gold_lump(500), territory],
    "Saxony": [protection, gold_per_turn(50)],
}
```

Used for AI counter-offers. Talleyrand should mirror this knowledge when building player deals.

---

## 3. Design: Nation Desire Profiles

Add `NATION_DESIRE_PROFILES` to `diplomatic_templates.py`. Defines what Talleyrand knows about each nation — drives both term selection and commentary.

```python
NATION_DESIRE_PROFILES = {
    "Prussia": {
        "covets_regions": ["Saxony", "Dresden"],
        "values_gold": "low",          # 800g — prefers territory over gold
        "values_territory": "high",
        "values_ap": "medium",
        "diplomatic_lever": "ambition",
        "weakness": "overextension",
    },
    "Austria": {
        "covets_regions": ["Bavaria", "Tyrol", "Bohemia"],
        "values_gold": "medium",       # 600g — appreciates gold
        "values_territory": "high",
        "values_ap": "low",            # Conservative, doesn't need extra actions
        "diplomatic_lever": "stability",
        "weakness": "pride",
    },
    "Britain": {
        "covets_regions": ["Netherlands", "Hanover"],
        "values_gold": "low",          # 1500g — richest, gold means little
        "values_territory": "medium",
        "values_ap": "medium",
        "diplomatic_lever": "trade",
        "weakness": "isolation",
    },
    "Saxony": {
        "covets_regions": ["Saxony", "Dresden"],
        "values_gold": "high",         # 200g — desperately poor
        "values_territory": "low",     # Too small to absorb more
        "values_ap": "high",           # Extra actions transform small nations
        "diplomatic_lever": "survival",
        "weakness": "desperation",
    },
}
```

**Gold scale effects:**
- `"high"` → gold sweetener values multiplied by 1.5 (poor nations appreciate it more)
- `"medium"` → no change
- `"low"` → gold sweetener values multiplied by 0.5 (rich nations barely notice)

---

## 4. Design: 5-Stage Suggestion Pipeline

Replace the body of `generate_suggested_terms()` with a 5-stage pipeline. **Function signature unchanged** — all callers continue working.

### Stage 1: Base Terms

Extract existing `generate_suggested_terms()` body into `_build_base_terms()`. No logic changes. Returns the same terms dict the current function produces (sweeteners, demands, clauses based on war_score/relation thresholds).

### Stage 2: Nation-Specific Clause Injection

After Stage 1, apply nation-aware modifications:

**Territory sweeteners (when base terms include territory_cede):**
- Check if target's `covets_regions` overlap with France's controlled regions
- If yes → replace generic territory_cede with the coveted region (set context tag `"coveted_territory_offered"`)
- If no → call `rank_cession_candidates(world, "France", target_nation)` for smart selection (set context tag `"smart_cession"`)
- Capital (Paris) excluded by both paths

**Territory demands (when base terms include territory demands):**
- Find target regions that border French territory (strategic buffer zones)
- Exclude target's capital
- Replace generic demand with specific border region (set context tag `"border_territory_demanded"`)

**Gold calibration by `values_gold`:**
- `"high"` → multiply gold sweetener values by 1.5; set tag `"gold_for_poor"` if no more significant tag
- `"low"` → multiply gold sweetener values by 0.5; set tag `"gold_useless"` if gold removed/reduced

**Protection clause:**
- If `diplomatic_lever == "survival"` (Saxony) AND proposal_type is peace/alliance → add `"protection_promised"` clause
- Worth +10 acceptance (from `SPECIAL_BONUSES`), costs France nothing
- Set tag `"protection_offered"`

**AP calibration by `values_ap`:**
- `"high"` → include AP sweetener at war_score < -30 (instead of current -50 threshold)
- `"low"` → skip AP sweetener unless war_score < -60
- Set tag `"ap_for_weak"` when added

### Stage 3: Economic Reality Check

Validate terms against actual game economy:
- Gold lump offers: capped at 25% of France's treasury (`world.nation_gold["France"]`)
- Gold per turn offers: capped at 20% of France's region income (`world.calculate_turn_income("France")["income"]`)
- Gold per turn demands: capped at 50% of target's region income
- Territory offers: verify France controls the specified region
- Territory demands: verify target controls the specified region
- All values forced to `int()`

### Stage 4: Talleyrand Commentary

Select `talleyrand_commentary` string based on the context tags accumulated in Stage 2.

**Priority order** (most significant first):
1. `"coveted_territory_offered"` — offering territory the target specifically desires
2. `"border_territory_demanded"` — demanding strategic buffer territory
3. `"gold_for_poor"` — gold sweetener for economically weak nation
4. `"gold_useless"` — skipped gold for rich nation
5. `"protection_offered"` — offering protection to vulnerable nation
6. `"ap_for_weak"` — AP sweetener for small power
7. `"smart_cession"` — rank_cession_candidates chose optimal region
8. `"desperate_terms"` — fallback when losing badly (war_score < -30)
9. `"dominant_terms"` — fallback when winning comfortably (war_score > 30)
10. `"neutral_deal"` — fallback, standard terms

Lookup: `TALLEYRAND_COMMENTARY[(nation, tag)]` → `TALLEYRAND_COMMENTARY[("_default", tag)]` → hardcoded fallback.

### Stage 5: Return

Add `terms["talleyrand_commentary"] = commentary` and return. No other changes to the return dict structure.

---

## 5. Commentary String Pool

~50 strings: 5 per nation (4 nations = 20) + 10 defaults + extras. Stored as `TALLEYRAND_COMMENTARY` dict in `diplomatic_templates.py`.

### Prussia (hawk diplomat: Hardenberg)
| Context Tag | Commentary |
|-------------|-----------|
| `coveted_territory_offered` | "Saxony is the prize Hardenberg dreams of. Offering it buys more than gold ever could." |
| `gold_useless` | "Prussia's treasury is adequate — they desire land, not coin. I've weighted the offer accordingly." |
| `border_territory_demanded` | "The Rhineland gives us a buffer against Prussian ambition. A wise demand." |
| `dominant_terms` | "Hardenberg will bristle, but Prussia is in no position to refuse. Press the advantage." |
| `neutral_deal` | "A straightforward arrangement. Hardenberg is practical — he'll weigh the terms honestly." |

### Austria (schemer diplomat: Metternich)
| Context Tag | Commentary |
|-------------|-----------|
| `coveted_territory_offered` | "Bavaria is Austria's natural sphere. Returning it costs us little and buys Metternich's goodwill." |
| `gold_for_poor` | "Vienna's treasury grows thin after years of war. Gold per turn steadies their hand — and their loyalty." |
| `protection_offered` | "A guarantee of protection appeals to Austrian caution. Metternich values stability above all." |
| `desperate_terms` | "Metternich is a schemer — even generous terms may not satisfy him. But we must try." |
| `neutral_deal` | "Metternich will study every clause for hidden advantage. I've kept the terms clean." |

### Britain (hawk diplomat: Castlereagh)
| Context Tag | Commentary |
|-------------|-----------|
| `gold_useless` | "Britain's coffers overflow — offering gold insults Castlereagh. Territory speaks louder." |
| `coveted_territory_offered` | "The Netherlands secures Britain's continental foothold. Castlereagh values it above gold." |
| `dominant_terms` | "Britain's continental army is small. Castlereagh knows his position — he'll accept reasonable terms." |
| `desperate_terms` | "Castlereagh drives a hard bargain. I've included everything short of Paris itself." |
| `neutral_deal` | "An island nation with continental ambitions. This arrangement serves both parties' interests." |

### Saxony (dove diplomat: Einsiedel)
| Context Tag | Commentary |
|-------------|-----------|
| `gold_for_poor` | "Saxony's treasury is nearly empty. Even modest gold buys Einsiedel's eternal gratitude." |
| `protection_offered` | "Saxony lives in fear of Prussian annexation. A French guarantee is worth more than gold to them." |
| `ap_for_weak` | "An extra action each turn transforms a small nation's capabilities. Einsiedel will understand this." |
| `coveted_territory_offered` | "Einsiedel cares only for the survival of his homeland. Territorial guarantees speak loudest." |
| `neutral_deal` | "A small nation, easily satisfied. Einsiedel will accept any arrangement that preserves Saxony." |

### Defaults (any nation)
| Context Tag | Commentary |
|-------------|-----------|
| `coveted_territory_offered` | "I've included territory they particularly desire. It should tip the balance in our favor." |
| `gold_for_poor` | "Their treasury is strained. Gold speaks loudly to those who lack it." |
| `gold_useless` | "Gold would be wasted here — I've substituted something they actually value." |
| `smart_cession` | "I've selected our least valuable border territory for cession. We lose little of strategic worth." |
| `desperate_terms` | "We are not in a position to be choosy, Sire. I've assembled the most persuasive package possible." |
| `dominant_terms` | "They have little choice but to accept. I've kept the demands firm but not humiliating." |
| `neutral_deal` | "Standard terms, Sire. Neither generous nor harsh — a foundation for negotiation." |
| `protection_offered` | "A guarantee of protection costs us nothing but obligation. For them, it means survival." |
| `ap_for_weak` | "An extra action per turn is transformative for a smaller power. They will value this highly." |
| `border_territory_demanded` | "Border territory provides strategic depth. A prudent demand." |

---

## 6. Wiring: Commentary into Popup

### Backend wiring (1-line change)

In `_enrich_proposal_summary()` at `diplomatic_dialogue.py:384`, after terms are extracted:

```python
# After line where terms are obtained (~line 400):
dialogue["talleyrand_commentary"] = terms.get("talleyrand_commentary", "")
```

This function already builds the popup data dict. The new key passes through the existing popup passthrough system (`_include_popup_passthroughs()` in `main.py`) — no changes to `main.py` needed.

### Frontend display (future Godot task, not in this implementation)

In `proposal_confirm_popup.gd`, add a `RichTextLabel` for `talleyrand_commentary` below the terms summary. Italicized, in Talleyrand's voice color (`#d9c08c`). The backend data will be available immediately.

---

## 7. Files to Modify

| # | File | Change | Risk |
|---|------|--------|------|
| 1 | `backend/game_logic/diplomatic_templates.py` | Add `NATION_DESIRE_PROFILES` dict, `TALLEYRAND_COMMENTARY` dict (~50 strings), rewrite `generate_suggested_terms()` as 5-stage pipeline, add 4 helper functions | MEDIUM — core suggestion function |
| 2 | `backend/game_logic/diplomatic_dialogue.py` | Add 1 line in `_enrich_proposal_summary()` to extract commentary | LOW |
| 3 | `tests/test_bugfix_proposal_flow.py` | Add Section 14: ~18 smart suggestion tests | N/A |

### Files NOT modified
- `backend/game_logic/diplomacy.py` — acceptance formula, SWEETENER_VALUES, SPECIAL_BONUSES unchanged
- `backend/game_logic/ai_diplomacy.py` — AI counter-offer logic unchanged
- `backend/main.py` — popup passthroughs already forward all dialogue fields
- `backend/models/world_state.py` — no new serialized fields
- `backend/commands/executor.py` — calls `generate_suggested_terms()` unchanged
- No Godot files modified (commentary passes through existing system)

---

## 8. Implementation Detail: Rewritten `generate_suggested_terms()`

```python
def generate_suggested_terms(target_nation: str, proposal_type: str, world) -> Dict:
    """Generate smart treaty terms based on game state AND nation-specific knowledge.

    5-stage pipeline:
      1. Base terms (war_score/relation thresholds)
      2. Nation-specific clause injection (coveted territory, gold calibration, protection)
      3. Economic reality check (cap offers/demands to feasible levels)
      4. Talleyrand commentary (explain WHY these terms)
      5. Return
    """
    from backend.game_logic.diplomacy import get_war_score_for, SPECIAL_BONUSES
    from backend.models.region import NATION_CAPITALS

    war_score = get_war_score_for(world, "France", target_nation)

    # --- Stage 1: Base terms ---
    terms = _build_base_terms(target_nation, proposal_type, world)

    # --- Stage 2: Nation-specific injection ---
    context_tags = []
    profile = NATION_DESIRE_PROFILES.get(target_nation, {})

    # 2a. Territory sweeteners: prefer coveted regions
    if any(s.get("type") == "territory_cede" for s in terms.get("sweeteners", [])):
        coveted = [r for r in profile.get("covets_regions", [])
                   if r in world.get_nation_regions("France")]
        if coveted:
            terms["sweeteners"] = [s for s in terms["sweeteners"]
                                   if s.get("type") != "territory_cede"]
            terms["sweeteners"].append(
                {"type": "territory_cede", "value": 1, "regions": [coveted[0]]})
            context_tags.append("coveted_territory_offered")
        else:
            candidates = rank_cession_candidates(world, "France", target_nation)
            if candidates:
                terms["sweeteners"] = [s for s in terms["sweeteners"]
                                       if s.get("type") != "territory_cede"]
                terms["sweeteners"].append(
                    {"type": "territory_cede", "value": 1, "regions": [candidates[0][0]]})
                context_tags.append("smart_cession")

    # 2b. Territory demands: prefer border regions
    if any(d.get("type") in ("territory_cede", "territory")
           for d in terms.get("demands", [])):
        target_regions = world.get_nation_regions(target_nation)
        france_regions = world.get_nation_regions("France")
        border = []
        for rname in target_regions:
            region = world.regions.get(rname)
            if region and any(adj in france_regions for adj in region.adjacent_regions):
                if rname != NATION_CAPITALS.get(target_nation):
                    border.append(rname)
        if border:
            terms["demands"] = [d for d in terms["demands"]
                                if d.get("type") not in ("territory_cede", "territory")]
            terms["demands"].append(
                {"type": "territory_cede", "value": 1, "regions": [border[0]]})
            context_tags.append("border_territory_demanded")

    # 2c. Gold calibration
    gold_pref = profile.get("values_gold", "medium")
    if gold_pref == "high":
        for s in terms.get("sweeteners", []):
            if "gold" in s.get("type", ""):
                s["value"] = int(s["value"] * 1.5)
        if not context_tags:
            context_tags.append("gold_for_poor")
    elif gold_pref == "low":
        for s in terms.get("sweeteners", []):
            if "gold" in s.get("type", ""):
                s["value"] = int(s["value"] * 0.5)
        if not context_tags:
            context_tags.append("gold_useless")

    # 2d. Protection clause for survival-driven nations
    if (profile.get("diplomatic_lever") == "survival"
            and proposal_type in ("peace", "defensive_alliance", "alliance")):
        if "protection_promised" in SPECIAL_BONUSES.get(target_nation, {}):
            if "protection_promised" not in terms.get("clauses", []):
                terms.setdefault("clauses", []).append("protection_promised")
                context_tags.append("protection_offered")

    # 2e. AP for nations that value extra actions
    ap_pref = profile.get("values_ap", "medium")
    if ap_pref == "high" and war_score < -30:
        if not any(s.get("type") == "ap_per_turn" for s in terms.get("sweeteners", [])):
            terms["sweeteners"].append({"type": "ap_per_turn", "value": 1})
            context_tags.append("ap_for_weak")

    # --- Stage 3: Economic reality check ---
    _validate_economic_feasibility(terms, target_nation, world)

    # --- Stage 4: Commentary ---
    if not context_tags:
        if war_score < -30:
            context_tags.append("desperate_terms")
        elif war_score > 30:
            context_tags.append("dominant_terms")
        else:
            context_tags.append("neutral_deal")

    terms["talleyrand_commentary"] = _get_smart_commentary(
        target_nation, context_tags[0])

    # --- Stage 5: Return ---
    return terms
```

### Helper: `_build_base_terms()`

The current body of `generate_suggested_terms()` (`diplomatic_templates.py:1208-1309`) is moved here unchanged. Same war_score/relation threshold logic, same proposal_type branching.

### Helper: `_validate_economic_feasibility()`

```python
def _validate_economic_feasibility(terms, target_nation, world):
    player_gold = world.nation_gold.get("France", 0)
    player_income = world.calculate_turn_income("France").get("income", 0)
    target_income = world.calculate_turn_income(target_nation).get("income", 0)

    for s in terms.get("sweeteners", []):
        if s.get("type") == "gold_lump":
            s["value"] = int(min(s["value"], max(50, int(player_gold * 0.25))))
        elif s.get("type") == "gold_per_turn":
            s["value"] = int(min(s["value"], max(25, int(player_income * 0.2))))
    for d in terms.get("demands", []):
        if d.get("type") == "gold_per_turn":
            d["value"] = int(min(d["value"], max(25, int(target_income * 0.5))))
    # Force all values to int (Godot crashes on floats)
    for s in terms.get("sweeteners", []):
        if "value" in s: s["value"] = int(s["value"])
    for d in terms.get("demands", []):
        if "value" in d: d["value"] = int(d["value"])
```

### Helper: `_get_smart_commentary()`

```python
def _get_smart_commentary(target_nation, context_tag):
    key = (target_nation, context_tag)
    if key in TALLEYRAND_COMMENTARY:
        return TALLEYRAND_COMMENTARY[key]
    default_key = ("_default", context_tag)
    if default_key in TALLEYRAND_COMMENTARY:
        return TALLEYRAND_COMMENTARY[default_key]
    return "I have assembled terms befitting the situation, Sire."
```

---

## 9. Tests (Section 14)

| # | Test Name | What It Verifies |
|---|-----------|-----------------|
| 1 | `test_prussia_offer_includes_saxony` | France controls Saxony, losing to Prussia → terms offer Saxony region |
| 2 | `test_austria_offer_includes_bavaria` | France controls Bavaria, losing to Austria → terms offer Bavaria |
| 3 | `test_coveted_fallback_to_rank_cession` | France doesn't control coveted region → rank_cession_candidates used |
| 4 | `test_demand_prefers_border_regions` | Winning → demands region adjacent to France, not random |
| 5 | `test_saxony_gold_multiplied` | Saxony gold sweetener is 1.5x normal value |
| 6 | `test_britain_gold_reduced` | Britain gold sweetener is 0.5x normal value |
| 7 | `test_gold_lump_capped_by_treasury` | Gold lump never exceeds 25% of France treasury |
| 8 | `test_gold_per_turn_capped_by_income` | Gold per turn never exceeds 20% of France income |
| 9 | `test_saxony_peace_includes_protection` | Saxony peace includes `protection_promised` clause |
| 10 | `test_protection_not_added_to_prussia` | Prussia peace does NOT include protection |
| 11 | `test_saxony_ap_at_minus_30` | Saxony gets AP sweetener at war_score -31 |
| 12 | `test_austria_no_ap_at_minus_30` | Austria does NOT get AP at war_score -31 |
| 13 | `test_commentary_present` | `talleyrand_commentary` key exists and is non-empty string |
| 14 | `test_prussia_saxony_commentary_mentions_saxony` | When offering Saxony, commentary references it |
| 15 | `test_default_commentary_fallback` | Unknown nation gets commentary via `_default` pool |
| 16 | `test_gold_demand_capped_by_target` | Gold demand ≤ 50% of target's income |
| 17 | `test_broke_france_offers_less` | France with 100g offers proportionally less gold |
| 18 | `test_territory_ownership_validated` | Offered territory is actually French-controlled |

---

## 10. What This Does NOT Change

- `calculate_acceptance()` in `diplomacy.py` — acceptance formula unchanged
- `SWEETENER_VALUES` / `DEMAND_VALUES` — unchanged
- `SPECIAL_BONUSES` — consumed by Stage 2 but dict itself unchanged
- `NATION_DESIRES` in `ai_diplomacy.py` — AI counter-offer logic unchanged
- `modify_generous` / `modify_harsh` in `executor.py` — call `generate_suggested_terms()` which we modify, but executor code itself unchanged
- No new WorldState fields, no serialization changes
- No changes to any Godot files

---

## 11. Verification

1. `".venv\Scripts\python.exe" -m pytest tests/test_bugfix_proposal_flow.py -v` — Section 14 passes
2. `".venv\Scripts\python.exe" -m pytest tests/ -v --tb=no -q` — full suite, zero regressions
3. **Manual curl:**
   ```bash
   curl -X POST http://127.0.0.1:8005/command \
     -H "Content-Type: application/json" \
     -d '{"command": "Talleyrand, propose peace to Prussia"}' | python -m json.tool
   ```
   Verify: `talleyrand_commentary` present, terms include Saxony if France controls it
4. Propose to each nation, verify commentary is unique and terms reflect nation profile

---

## 12. Design Decisions

**D1. Gold scaling applies to sweeteners only, not demands.**
The `values_gold` multiplier (1.5x for "high", 0.5x for "low") only affects gold *sweeteners* (what France offers). Gold *demands* (what France takes from winners) are already capped by `_validate_economic_feasibility()` which checks the target's actual income. Scaling demands by the target's gold preference would be backwards — poor nations "value gold highly" but can't *pay* gold. The feasibility check handles this naturally.

**D2. `NATION_DESIRE_PROFILES` is hard-coded, not moddable.**
Modding support is a separate concern. The profiles are a static data dict — easy to make moddable later if needed. No modding system changes in this spec.

**D3. Saxony's `covets_regions` listing their own territory is correct.**
When France has conquered Saxony/Dresden, offering them back is the most meaningful sweetener ("returning the homeland"). When France doesn't control those regions (Saxony still has them), the `rank_cession_candidates()` fallback activates — which is the right behavior. This is thematically perfect: Talleyrand knows Einsiedel's deepest desire is the survival of his nation.

**D4. Commentary is generated once per suggestion, not updated by modify_generous/modify_harsh.**
The modify handlers in `executor.py` call `generate_suggested_terms()` fresh on round 1 (gets commentary), then use `copy.deepcopy(terms)` on subsequent rounds (commentary preserved from round 1). This is correct: commentary explains Talleyrand's *initial* reasoning. When the player clicks "more generous" or "harsher", those are the player's decisions — Talleyrand's role is to suggest, not narrate every tweak.
