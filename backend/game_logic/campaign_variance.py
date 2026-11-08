"""Campaign variance — the dice and the bounds (AI-0b / AI-0c).

Spec: docs/AI_INTENT_SPEC.md §3.8 (the seed), §3.8.1 (the historical
envelope), §6 D7 (the gate decision). Stage A of the phased build plan
(§11.1).

The campaign seed is the ONLY source of cross-campaign variance. Three
contracts govern everything in this module:

1. **The seed is serialized** (`WorldState.campaign_seed`) and round-trips
   exactly — `from_dict` restores what `to_dict` wrote, never a freshly
   generated value (§5 pin 14c). A save with no seed key is a pre-seed
   campaign and reads `historical`.
2. **`historical` (or the env var unset) collapses every band to its
   authored centre** — today's boot, byte-for-byte (§5 pin 14a). The whole
   suite runs pinned to it (conftest), like `SOVEREIGN_SCENARIO=none`.
3. **Bands are authored content** in the scenario file — no authored band,
   no variance (§3.8.1). The engine cannot invent a range it was not given.

Derivation is hash-based (sha256), NEVER the ambient `random` module: the
module-RNG streams (combat 2d6, enemy mood, vassal defection, jealousy) are
seeded by 21 test files and M1–M7 depend on their draw order — consuming or
reseeding them here would shift every pinned trial (§5 pin 2).
"""

import hashlib
import os
from typing import Any, Dict, List, Optional, Sequence

SEED_ENV = "SOVEREIGN_SEED"
HISTORICAL_SEED = "historical"

# §3.8 "weighted late": the in-campaign jitter band reaches full width by
# this turn. Turn 0 jitter is always 0 — the boot spread comes from the
# AUTHORED Tier-2 bands (§3.8.1), never from this ramp. Blessed number,
# tunable in-band.
JITTER_RAMP_TURNS = 12


def resolve_campaign_seed(explicit: Optional[str] = None) -> str:
    """The seed precedence: explicit param > SOVEREIGN_SEED env > historical.

    The default lives IN THE MODEL (WorldState.__init__ calls this), not in
    main.py's scenario-path selector — 75 direct from_scenario callers
    bypass main.py entirely (§3.8.1 migration paragraph / §10 row 16).
    """
    if explicit is not None and str(explicit).strip():
        return str(explicit).strip()
    env = os.environ.get(SEED_ENV, "").strip()
    return env or HISTORICAL_SEED


def is_historical(seed: Optional[str]) -> bool:
    """True when the seed reproduces today's boot byte-for-byte."""
    text = str(seed or HISTORICAL_SEED).strip().lower()
    return (text or HISTORICAL_SEED) == HISTORICAL_SEED


# ── The rolled seed (Tier 1, DYNAMISM_SPEC.md §2 — November 7, 2026) ──────
#
# `roll_campaign_seed()` names a fresh campaign: a READABLE adjective-noun
# pair with a two-digit mark ("iron-eagle-07"), never `historical` (no word
# below is it, structurally). Entropy comes from `secrets` — NEVER the
# ambient `random` module, whose streams 21 test files and M1–M7 pin by
# draw order (§5 pin 2; the same law the hash derivations above keep).
# The roll happens exactly once per New Game without an explicit seed or a
# SOVEREIGN_SEED env (main.py's /new_game precedence) — the suite's
# conftest pins the env, so no test and no harness arm ever rolls.

_ROLL_ADJECTIVES = (
    "iron", "gilded", "wintry", "scarlet", "stormy", "quiet", "burning",
    "frozen", "broken", "proud", "hungry", "distant", "thundering", "pale",
    "crimson", "long", "bitter", "gallant", "restless", "shrouded",
    "swift", "old", "silent", "midnight",
)
_ROLL_NOUNS = (
    "eagle", "bayonet", "grenadier", "hussar", "cannon", "standard",
    "bivouac", "frontier", "crossing", "redoubt", "salient", "vanguard",
    "dispatch", "campfire", "squadron", "lancer", "courier", "bastion",
    "caisson", "sabre", "musket", "colours", "march", "levee",
)


def roll_campaign_seed() -> str:
    """One readable seed, freshly rolled — "adjective-noun-NN"."""
    import secrets
    return (f"{secrets.choice(_ROLL_ADJECTIVES)}-"
            f"{secrets.choice(_ROLL_NOUNS)}-{secrets.randbelow(100):02d}")


