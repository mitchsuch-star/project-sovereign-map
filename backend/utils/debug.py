"""Debug output utility. Gates print statements behind a global debug flag."""

import os

# Reads DEBUG_MODE from environment, defaults to True for backward compatibility
# Set INK_DEBUG=0 to silence debug prints
_DEBUG_ENABLED = os.environ.get("INK_DEBUG", "1") != "0"


def debug_print(*args, **kwargs):
    """Print only when debug output is enabled."""
    if _DEBUG_ENABLED:
        print(*args, **kwargs)
