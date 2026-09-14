"""IQ-2 "The Collapse Is Legible" — the ONE source for a collapsed realm.

Measured (the Phase-3 re-score, September 2026): a France reduced to one
province — and on the shipped tree to NONE — played four more turns while
every surface narrated an ordinary campaign. Talleyrand opened the morning
with "Sire, I believe Denmark may be ready to discuss improved relations. The
diplomatic winds favor us."; the headline priced each turn of occupation of
the LAST French province as "worth a province to their recruiting
sergeants"; Berthier closed "Your armies stand ready, Sire. The initiative is
ours."; and the only collapse warning the game owned
(`turn_manager.get_defeat_imminent_state`) was switched off on every Europe
world, because its copy promised "the campaign ends" and EC-6a made the
campaign an open-ended sandbox.

The scope note is binding and is why this module exists as a READER only:
**making the collapse legible does not make it terminal.** Win and defeat
conditions stay with the Victory & Objectives Pass. Nothing built on this
module may end, block or shorten the campaign, and no sentence it produces
may promise that anything ends. It states what the realm still holds, what
still stands under arms, and where the sovereign is — the player's own
knowledge, so every figure is fog-safe (R5 governs the ENEMY, never our own
body).

Every surface that speaks of the collapse reads `get_collapse_state` — the
dispatch headline and Berthier's close, Talleyrand's report, the sandbox arm
of the defeat-imminent warning and its rail notice, the end-turn banner, the
war room, the ledgers, the status report and Le Moniteur — so they cannot
disagree about whether France has fallen (the CA9 through-line: one rule, one
implementation). Display only (GR6); ZERO serialized fields.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.display_names import humanize_entity_name
from backend.game_logic.formations import formed_display_name

# Flip lever (the file convention: False reproduces the pre-IQ-2 surfaces
# byte-for-byte — every reader treats None as "no collapse").
THE_COLLAPSE_IS_LEGIBLE = True

# A realm holding this many provinces or fewer has COLLAPSED. Blessed
# default, display-only, tunable in band. One, not a fraction of the boot
# holdings: the measured campaigns sat at 2 provinces for ten turns and at
# 1 for six, and "two provinces" is a war going very badly — "one" is the
# state every surface was lying about. The Victory Pass may widen it when it
# owns what a collapse MEANS.
COLLAPSE_PROVINCE_CEILING = 1

TIER_FALLEN = "fallen"             # no province at all
TIER_LAST_PROVINCE = "last_province"  # exactly one


def get_collapse_state(world, nation: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """The collapse, or None when the realm stands.

    Sandbox worlds only: the legacy 19-region world keeps its own terminal
    rules (0 provinces IS game over there, and `get_defeat_imminent_state`'s
    legacy arm already warns at one), so it is byte-identical by
    construction (N1).

    Bounded work (GR8): `get_nation_regions` is the per-turn cached map, and
    the marshal pass is the roster, not the map.
    """
    if not THE_COLLAPSE_IS_LEGIBLE:
        return None
    if world is None or not getattr(world, "sandbox_mode", False):
        return None
    nation = nation or getattr(world, "player_nation", None)
    if not nation:
        return None
    held: List[str] = sorted(world.get_nation_regions(nation) or [])
    if len(held) > COLLAPSE_PROVINCE_CEILING:
        return None

    capital = world.get_nation_capital(nation) or ""
    capital_region = world.regions.get(capital) if capital else None
    capital_controller = (getattr(capital_region, "controller", "") or "") if capital_region else ""
    capital_held = bool(capital) and capital_controller == nation

    standing = []
    prisoners = []
    sovereign = None
    for m in world.marshals.values():
        if m.nation != nation:
            continue
        if getattr(m, "is_sovereign", False):
            sovereign = m
        if getattr(m, "captured_by", ""):
            prisoners.append(m.name)
        elif int(getattr(m, "strength", 0) or 0) > 0:
            standing.append(m)
    standing.sort(key=lambda m: (-int(m.strength), m.name))
    sovereign_captor = (getattr(sovereign, "captured_by", "") or "") if sovereign else ""

    return {
        "tier": TIER_FALLEN if not held else TIER_LAST_PROVINCE,
        "nation": nation,
        "provinces_held": int(len(held)),
        "provinces": held,
        "capital": capital,
        "capital_held": bool(capital_held),
        # "" when the capital is ours or nobody holds it.
        "capital_holder": capital_controller if (capital and not capital_held) else "",
        "standing": [m.name for m in standing],
        "standing_men": int(sum(int(m.strength) for m in standing)),
        "prisoners": sorted(prisoners),
        "sovereign": sovereign.name if sovereign else "",
        "sovereign_captor": sovereign_captor,
    }


# ════════════════════════════════════════════════════════════════════════
# The shared phrases. Every surface composes from these, so the same fact is
# worded the same way wherever the player reads it.
# ════════════════════════════════════════════════════════════════════════

def _join(names: List[str]) -> str:
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f" and {names[-1]}"


def _person(world, name: str) -> str:
    """A marshal's display name; the sovereign is 'the Emperor'."""
    m = getattr(world, "marshals", {}).get(name)
    if m is not None and getattr(m, "is_sovereign", False):
        return "the Emperor"
    return humanize_entity_name(name)