def cast_understudy(seed: str,
                    shortlist: Sequence[str]) -> Optional[str]:
    """T2-6 (§3.8.2 "the casting band"; `DYNAMISM_SPEC.md` §2 Tier 2 —
    "the lawful lucky nation"): the ONE understudy this seed casts from
    the authored shortlist — None on `historical` (the structural
    collapse: nobody is cast, no reorder, no dial) and on an empty
    list. Pure hash (namespace `casting::understudy`), exported so
    tests and tools can ask who a seed casts without booting a world."""
    courts = [str(n) for n in (shortlist or []) if str(n).strip()]
    if not courts or is_historical(seed):
        return None
    return courts[seeded_int(seed, "casting::understudy",
                             0, len(courts) - 1)]


def _unit(seed: str, namespace: str) -> float:
    """Deterministic float in [0, 1) from (seed, namespace). Pure hash —
    no module RNG consumed, no state anywhere."""
    digest = hashlib.sha256(
        f"{seed}::{namespace}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / 2 ** 64


def seeded_int(seed: str, namespace: str, lo: int, hi: int) -> int:
    """Deterministic int in [lo, hi] inclusive. Raw derivation — historical
    collapse is the CALLER's contract (band appliers use the authored
    centre; jitter/tiebreak return their neutral arm)."""
    lo_i, hi_i = int(lo), int(hi)
    if hi_i <= lo_i:
        return lo_i
    span = hi_i - lo_i + 1
    return lo_i + int(_unit(seed, namespace) * span)


def seeded_jitter(seed: str, namespace: str, amplitude: int,
                  turn: int) -> int:
    """§3.8 threshold jitter: deterministic int in [-amp, +amp], ramping
    from 0 at turn 0 to full width by JITTER_RAMP_TURNS (weighted late —
    turn 1 of 1805 looks like 1805 on every seed; divergence arrives as
    the campaign earns it). Historical seed => always 0."""
    if is_historical(seed) or amplitude <= 0:
        return 0
    scale = min(1.0, max(0.0, float(turn) / float(JITTER_RAMP_TURNS)))
    span = int(round(int(amplitude) * scale))
    if span <= 0:
        return 0
    return seeded_int(seed, f"jitter::{namespace}", -span, span)


def seeded_tiebreak(seed: str, namespace: str,
                    candidates: Sequence[Any]) -> Any:
    """§3.8 tie-breaks: where two designs or targets score equal, the seed
    chooses — authored order stops being destiny. Historical seed => the
    first candidate (today's first-predicate-wins behaviour)."""
    items = list(candidates)
    if not items:
        return None
    if is_historical(seed) or len(items) == 1:
        return items[0]
    return items[seeded_int(seed, f"tiebreak::{namespace}",
                            0, len(items) - 1)]


def seeded_permutation(seed: str, namespace: str,
                       items: Sequence[Any]) -> List[Any]:
    """Deterministic permutation of items (hash-keyed sort by original
    index). Historical seed => identity (authored order)."""
    seq = list(items)
    if is_historical(seed) or len(seq) < 2:
        return seq
    keyed = sorted(
        range(len(seq)),
        key=lambda i: _unit(seed, f"perm::{namespace}::{i}"))
    return [seq[i] for i in keyed]


# ── Authored-band resolution (AI-0c) ──────────────────────────────────────
#
# Bands ride the scenario file beside the values they vary (§3.8.1):
#   nation_relations pair:  {"value": -10, "band": [-25, 5]}   (trust idiom)
#   threat_level:           sibling key "threat_level_band": [lo, hi]
#   deck order:             "order_group": N on >=2 CONTIGUOUS deck entries
# validate_scenario checks the shapes and the clamps; this resolver assumes
# a validated scenario and collapses every band to a concrete value BEFORE
# from_dict ingests it — from_dict (the save-load path) never sees a band.


def relation_band_entry_value(entry: Any) -> int:
    """The authored centre of a nation_relations entry (bare int or the
    band-carrying {"value": N, "band": [lo, hi]} object)."""
    if isinstance(entry, dict):
        return int(entry.get("value") or 0)
    return int(entry)


def apply_scenario_variance(scenario_data: Dict[str, Any],
                            seed: str) -> Dict[str, Any]:
    """Collapse every authored band in scenario_data to a concrete value.

    Mutates and returns scenario_data. On the historical seed every band
    resolves to its authored centre — the output is behaviourally
    byte-identical to the pre-band scenario. Band-carrying shapes are
    stripped so from_dict (and the serialized world) only ever sees the
    resolved plain values.
    """
    historical = is_historical(seed)

    relations = scenario_data.get("nation_relations")
    if isinstance(relations, dict):
        for pair, entry in list(relations.items()):
            if not isinstance(entry, dict):
                continue
            value = int(entry.get("value") or 0)
            band = entry.get("band")
            if (not historical and isinstance(band, (list, tuple))
                    and len(band) == 2):
                value = seeded_int(seed, f"relations::{pair}",
                                   int(band[0]), int(band[1]))
            relations[pair] = value

    threat_band = scenario_data.pop("threat_level_band", None)
    if (not historical and isinstance(threat_band, (list, tuple))
            and len(threat_band) == 2):
        scenario_data["threat_level"] = seeded_int(
            seed, "threat_level", int(threat_band[0]), int(threat_band[1]))

    agendas = scenario_data.get("agendas")
    if isinstance(agendas, dict):
        for nation, deck in agendas.items():
            if not isinstance(deck, list):
                continue
            agendas[nation] = _resolve_deck_order(seed, nation, deck,
                                                  historical)
            # T2-B (the Tier-2 gate record, AI_INTENT_SPEC.md §3.8.2 —
            # "initial ladder readiness"): resolved AFTER the order band,
            # so the namespace keys by the entry's own id, not its slot.
            _resolve_deck_readiness(seed, nation, agendas[nation],
                                    historical)

    # T2-B (§3.8.2 — "the minors' lean" / T2-6's dial): the statecraft
    # block's weight_mod bands, collapsed to plain ints before from_dict
    # ingests the block (the save path never sees a band).
    statecraft = scenario_data.get("statecraft")
    if isinstance(statecraft, dict):
        resolve_statecraft_bands(statecraft, seed, historical=historical)

    # T2-6 (§3.8.2 — "the casting band"): AFTER the statecraft bands, so
    # the cast court's bold dial lands as a plain int over its resolved
    # lean (the override wins) and the key is stripped like every band.
    _resolve_casting(scenario_data, seed, historical)

    moments = scenario_data.get("moments")
    if isinstance(moments, dict):
        resolve_moment_turns(moments, seed, historical=historical)

    return scenario_data


def _resolve_deck_readiness(seed: str, nation: str, deck: List[Any],
                            historical: bool) -> None:
    """T2-B (§3.8.2, "initial ladder readiness" — §3.8's jitter applied at
    turn 0): collapse an entry's {"readiness": N, "readiness_band":
    [lo, hi]} to a concrete int — the authored value on `historical`, a
    seeded int in the band otherwise (namespace
    `readiness::<nation>::<id>`). The band is stripped so the serialized
    deck carries a plain int; an entry without the keys is untouched
    (every pre-band deck, byte for byte). The int rides `AgendaView.params`
    and `intent._derive_weight` adds it — 0 when unauthored."""
    for entry in deck:
        if not isinstance(entry, dict):
            continue
        band = entry.pop("readiness_band", None)
        if band is None and "readiness" not in entry:
            continue
        value = int(entry.get("readiness") or 0)
        if (not historical and isinstance(band, (list, tuple))
                and len(band) == 2):
            value = seeded_int(seed,
                               f"readiness::{nation}::{entry.get('id')}",
                               int(band[0]), int(band[1]))
        entry["readiness"] = value


def resolve_statecraft_bands(statecraft: Dict[str, Any], seed: str,
                             historical: Optional[bool] = None
                             ) -> Dict[str, Any]:
    """T2-B (§3.8.2): collapse each nation's statecraft `weight_mod`
    {"value": N, "band": [lo, hi]} to a plain int — the authored value on
    `historical`, seeded in the band otherwise (namespace
    `statecraft::<nation>::weight_mod`). A bare int is kept as authored;
    `wary_of` is never touched here (it is unbanded by design — a fear is
    a profile, not a contingency). Idempotent on a resolved int."""
    if historical is None:
        historical = is_historical(seed)
    for nation, overlay in statecraft.items():
        if not isinstance(overlay, dict):
            continue
        weight_mod = overlay.get("weight_mod")
        if not isinstance(weight_mod, dict):
            continue
        value = int(weight_mod.get("value") or 0)
        band = weight_mod.get("band")
        if (not historical and isinstance(band, (list, tuple))
                and len(band) == 2):
            value = seeded_int(seed, f"statecraft::{nation}::weight_mod",
                               int(band[0]), int(band[1]))
        overlay["weight_mod"] = value
    return statecraft


def resolve_moment_turns(moments: Dict[str, Any], seed: str,
                         historical: Optional[bool] = None) -> Dict[str, Any]:
    """S14c (`docs/EVENTS_SPEC.md` §5): collapse each moment's authored
    window band {"value": N, "band": [lo, hi]} to a concrete turn — the
    authored `value` on `historical`, a seeded int in the band otherwise
    (namespace `moment::<id>::turn`). The band is stripped and the int
    serialized, so a later edit to the authored band cannot disturb a save.
    Idempotent on a resolved int; a causal entry (`lag`, no `turn`) and an
    unbanded `{"value": N}` never vary. The boot (`apply_scenario_variance`)
    and the pre-S14c backfill (the save's own seed) share it."""
    if historical is None:
        historical = is_historical(seed)
    for entry in (moments.get("deck") or []):
        turn = entry.get("turn") if isinstance(entry, dict) else None
        if not isinstance(turn, dict):
            continue
        value = int(turn.get("value") or 0)
        band = turn.get("band")
        if (not historical and isinstance(band, (list, tuple))
                and len(band) == 2):
            value = seeded_int(seed, f"moment::{entry.get('id')}::turn",
                               int(band[0]), int(band[1]))
        entry["turn"] = value
    return moments


def _resolve_casting(scenario_data: Dict[str, Any], seed: str,
                     historical: bool) -> None:
    """T2-6 (§3.8.2 "the casting band" — ruled at the tier's head; the
    live-first ruling at the slice's own plan, November 8, 2026): pop
    the authored `casting` key (the band-strip idiom — from_dict and
    the serialized world never see it), pick the understudy
    (`cast_understudy`), boot its first ACQUIRE at its deck's head —
    a guard ahead of it steps behind: the cast court has set its
    posture aside, which is what being cast MEANS (an ambitious
    Denmark is not the neutral of 1807), and satisfaction restores it
    (the acquire goes inactive, the guard resurfaces) — and write the
    bold dial over the court's resolved lean in the statecraft overlay
    (namespace `casting::weight_mod`, seeded in the authored band).
    On `historical` the key is stripped and nothing else moves —
    nobody is cast, structurally."""
    casting = scenario_data.pop("casting", None)
    if not isinstance(casting, dict) or historical:
        return
    cast = cast_understudy(seed, casting.get("shortlist") or [])
    if not cast:
        return
    agendas = scenario_data.get("agendas")
    deck = agendas.get(cast) if isinstance(agendas, dict) else None
    if isinstance(deck, list):
        index = next((i for i, entry in enumerate(deck)
                      if isinstance(entry, dict)
                      and entry.get("type") == "acquire_regions"), None)
        if index is not None and index > 0:
            deck.insert(0, deck.pop(index))
    dial = casting.get("weight_mod")
    value: Optional[int] = None
    if isinstance(dial, dict):
        band = dial.get("band")
        if isinstance(band, (list, tuple)) and len(band) == 2:
            value = seeded_int(seed, "casting::weight_mod",
                               int(band[0]), int(band[1]))
        else:
            value = int(dial.get("value") or 0)
    elif isinstance(dial, int) and not isinstance(dial, bool):
        value = int(dial)
    if value is not None:
        statecraft = scenario_data.setdefault("statecraft", {})
        overlay = statecraft.setdefault(cast, {})
        if isinstance(overlay, dict):
            overlay["weight_mod"] = int(value)


def _resolve_deck_order(seed: str, nation: str, deck: List[Any],
                        historical: bool) -> List[Any]:
    """Permute each contiguous order_group run (seeded), then strip the
    order_group key so the serialized deck is shaped exactly as today."""
    resolved: List[Any] = []
    index = 0
    while index < len(deck):
        entry = deck[index]
        group = entry.get("order_group") if isinstance(entry, dict) else None
        if group is None:
            resolved.append(entry)
            index += 1
            continue
        run = [entry]
        walk = index + 1
        while walk < len(deck):
            nxt = deck[walk]
            if (isinstance(nxt, dict)
                    and nxt.get("order_group") == group):
                run.append(nxt)
                walk += 1
            else:
                break
        if not historical and len(run) > 1:
            run = seeded_permutation(
                seed, f"deck_order::{nation}::{group}", run)
        resolved.extend(run)
        index = walk
    for entry in resolved:
        if isinstance(entry, dict):
            entry.pop("order_group", None)
    return resolved
