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

    Thresholds:
    - 80+ : Auto-correct silently (high confidence)
    - 60-79: Return suggestion for confirmation
    - <60  : Return error with nearby options
    """

    # Threshold constants
    AUTO_CORRECT_THRESHOLD = 80  # Auto-correct without asking
    SUGGEST_THRESHOLD = 60       # Suggest with confirmation

    def __init__(self):
        """Initialize fuzzy matcher."""
        pass

    def match(
        self,
        query: str,
        candidates: List[str],
        threshold: int = 80
    ) -> Optional[Tuple[str, int]]:
        """
        Find best fuzzy match for query string.

        Args:
            query: User input string (may have typos)
            candidates: List of valid options to match against
            threshold: Minimum similarity score (0-100)

        Returns:
            Tuple of (best_match, score) if found, else None

        Example:
            >>> matcher = FuzzyMatcher()
            >>> matcher.match("Waterlo", ["Waterloo", "Paris", "Belgium"])
            ("Waterloo", 93)
            >>> matcher.match("Asdf", ["Waterloo", "Paris"], threshold=80)
            None
        """
        if not query or not candidates:
            return None

        # Use fuzzywuzzy to find best match
        # process.extractOne returns (match, score) or None
        result = process.extractOne(
            query,
            candidates,
            scorer=fuzz.ratio,  # Simple ratio comparison
            score_cutoff=threshold
        )

        if result:
            best_match, score = result
            return (best_match, score)

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

        # Try fuzzy match with auto-correct threshold
        result = self.match(query, candidates, threshold=self.AUTO_CORRECT_THRESHOLD)

        if result:
            match, score = result
            return {
                "action": "auto_correct",
                "match": match,
                "score": score,
                "suggestions": []
            }

        # Try fuzzy match with suggest threshold
        result = self.match(query, candidates, threshold=self.SUGGEST_THRESHOLD)

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
# TODO Phase 6: Godot autocomplete dropdown UI


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
