"""Single source for the recruit ARM the player asked for.

``requested_type`` drives the soft-correction message in ``_execute_recruit``
("Ney commands no cavalry, Sire — infantry raised instead"). It was extracted
only inside the mock parser's recruit branch, which left two holes:

  1. On the LIVE path it was unreachable. PARSE_TOOL has no ``requested_type``
     property and the prompt never mentions one, so the field the executor
     reads could only ever be None — any recruit phrasing the fast parser
     failed to classify (and therefore handed to the LLM) silently lost the
     arm, and the player was never told why he got infantry.
  2. When ``UNRESOLVED_ADDRESS_CONFIDENCE`` dropped a fast parse below the 0.7
     gate, the fast parser HAD the arm and the live result discarded it.

Deriving it deterministically from the raw text — rather than adding a schema
field and asking the model — is both cheaper and GR6-purer: the arm is a fact
about the words the player typed, not a judgement call.
"""

import re
from typing import Optional

# Cavalry is checked FIRST so "horse artillery" stays cavalry.
_CAVALRY_KEYWORDS = ("cavalry", "horse", "rider", "horsemen")

# PF-7 review fix: WORD-BOUNDARY match. The bare substring "gun" collided with
# the region name Burgundy (bur-GUN-dy), firing a spurious soft-correction on
# "recruit infantry at Burgundy".
_ARTILLERY_RE = re.compile(
    r'\b(?:artillery|cannons?|guns?|batter(?:y|ies)|artillerie)\b')

_INFANTRY_KEYWORDS = ("infantry", "foot")


def extract_requested_arm(command_text: Optional[str]) -> Optional[str]:
    """The arm named in ``command_text``, or None.

    Order is load-bearing and preserved from the mock parser's original
    branch — see the module docstring and the two comments inline.
    """
    if not command_text:
        return None
    lowered = command_text.lower()
    if any(kw in lowered for kw in _CAVALRY_KEYWORDS):
        return "cavalry"
    if _ARTILLERY_RE.search(lowered):
        return "artillery"
    if any(kw in lowered for kw in _INFANTRY_KEYWORDS):
        return "infantry"
    return None
