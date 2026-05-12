"""Workflow architecture — operational bottleneck identification and AI-native redesign.

This module handles:
    - Workflow analysis and bottleneck detection
    - AI-native redesign pattern catalog
    - Automation opportunity identification
    - GTM function mapping (sales, CS, marketing, ops)

Key Classes:
    BottleneckDetector — classify bottlenecks by type, rate automation potential
    RedesignPattern   — catalog of 8 AI-native workflow redesign patterns
    WorkflowAnalyzer  — complete analysis pipeline with deep inference integration

Usage:
    from workflow_architecture import WorkflowAnalyzer, BottleneckDetector

    analyzer = WorkflowAnalyzer()
    result = analyzer.analyze("Sales reps spend 3 hrs/day manually updating CRM from email")
    print(result.recommended_patterns)
    print(result.overall_automation_potential)

    detector = BottleneckDetector()
    bottlenecks = detector.analyze(signal_text)
"""

from workflow_architecture.bottleneck_detector import (
    BottleneckDetector,
    BottleneckSignal,
    BottleneckType,
    GTMFunction,
    AutomationPotential,
    OperationalLeverage,
)

from workflow_architecture.redesign_patterns import (
    RedesignPattern,
    PATTERNS,
    get_pattern,
    get_patterns_by_gtm,
    get_patterns_by_automation_threshold,
    get_all_patterns,
    patterns_summary,
    GROWTH_WORKFLOW_EXAMPLES,
)

from workflow_architecture.workflow_analyzer import (
    WorkflowAnalyzer,
    WorkflowAnalysis,
    quick_analyze,
)

__all__ = [
    "BottleneckDetector",
    "BottleneckSignal",
    "BottleneckType",
    "GTMFunction",
    "AutomationPotential",
    "OperationalLeverage",
    "RedesignPattern",
    "PATTERNS",
    "get_pattern",
    "get_patterns_by_gtm",
    "get_patterns_by_automation_threshold",
    "get_all_patterns",
    "patterns_summary",
    "GROWTH_WORKFLOW_EXAMPLES",
    "WorkflowAnalyzer",
    "WorkflowAnalysis",
    "quick_analyze",
]