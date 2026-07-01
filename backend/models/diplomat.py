"""
Diplomatic Representative — Phase 8 Session 2

Each nation has exactly one diplomat who handles all diplomacy.
Diplomats are NOT marshals — they go in world.diplomats, never world.marshals.
Diplomat personalities are completely separate from marshal personalities.
"""

from typing import Dict, Mapping


# Valid diplomat personalities (separate from marshal personalities)
DIPLOMAT_PERSONALITIES = ("schemer", "loyalist", "hawk", "dove")


class DiplomaticRepresentative:
    """A nation's diplomatic representative."""

    def __init__(
        self,
        name: str,
        nation: str,
        personality: str,
        skill: int,
        biography: str = "",
    ):
        self.name = name
        self.nation = nation
        self.personality = personality  # schemer/loyalist/hawk/dove
        self.skill = skill              # 1-10
        self.biography = biography

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "nation": self.nation,
            "personality": self.personality,
            "skill": int(self.skill),
            "biography": self.biography,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DiplomaticRepresentative':
        # Note: trust field silently ignored for backward compat with old saves
        return cls(
            name=data.get("name", "Unknown"),
            nation=data.get("nation", "Unknown"),
            personality=data.get("personality", "loyalist"),
            skill=int(data.get("skill", 5)),
            biography=data.get("biography", ""),
        )

    def __repr__(self) -> str:
        return f"Diplomat({self.name}, {self.nation}, {self.personality}, skill={self.skill})"


# ═══════ STARTING DIPLOMAT DEFINITIONS (data-only) ═══════
# Nation → diplomat definition. Adding a new nation = adding one entry here.
# No function edits required.

_DIPLOMAT_DEFINITIONS: Dict[str, Dict] = {
    "France": {
        "name": "Talleyrand",
        "personality": "schemer",
        "skill": 10,
        "biography": "The devil's diplomat. Serves France — or rather, serves what he believes France should be.",
    },
    "Britain": {
        "name": "Castlereagh",
        "personality": "hawk",
        "skill": 7,
        "biography": "Cold, calculating, implacable. Views any French advantage as a threat to the balance of power.",
    },
    "Prussia": {
        "name": "Hardenberg",
        "personality": "hawk",
        "skill": 6,
        "biography": "Demands respect, offers little.",
    },
    "Austria": {
        "name": "Metternich",
        "personality": "schemer",
        "skill": 9,
        "biography": "Spider diplomat, delays & leverages.",
    },
    "Saxony": {
        "name": "Einsiedel",
        "personality": "dove",
        "skill": 4,
        "biography": "Fears aggression, hopes for peace.",
    },
}


def create_diplomat_from_data(nation: str, data: Mapping) -> 'DiplomaticRepresentative':
    """Create a DiplomaticRepresentative from a data-driven definition dict."""
    return DiplomaticRepresentative(
        name=data["name"],
        nation=nation,
        personality=data["personality"],
        skill=int(data["skill"]),
        biography=data.get("biography", ""),
    )


# STARTING_DIPLOMATS is materialized from _DIPLOMAT_DEFINITIONS for backward
# compatibility with code that imports the template dict directly (e.g. the
# nation_config roster composition and completeness tests).
STARTING_DIPLOMATS: Dict[str, 'DiplomaticRepresentative'] = {
    nation: create_diplomat_from_data(nation, defn)
    for nation, defn in _DIPLOMAT_DEFINITIONS.items()
}


def _clone_diplomat(template: 'DiplomaticRepresentative') -> 'DiplomaticRepresentative':
    """Clone a diplomat template while preserving legacy STARTING_DIPLOMATS semantics."""
    return DiplomaticRepresentative(
        name=template.name,
        nation=template.nation,
        personality=template.personality,
        skill=int(template.skill),
        biography=template.biography,
    )


def create_starting_diplomats() -> Dict[str, 'DiplomaticRepresentative']:
    """Create fresh copies of all starting diplomats, keyed by nation."""
    return {
        nation: _clone_diplomat(template)
        for nation, template in STARTING_DIPLOMATS.items()
    }


