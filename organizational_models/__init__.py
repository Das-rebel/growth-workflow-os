"""Organization design pattern library for AI-native organizations.

Exports:
    ORG_PATTERNS: dict of pattern definitions
    OrgPatternAnalyzer: analyzes signals for org design implications
    get_pattern(identifier): find pattern by name or alias
    list_patterns(): summary of all patterns
"""

from organizational_models.patterns import (
    ORG_PATTERNS,
    OrgPatternAnalyzer,
    get_pattern,
    list_patterns,
)

__all__ = ["ORG_PATTERNS", "OrgPatternAnalyzer", "get_pattern", "list_patterns"]