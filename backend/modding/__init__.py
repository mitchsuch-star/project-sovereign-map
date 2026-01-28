"""
Modding support utilities for Project Sovereign.

This package provides validation and helper functions for creating
custom scenarios, marshals, and regions via JSON files.

Usage:
    # Validate a scenario file
    python -m backend.modding.validator mods/my_scenario.json

    # Generate documentation from code
    python -m backend.modding.doc_generator all
"""

from .validator import (
    validate_marshal,
    validate_region,
    validate_scenario,
    ValidationResult,
    ValidationError
)

__all__ = [
    "validate_marshal",
    "validate_region",
    "validate_scenario",
    "ValidationResult",
    "ValidationError"
]