# ═══════ FULL-EUROPE (126-province) DIPLOMAT ROSTER — Map Slice 3 ═══════
# Diplomat definitions for the 15 nations the europe.json ownership pass adds
# beyond the legacy five. These are kept SEPARATE from `_DIPLOMAT_DEFINITIONS`
# on purpose: `STARTING_DIPLOMATS` feeds `nation_config.RUNTIME_NATIONS`, which
# drives the default (legacy 5-nation) `WorldState()`. Merging them would balloon
# the legacy world's roster and break its test fixture. The Europe world builder
# (Slice 4) composes its diplomats from the five named templates PLUS these.
#
# Named historical foreign ministers are used where well-documented; the rest
# carry a functional chancery persona. All new nations resolve VOICE through the
# `resolve_named_diplomat()` → chancery fallback in v1; bespoke in-register voice
# lines are owner-row DEF-1 ("Roster Voices"), a tracked follow-up, not a blocker.
_EUROPE_EXTRA_DIPLOMAT_DEFINITIONS: Dict[str, Dict] = {
    "Russia": {
        "name": "Czartoryski",
        "personality": "schemer",
        "skill": 7,
        "biography": "Alexander's foreign minister; dreams of a Europe re-drawn to Russian design.",
    },
    "Spain": {
        "name": "Cevallos",
        "personality": "loyalist",
        "skill": 5,
        "biography": "Godoy's man at the ministry; binds Spain to the French star for now.",
    },
    "Ottoman": {
        "name": "Reis Efendi",
        "personality": "dove",
        "skill": 5,
        "biography": "The Porte's chief scribe of foreign affairs; patient, evasive, immovable.",
    },
    "Sweden": {
        "name": "Ehrenheim",
        "personality": "loyalist",
        "skill": 4,
        "biography": "Serves a king whose loathing of Bonaparte outruns Sweden's means.",
    },
    "Naples": {
        "name": "Medici",
        "personality": "dove",
        "skill": 4,
        "biography": "Steers the Bourbon court between the French army and the British fleet.",
    },
    "Portugal": {
        "name": "Araujo",
        "personality": "dove",
        "skill": 4,
        "biography": "Keeps Lisbon's old alliance with London alive without provoking Madrid.",
    },
    "Denmark": {
        "name": "Bernstorff",
        "personality": "loyalist",
        "skill": 5,
        "biography": "Guards Danish neutrality and the Sound, wary of every fleet that nears it.",
    },
    "Bavaria": {
        "name": "Montgelas",
        "personality": "schemer",
        "skill": 7,
        "biography": "Architect of a modern Bavaria; casts his lot with Paris to grow it.",
    },
    "Hanover": {
        "name": "Chancery of Hanover",
        "personality": "dove",
        "skill": 3,
        "biography": "An electorate that shares Britain's crown and France's occupation both.",
    },
    "Hesse": {
        "name": "Chancery of Hesse",
        "personality": "dove",
        "skill": 3,
        "biography": "A small German court trying to stay small and unnoticed.",
    },
    "PapalStates": {
        "name": "Consalvi",
        "personality": "dove",
        "skill": 6,
        "biography": "Cardinal Secretary of State; defends the Church's temporal remnant with guile.",
    },
    "Sardinia": {
        "name": "Chancery of Sardinia",
        "personality": "loyalist",
        "skill": 4,
        "biography": "A king exiled to his island, waiting for Piedmont's return.",
    },
    "Holland": {
        "name": "Schimmelpenninck",
        "personality": "loyalist",
        "skill": 5,
        "biography": "Grand Pensionary of a republic that lives on French sufferance.",
    },
    "KingdomOfItaly": {
        "name": "Marescalchi",
        "personality": "loyalist",
        "skill": 5,
        "biography": "Foreign minister of a kingdom whose king wears the French crown.",
    },
    "Switzerland": {
        "name": "Chancery of Helvetia",
        "personality": "dove",
        "skill": 3,
        "biography": "Confederate cantons mediated — in every sense — by Bonaparte.",
    },
}


def create_europe_diplomats() -> Dict[str, 'DiplomaticRepresentative']:
    """Fresh diplomats for the full 20-nation Europe roster (Map Slice 3).

    Composes the five named legacy templates with the 15 Europe additions. Used
    by the Slice 4 Europe world builder; never mutates the legacy globals.
    """
    diplomats: Dict[str, 'DiplomaticRepresentative'] = {
        nation: _clone_diplomat(template)
        for nation, template in STARTING_DIPLOMATS.items()
    }
    for nation, defn in _EUROPE_EXTRA_DIPLOMAT_DEFINITIONS.items():
        diplomats[nation] = create_diplomat_from_data(nation, defn)
    return diplomats
