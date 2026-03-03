"""
Diplomatic Representative — Phase 8 Session 2

Each nation has exactly one diplomat who handles all diplomacy.
Diplomats are NOT marshals — they go in world.diplomats, never world.marshals.
Diplomat personalities are completely separate from marshal personalities.
"""

from typing import Dict


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
        trust: int = 65,
        biography: str = "",
    ):
        self.name = name
        self.nation = nation
        self.personality = personality  # schemer/loyalist/hawk/dove
        self.skill = skill              # 1-10
        self.trust = trust              # Schemers start at 55, others at 65
        self.biography = biography

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "nation": self.nation,
            "personality": self.personality,
            "skill": int(self.skill),
            "trust": int(self.trust),
            "biography": self.biography,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DiplomaticRepresentative':
        return cls(
            name=data.get("name", "Unknown"),
            nation=data.get("nation", "Unknown"),
            personality=data.get("personality", "loyalist"),
            skill=int(data.get("skill", 5)),
            trust=int(data.get("trust", 65)),
            biography=data.get("biography", ""),
        )

    def __repr__(self) -> str:
        return f"Diplomat({self.name}, {self.nation}, {self.personality}, skill={self.skill})"


# ═══════ STARTING DIPLOMATS ═══════

STARTING_DIPLOMATS = {
    "France": DiplomaticRepresentative(
        name="Talleyrand",
        nation="France",
        personality="schemer",
        skill=10,
        trust=55,
        biography="The devil's diplomat. Serves France — or rather, serves what he believes France should be.",
    ),
    "Britain": DiplomaticRepresentative(
        name="Castlereagh",
        nation="Britain",
        personality="hawk",
        skill=7,
        trust=65,
        biography="Cold, calculating, implacable. Views any French advantage as a threat to the balance of power.",
    ),
    "Prussia": DiplomaticRepresentative(
        name="Hardenberg",
        nation="Prussia",
        personality="hawk",
        skill=6,
        trust=65,
        biography="Demands respect, offers little.",
    ),
    "Austria": DiplomaticRepresentative(
        name="Metternich",
        nation="Austria",
        personality="schemer",
        skill=9,
        trust=55,
        biography="Spider diplomat, delays & leverages.",
    ),
    "Saxony": DiplomaticRepresentative(
        name="Einsiedel",
        nation="Saxony",
        personality="dove",
        skill=4,
        trust=65,
        biography="Fears aggression, hopes for peace.",
    ),
}


def create_starting_diplomats() -> Dict[str, 'DiplomaticRepresentative']:
    """Create fresh copies of all starting diplomats, keyed by nation."""
    result = {}
    for nation, template in STARTING_DIPLOMATS.items():
        result[nation] = DiplomaticRepresentative(
            name=template.name,
            nation=template.nation,
            personality=template.personality,
            skill=template.skill,
            trust=template.trust,
            biography=template.biography,
        )
    return result
