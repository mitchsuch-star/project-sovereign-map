"""
Fuzzy String Matching for Project Sovereign

Provides typo-tolerant matching for region and marshal names.
Foundation for Phase 3 LLM interpretation and Phase 6 autocomplete UI.
"""

from typing import List, Optional, Tuple
from fuzzywuzzy import process, fuzz


class FuzzyMatcher:
    """
    Fuzzy string matcher for typo tolerance.

    Uses Levenshtein distance to find best matches for user input.
    Adjusts thresholds for short strings (e.g., "Ney" → "Nay").

    Thresholds:
    - 80+ : Auto-correct silently (high confidence)
    - 60-79: Return suggestion for confirmation
    - <60  : Return error with nearby options

    Short name handling (<=4 chars):
    - Uses lower thresholds (70/50) for short names
    - Uses token_set_ratio for better partial matching
    """

    # Threshold constants for normal names (5+ chars)
    AUTO_CORRECT_THRESHOLD = 80  # Auto-correct without asking
    SUGGEST_THRESHOLD = 60       # Suggest with confirmation

    # Lower thresholds for short names (<=4 chars)
    SHORT_NAME_AUTO_CORRECT = 70
    SHORT_NAME_SUGGEST = 50

    def __init__(self):
        """Initialize fuzzy matcher."""
        pass

    def _get_thresholds(self, query: str) -> Tuple[int, int]:
        """Get appropriate thresholds based on query length."""
        # Very short (1-2 chars) - always suggest, never auto-correct
        if len(query) <= 2:
            return (100, self.SHORT_NAME_SUGGEST)  # 100 = only exact match auto-corrects
        # Short names (3-4 chars) - lower threshold
        if len(query) <= 4:
            return (self.SHORT_NAME_AUTO_CORRECT, self.SHORT_NAME_SUGGEST)
        return (self.AUTO_CORRECT_THRESHOLD, self.SUGGEST_THRESHOLD)

    def _get_best_score(self, query: str, candidate: str) -> int:
        """
        Get best fuzzy score using multiple algorithms.

        For short names (3-4 chars), combines ratio with partial_ratio for better matching.
        Very short names (1-2 chars) only use standard ratio to avoid false positives.
        """
        # Standard ratio
        ratio_score = fuzz.ratio(query.lower(), candidate.lower())

        # For very short queries (1-2 chars), only use standard ratio
        # This prevents "N" from matching "Ney" with 100% partial match
        if len(query) <= 2:
            return ratio_score

        # For short names (3-4 chars), also check partial ratio
        if len(query) <= 4 or len(candidate) <= 4:
            partial_score = fuzz.partial_ratio(query.lower(), candidate.lower())
            # Use the better of the two
            return max(ratio_score, partial_score)

        return ratio_score

    def match(
        self,
        query: str,
        candidates: List[str],
        threshold: int = None
    ) -> Optional[Tuple[str, int]]:
        """
        Find best fuzzy match for query string.

        Args:
            query: User input string (may have typos)
            candidates: List of valid options to match against
            threshold: Minimum similarity score (0-100), auto-adjusts for short names

        Returns:
            Tuple of (best_match, score) if found, else None

        Example:
            >>> matcher = FuzzyMatcher()
            >>> matcher.match("Waterlo", ["Waterloo", "Paris", "Belgium"])
            ("Waterloo", 93)
            >>> matcher.match("Nay", ["Ney", "Davout"])  # Short name
            ("Ney", 67)  # Lower threshold allows match
        """
        if not query or not candidates:
            return None

        # Use dynamic threshold for short names
        if threshold is None:
            auto_threshold, _ = self._get_thresholds(query)
            threshold = auto_threshold

        # Find best match using our custom scoring
        best_match = None
        best_score = 0

        for candidate in candidates:
            score = self._get_best_score(query, candidate)
            if score > best_score:
                best_score = score
                best_match = candidate

        if best_score >= threshold:
            return (best_match, best_score)

        return None

    def match_with_context(
        self,
        query: str,
        candidates: List[str]
    ) -> dict:
        """
        Match with contextual response (auto-correct, suggest, or error).

        Args:
            query: User input string
            candidates: List of valid options

        Returns:
            Dict with:
            - action: "auto_correct", "suggest", or "error"
            - match: Best match string (if found)
            - score: Similarity score
            - suggestions: List of near matches (for errors)

        Example:
            >>> matcher.match_with_context("Waterlo", ["Waterloo", "Paris"])
            {"action": "auto_correct", "match": "Waterloo", "score": 93}
        """
        if not query or not candidates:
            return {
                "action": "error",
                "match": None,
                "score": 0,
                "suggestions": []
            }

        # Check exact match first (case-insensitive)
        query_lower = query.lower()
        for candidate in candidates:
            if candidate.lower() == query_lower:
                return {
                    "action": "exact",
                    "match": candidate,
                    "score": 100,
                    "suggestions": []
                }

        # Get dynamic thresholds based on query length
        auto_threshold, suggest_threshold = self._get_thresholds(query)

        # Try fuzzy match with auto-correct threshold
        result = self.match(query, candidates, threshold=auto_threshold)

        if result:
            match, score = result
            return {
                "action": "auto_correct",
                "match": match,
                "score": score,
                "suggestions": []
            }

        # Try fuzzy match with suggest threshold
        result = self.match(query, candidates, threshold=suggest_threshold)

        if result:
            match, score = result
            return {
                "action": "suggest",
                "match": match,
                "score": score,
                "suggestions": [match]
            }

        # No good match - return top 3 suggestions
        all_matches = process.extract(
            query,
            candidates,
            scorer=fuzz.ratio,
            limit=3
        )

        suggestions = [m[0] for m in all_matches] if all_matches else []

        return {
            "action": "error",
            "match": None,
            "score": 0,
            "suggestions": suggestions
        }

    def match_case_insensitive(
        self,
        query: str,
        candidates: List[str],
        threshold: int = 80
    ) -> Optional[Tuple[str, int]]:
        """
        Case-insensitive fuzzy matching.

        Args:
            query: User input (any case)
            candidates: Valid options (any case)
            threshold: Minimum score

        Returns:
            Best match with original casing from candidates
        """
        # Convert all to lowercase for matching
        query_lower = query.lower()
        candidates_lower = [c.lower() for c in candidates]

        result = self.match(query_lower, candidates_lower, threshold)

        if result:
            match_lower, score = result
            # Find original casing
            for candidate in candidates:
                if candidate.lower() == match_lower:
                    return (candidate, score)

        return None


