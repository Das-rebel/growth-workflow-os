# Narrative Strategy Module

Market narrative tracking, positioning analysis, and competitive narrative differentiation for AI-native growth organizations.

## Architecture

```
narrative_strategy/
├── __init__.py
├── positioning.py      # Positioning analysis engine + messaging architecture
├── market_narrative.py  # Market narrative tracking + gap identification
└── narrative_analyzer.py # Signal processing and report generation
```

## Quick Start

```python
from narrative_strategy import (
    NarrativeAnalyzer, MarketNarrativeTracker, NarrativeGapFinder,
    PositioningAnalyzer, MessagingArchitecture,
    SignalSource, NarrativeTheme, ProductPosture, ValueWedge,
    analyze_signals,
)

# 1. Ingest market signals and get an analysis report
signals = [
    (SignalSource.ANALYST_REPORT, "Agent-first narrative is peaking in enterprise. Gartner 2025."),
    (SignalSource.COMPETITOR_SITE, "Acme Corp claims autonomous revenue intelligence."),
    (SignalSource.CUSTOMER_CALL, "Buyer frustrated with AI-washed products. Wants proof."),
]
report = analyze_signals(signals)
print(report.narrative_health_score)
print(report.recommendations)

# 2. Track market narratives over time
tracker = MarketNarrativeTracker()
# ... add signals via tracker.ingest_signal() ...
narrative_map = tracker.build_narrative_map()
print(tracker.generate_positioning_recommendation())

# 3. Find unclaimed positioning spaces
gap_finder = NarrativeGapFinder(tracker)
gaps = gap_finder.find_gaps()
for gap in gaps:
    print(gap.gap_name, gap.recommended_play)

# 4. Build messaging architecture from positioning vector
analyzer = PositioningAnalyzer()
signals = [...]  # your signals
vectors = analyzer.analyze_signals(signals)
messaging = analyzer.build_messaging_architecture(
    vector=vectors[0],
    differentiation_points=["Outcome-first: we sell revenue not software"],
    competitor_frames=["AI-powered assistant", "Intelligent automation"],
)
print(messaging.category_name, messaging.tagline)
```

## Core Concepts

### Positioning (positioning.py)

- **ProductPosture**: `agent_first`, `copilot_first`, `full_auto`, `hybrid`
- **ValueWedge**: `productivity`, `revenue`, `cost_reduction`, `risk_reduction`
- **BuyerJourney**: `plg` (bottom-up), `sales` (top-down), `hybrid_gtm`
- **PositioningVector**: Where you sit in the positioning space
- **MessagingArchitecture**: Category name, tagline, core message, proof points, competitive rebuttals

### Market Narrative (market_narrative.py)

- **NarrativeTheme**: Tracks which narrative is dominant (agent_first, copilot_first, ai_washed_skepticism, outcome_based, etc.)
- **NarrativeState**: Share of voice, momentum, buyer sentiment, competitive density, maturity
- **NarrativeMap**: Full snapshot of the narrative landscape at a point in time
- **NarrativeTracker**: Records snapshots over time, detects trends

### Signal Analysis (narrative_analyzer.py)

- **SignalSource**: analyst_report, vc_publication, competitor_site, customer_call, job_posting, social_mention, earnings_call, conference_talk
- **SignalProcessor**: Processes raw text from each source type with specific extraction logic
- **NarrativeAnalyzer**: Ingests signals, extracts opportunities/threats, generates AnalysisReport

## Key Classes

| Class | File | Purpose |
|-------|------|---------|
| `PositioningAnalyzer` | positioning.py | Signal-based positioning extraction |
| `NarrativeTracker` | market_narrative.py | Track narrative evolution over time |
| `NarrativeGapFinder` | market_narrative.py | Find unclaimed positioning gaps |
| `NarrativeAnalyzer` | narrative_analyzer.py | Process signals → opportunities/threats |
| `SignalProcessor` | narrative_analyzer.py | Per-source-type signal processing |
| `MessagingArchitecture` | positioning.py | Full messaging hierarchy builder |

## Usage Patterns

### Weekly Narrative Review

```python
# Build current narrative map
tracker = MarketNarrativeTracker()
for sig in weekly_signals:
    tracker.ingest_signal(sig)
current_map = tracker.build_narrative_map()

# Compare with previous week
if len(tracker.maps) >= 2:
    delta = tracker.compare_maps(tracker.maps[-2], tracker.maps[-1])
    print(delta["themes_gained"], delta["themes_lost"])

# Get positioning recommendation
recommendation = tracker.generate_positioning_recommendation()
```

### Competitive Narrative Audit

```python
analyzer = NarrativeAnalyzer()
analyzer.ingest_bulk([
    (SignalSource.COMPETITOR_SITE, competitor_1_homepage_text),
    (SignalSource.COMPETITOR_SITE, competitor_2_homepage_text),
    (SignalSource.ANALYST_REPORT, industry_report_text),
])
report = analyzer.generate_report()
# report.threats contains competitor narrative threats
# report.recommendations contains suggested responses
```

### Positioning Refresh

```python
analyzer = PositioningAnalyzer()
vectors = analyzer.analyze_signals(signals)
vector = vectors[0]

messaging = analyzer.build_messaging_architecture(
    vector=vector,
    differentiation_points=["Real autonomous action, not just AI branding"],
    competitor_frames=["AI copilot", "Intelligent automation"],
)
# messaging contains: category_name, category_frame, tagline, core_message,
# supporting_messages, proof_points, competitive_rebuttals
```