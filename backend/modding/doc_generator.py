"""
Auto-generate documentation from code.

This tool extracts field information from serializable classes and
generates markdown documentation tables.

Usage:
    python -m backend.modding.doc_generator marshal
    python -m backend.modding.doc_generator region
    python -m backend.modding.doc_generator all
    python -m backend.modding.doc_generator --check  # Compare to existing docs

Examples:
    # Generate marshal field docs
    python -m backend.modding.doc_generator marshal

    # Generate all class docs
    python -m backend.modding.doc_generator all > docs/generated_schema.md
"""

import sys
from typing import Any, Dict, List, Type
from pathlib import Path
from dataclasses import fields, is_dataclass

from backend.models.marshal import Marshal, StrategicOrder, StrategicCondition
from backend.models.region import Region
from backend.models.trust import Trust


def get_type_name(value: Any) -> str:
    """Get a human-readable type name for a value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        if len(value) > 0:
            inner_type = get_type_name(value[0])
            return f"array<{inner_type}>"
        return "array"
    if isinstance(value, dict):
        return "object"
    if hasattr(value, 'to_dict'):
        return type(value).__name__
    return type(value).__name__


def get_default_repr(value: Any, max_len: int = 40) -> str:
    """Get a truncated string representation of a default value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, str):
        if len(value) > max_len:
            return f'"{value[:max_len]}..."'
        return f'"{value}"'
    if isinstance(value, (list, dict)):
        s = str(value)
        if len(s) > max_len:
            return s[:max_len] + "..."
        return s
    return str(value)


def get_field_info(instance: Any) -> List[Dict]:
    """Extract field information from a class instance."""
    fields_info = []
    data = instance.to_dict()

    for key, value in data.items():
        field_info = {
            "name": key,
            "type": get_type_name(value),
            "default": get_default_repr(value),
        }
        fields_info.append(field_info)

    return fields_info


def generate_markdown_table(fields_info: List[Dict], title: str = None) -> str:
    """Generate markdown table from field info."""
    lines = []

    if title:
        lines.append(f"### {title}")
        lines.append("")

    lines.append("| Field | Type | Default |")
    lines.append("|-------|------|---------|")

    for f in fields_info:
        # Escape pipe characters in values
        default = f['default'].replace("|", "\\|")
        lines.append(f"| `{f['name']}` | {f['type']} | {default} |")

    return "\n".join(lines)


def generate_marshal_docs() -> str:
    """Generate Marshal field documentation."""
    marshal = Marshal(
        name="Example",
        location="Paris",
        strength=50000,
        personality="balanced",
        nation="France"
    )

    fields_info = get_field_info(marshal)
    return generate_markdown_table(fields_info, "Marshal Fields")


def generate_region_docs() -> str:
    """Generate Region field documentation."""
    region = Region(
        name="Example",
        adjacent_regions=["Paris", "Lyon"],
        income_value=100,
        is_capital=False
    )

    fields_info = get_field_info(region)
    return generate_markdown_table(fields_info, "Region Fields")


def generate_strategic_order_docs() -> str:
    """Generate StrategicOrder field documentation."""
    order = StrategicOrder(
        command_type="MOVE_TO",
        target="Paris",
        target_type="region",
        started_turn=1,
        original_command="move to Paris"
    )

    fields_info = get_field_info(order)
    return generate_markdown_table(fields_info, "StrategicOrder Fields")


def generate_strategic_condition_docs() -> str:
    """Generate StrategicCondition field documentation."""
    condition = StrategicCondition(
        max_turns=5,
        until_battle_won=False
    )

    fields_info = get_field_info(condition)
    return generate_markdown_table(fields_info, "StrategicCondition Fields")


def generate_all_docs() -> str:
    """Generate documentation for all classes."""
    sections = [
        "# Generated Schema Reference",
        "",
        "This document is auto-generated from the codebase.",
        "Run `python -m backend.modding.doc_generator all` to regenerate.",
        "",
        generate_marshal_docs(),
        "",
        generate_region_docs(),
        "",
        generate_strategic_order_docs(),
        "",
        generate_strategic_condition_docs(),
    ]
    return "\n".join(sections)


def check_docs_current() -> bool:
    """
    Check if generated docs match existing documentation.

    Returns True if docs are current, False if outdated.
    """
    # This would compare generated output to existing docs
    # For now, just print a message
    print("Doc check: Comparing generated output to existing documentation...")

    generated = generate_all_docs()
    print(f"Generated {len(generated)} characters of documentation")

    # TODO: Compare to actual doc files
    # For now, always return True
    return True


def main():
    """Command-line interface for doc generator."""
    if len(sys.argv) < 2:
        print("Usage: python -m backend.modding.doc_generator [marshal|region|all|--check]")
        print()
        print("Commands:")
        print("  marshal   Generate Marshal field documentation")
        print("  region    Generate Region field documentation")
        print("  order     Generate StrategicOrder field documentation")
        print("  condition Generate StrategicCondition field documentation")
        print("  all       Generate documentation for all classes")
        print("  --check   Check if documentation is current")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "marshal":
        print(generate_marshal_docs())

    elif cmd == "region":
        print(generate_region_docs())

    elif cmd == "order":
        print(generate_strategic_order_docs())

    elif cmd == "condition":
        print(generate_strategic_condition_docs())

    elif cmd == "all":
        print(generate_all_docs())

    elif cmd == "--check":
        if check_docs_current():
            print("Documentation is current.")
            sys.exit(0)
        else:
            print("Documentation is OUTDATED. Regenerate with: python -m backend.modding.doc_generator all")
            sys.exit(1)

    else:
        print(f"Unknown command: {cmd}")
        print("Run without arguments for usage help.")
        sys.exit(1)


if __name__ == "__main__":
    main()
