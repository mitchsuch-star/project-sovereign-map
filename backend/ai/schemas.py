"""
Schemas for LLM command parsing in Project Sovereign.
Phase 4: LLM Integration preparation.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ParseResult:
    """
    Structured result from command parsing.

    Supports both tactical commands ("Ney, attack Wellington") and
    strategic commands ("Hold until reinforced", "Pursue the Prussians").

    Attributes:
        matched: Whether the parser successfully matched a command pattern
        command_type: "tactical" (immediate action) or "strategic" (standing order)
        marshals: List of marshals involved (usually 1, can be multiple for army-wide)
        action: The action to perform (attack, move, defend, etc.)
        target: Target of the action (enemy marshal, region, etc.)
        standing_order: For strategic commands, the ongoing order type
        condition: For conditional orders ("until X", "when Y")
        ambiguity: 0-100, how ambiguous the command was (mock=5)
        strategic_score: 0-100, strategic complexity score (mock=10)
        interpretation: Human-readable description of what was understood
        dialogue: LLM-generated personality response (None in mock mode)
        suggestion: LLM-generated alternative suggestion (None in mock mode)
        confidence: 0.0-1.0, parser confidence in the interpretation
        mode: "mock" or "live" (which parser was used)
        target_stance: For stance_change action, the target stance
        raw_command: Original command text
        type: Command type marker (e.g., "debug" for special commands)
    """
    # Core parsing results
    matched: bool = True
    command_type: str = "tactical"  # tactical | strategic
    marshals: List[str] = field(default_factory=list)
    action: str = "unknown"
    target: Optional[str] = None

    # Strategic command fields (Phase 4+)
    standing_order: Optional[str] = None
    condition: Optional[str] = None

    # Phase 5.2: Strategic order fields
    is_strategic: bool = False
    strategic_type: Optional[str] = None  # "MOVE_TO", "PURSUE", "HOLD", "SUPPORT"
    target_snapshot_location: Optional[str] = None  # For MOVE_TO friendly marshal
    strategic_condition: Optional[Dict[str, Any]] = None  # Serialized StrategicCondition

    # Phase 5.2-C: Interpretation for vague commands (Grouchy clarification system)
    interpreted_target: Optional[str] = None      # Parser's best guess for generic targets
    interpretation_reason: Optional[str] = None   # "nearest", "most threatened"
    alternatives: List[str] = field(default_factory=list)  # Other valid targets

    # Scoring fields
    ambiguity: int = 5  # 0-100, mock default is 5
    strategic_score: int = 10  # 0-100, mock default is 10

    # LLM response fields (populated in live mode)
    interpretation: str = ""
    dialogue: Optional[str] = None
    suggestion: Optional[str] = None

    # Metadata
    confidence: float = 0.9
    mode: str = "mock"
    key_source: str = "none"  # "none", "inhouse", or "byok"
    target_stance: Optional[str] = None
    raw_command: str = ""
    type: Optional[str] = None  # Special type marker (e.g., "debug")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for backward compatibility with existing code.
        Maps to the original return format expected by parser.py and executor.py.
        """
        result = {
            "marshal": self.marshals[0] if self.marshals else None,
            "action": self.action,
            "target": self.target,
            "confidence": self.confidence,
            "raw_command": self.raw_command,
            "mode": self.mode,
            "key_source": self.key_source,
        }

        # Add optional fields if present
        if self.target_stance:
            result["target_stance"] = self.target_stance
        if self.type:
            result["type"] = self.type

        # Add new scoring fields
        result["ambiguity"] = self.ambiguity
        result["strategic_score"] = self.strategic_score
        result["interpretation"] = self.interpretation
        result["command_type"] = self.command_type

        # Add LLM response fields if present
        if self.dialogue:
            result["dialogue"] = self.dialogue
        if self.suggestion:
            result["suggestion"] = self.suggestion
        if self.standing_order:
            result["standing_order"] = self.standing_order
        if self.condition:
            result["condition"] = self.condition

        # Phase 5.2: Strategic order fields
        result["is_strategic"] = self.is_strategic
        if self.is_strategic:
            result["strategic_type"] = self.strategic_type
            result["target_snapshot_location"] = self.target_snapshot_location
            result["strategic_condition"] = self.strategic_condition

        # Phase 5.2-C: Interpretation fields for clarification system
        if self.interpreted_target:
            result["interpreted_target"] = self.interpreted_target
            result["interpretation_reason"] = self.interpretation_reason
            result["alternatives"] = self.alternatives

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParseResult":
        """
        Create ParseResult from a dictionary.
        Useful for testing and backward compatibility.
        """
        marshals = []
        if data.get("marshal"):
            marshals = [data["marshal"]]

        return cls(
            matched=data.get("matched", True),
            command_type=data.get("command_type", "tactical"),
            marshals=marshals,
            action=data.get("action", "unknown"),
            target=data.get("target"),
            standing_order=data.get("standing_order"),
            condition=data.get("condition"),
            ambiguity=data.get("ambiguity", 5),
            strategic_score=data.get("strategic_score", 10),
            interpretation=data.get("interpretation", ""),
            dialogue=data.get("dialogue"),
            suggestion=data.get("suggestion"),
            confidence=data.get("confidence", 0.9),
            mode=data.get("mode", "mock"),
            key_source=data.get("key_source", "none"),
            target_stance=data.get("target_stance"),
            raw_command=data.get("raw_command", ""),
            type=data.get("type"),
            is_strategic=data.get("is_strategic", False),
            strategic_type=data.get("strategic_type"),
            target_snapshot_location=data.get("target_snapshot_location"),
            strategic_condition=data.get("strategic_condition"),
            interpreted_target=data.get("interpreted_target"),
            interpretation_reason=data.get("interpretation_reason"),
            alternatives=data.get("alternatives", []),
        )


@dataclass
class ProviderConfig:
    """
    Configuration for an LLM provider.
    """
    name: str
    api_key_env: str  # Environment variable name for API key
    model: str  # Default model to use
    endpoint: Optional[str] = None  # Custom endpoint (for Groq, local models)
    max_tokens: int = 500
    temperature: float = 0.3  # Low temperature for consistent parsing
