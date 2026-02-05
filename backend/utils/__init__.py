"""Utility modules for Project Sovereign."""


def ordinal(n: int) -> str:
    """Convert number to ordinal string (1 -> '1st', 2 -> '2nd', 111 -> '111th', etc.)."""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return f"{n}{suffix}"