# TODO Phase 3: LLM will interpret commands with context
# TODO Phase 3: Add search_regions() and search_marshals() functions
# TODO Phase 6: Godot autocomplete dropdown UI with iPhone-style suggestions
#   - Show suggestions as user types (like iOS autocomplete)
#   - Display 3-5 candidates below input field
#   - Tap/click to select, or keep typing
#   - Keyboard navigation (arrow keys, tab to accept)
#   - Animate suggestions appearing/disappearing


if __name__ == "__main__":
    """Quick test of fuzzy matcher."""
    print("=" * 60)
    print("FUZZY MATCHER TEST")
    print("=" * 60)

    matcher = FuzzyMatcher()

    # Test 1: High confidence auto-correct
    print("\nTest 1: Typo with high confidence")
    result = matcher.match_with_context("Waterlo", ["Waterloo", "Paris", "Belgium"])
    print(f"Query: 'Waterlo'")
    print(f"Result: {result}")

    # Test 2: Medium confidence suggestion
    print("\nTest 2: Partial match")
    result = matcher.match_with_context("Bruss", ["Brussels", "Bavaria", "Britain"])
    print(f"Query: 'Bruss'")
    print(f"Result: {result}")

    # Test 3: Low confidence error
    print("\nTest 3: No good match")
    result = matcher.match_with_context("Asdfgh", ["Waterloo", "Paris", "Belgium"])
    print(f"Query: 'Asdfgh'")
    print(f"Result: {result}")

    # Test 4: Exact match
    print("\nTest 4: Exact match (case-insensitive)")
    result = matcher.match_with_context("waterloo", ["Waterloo", "Paris", "Belgium"])
    print(f"Query: 'waterloo'")
    print(f"Result: {result}")

    # Test 5: Marshal name typo
    print("\nTest 5: Marshal typo")
    result = matcher.match_with_context("Davot", ["Davout", "Ney", "Grouchy"])
    print(f"Query: 'Davot'")
    print(f"Result: {result}")

    print("\n" + "=" * 60)
    print("FUZZY MATCHER TEST COMPLETE!")
    print("=" * 60)