def realm_sentence(world, state: Dict[str, Any]) -> str:
    """'France holds no province of her own.' / '… a single province: Brittany.'"""
    realm = formed_display_name(world, state["nation"])
    if state["tier"] == TIER_FALLEN:
        return f"{realm} holds no province of her own."
    return f"{realm} holds a single province: {state['provinces'][0]}."


def capital_clause(world, state: Dict[str, Any]) -> str:
    """' Paris is in Austria's hands.' — '' when the capital is ours, or is
    the one province we hold (the realm sentence already names it)."""
    capital = state.get("capital") or ""
    if not capital or state.get("capital_held"):
        return ""
    holder = state.get("capital_holder") or ""
    if holder:
        return f" {capital} is in {formed_display_name(world, holder)}'s hands."
    return f" {capital} is lost to us."


def forces_clause(world, state: Dict[str, Any]) -> str:
    """What still stands under arms — never a promise about what it can do."""
    standing = state.get("standing") or []
    men = int(state.get("standing_men") or 0)
    if not standing:
        return "No corps of ours stands free under arms."
    names = [_person(world, n) for n in standing]
    if len(names) == 1:
        who = names[0]
        owner = "the Emperor's" if who == "the Emperor" else f"{who}'s"
        return f"{owner[0].upper()}{owner[1:]} corps still stands under our colours — {men:,} men."
    return (f"{len(names)} corps still stand under our colours — "
            f"{_join(names)}, {men:,} men in all.")


def sovereign_clause(world, state: Dict[str, Any]) -> str:
    """' The Emperor is a prisoner of Austria.' — '' while he is free."""
    captor = state.get("sovereign_captor") or ""
    if not captor:
        return ""
    return f" The Emperor is a prisoner of {formed_display_name(world, captor)}."


def summary_line(world, state: Dict[str, Any]) -> str:
    """The whole standing fact in one breath: realm, capital, army, sovereign."""
    return (f"{realm_sentence(world, state)}{capital_clause(world, state)} "
            f"{forces_clause(world, state)}{sovereign_clause(world, state)}")


# The one sentence that answers "does this end the game?" — the scope note,
# spoken. Sandbox-true: `_check_victory_conditions` returns game-continues
# first on every Europe world, and `_eliminate_nation` never runs on the
# player.
CAMPAIGN_CONTINUES = ("The campaign does not end with the land — it goes on "
                      "in the field and at the peace table.")


def collapse_line(world, nation: Optional[str] = None) -> str:
    """Convenience for a surface that wants one line or nothing."""
    state = get_collapse_state(world, nation)
    if state is None:
        return ""
    return summary_line(world, state)
