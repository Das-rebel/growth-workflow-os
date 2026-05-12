"""
Narrative Strategy — market narrative tracking, positioning analysis,
and competitive narrative differentiation for AI-native growth organizations.

Key exports:
- PositioningAnalyzer + MessagingArchitecture (positioning.py)
- MarketNarrativeTracker + NarrativeGapFinder (market_narrative.py)
- NarrativeAnalyzer + analyze_signals (narrative_analyzer.py)
- All enums: ProductPosture, ValueWedge, BuyerJourney, NarrativeTheme, SignalSource, etc.
"""

from narrative_strategy.positioning import (
    PositioningAnalyzer,
    PositioningSignal,
    PositioningVector,
    ProductPosture,
    BuyerJourney,
    ValueWedge,
    ProofPoint,
    CompetitiveRebuttal,
    MessagingArchitecture,
    NarrativeTracker,
    NarrativeSnapshot,
)

from narrative_strategy.market_narrative import (
    MarketNarrativeTracker,
    NarrativeGapFinder,
    NarrativeMap,
    NarrativeState,
    NarrativeSignal,
    NarrativeTheme,
    PositioningGap,
)

from narrative_strategy.narrative_analyzer import (
    NarrativeAnalyzer,
    SignalProcessor,
    SignalSource,
    NarrativeImplication,
    ProcessedSignal,
    PositioningOpportunity,
    PositioningThreat,
    AnalysisReport,
    analyze_signals,
    to_json,
)

__all__ = [
    # positioning.py
    "PositioningAnalyzer",
    "PositioningSignal",
    "PositioningVector",
    "ProductPosture",
    "BuyerJourney",
    "ValueWedge",
    "ProofPoint",
    "CompetitiveRebuttal",
    "MessagingArchitecture",
    "NarrativeTracker",
    "NarrativeSnapshot",
    # market_narrative.py
    "MarketNarrativeTracker",
    "NarrativeGapFinder",
    "NarrativeMap",
    "NarrativeState",
    "NarrativeSignal",
    "NarrativeTheme",
    "PositioningGap",
    # narrative_analyzer.py
    "NarrativeAnalyzer",
    "SignalProcessor",
    "SignalSource",
    "NarrativeImplication",
    "ProcessedSignal",
    "PositioningOpportunity",
    "PositioningThreat",
    "AnalysisReport",
    "analyze_signals",
    "to_json",
]