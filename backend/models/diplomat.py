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
