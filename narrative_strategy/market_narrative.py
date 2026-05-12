"""
Market Narrative Tracker for AI-Native GTM

Tracks the dominant narratives in the AI-native GTM space:
- Agent-first vs Copilot-first vs Full-auto
- Which narratives are gaining or losing share
- Narrative gaps where a company can establish ownership
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import re
from datetime import datetime, timedelta


class NarrativeTheme(str, Enum):
    """Primary narrative themes in AI-native GTM."""
    AGENT_FIRST = "agent_first"
    COPILOT_FIRST = "copilot_first"
    FULL_AUTO = "full_auto"
    AI_WRASHED_SKEPTICISM = "ai_washed_skepticism"  # "Prove it or it's hype"
    OUTCOME_BASED = "outcome_based"               # "We sell outcomes, not software"
    TRUST_ANXIOUS = "trust_anxious"               # "How do we know the AI won't fail catastrophically"
    RESISTANCE = "resistance"                      # "AI will replace our jobs"
    INTEGRATION_ANXIETY = "integration_anxiety"    # "Will it fit our stack"


@dataclass
class NarrativeSignal:
    """A piece of evidence about a narrative's state."""
    source: str                    # e.g., "Sequoia 2025 AI Report", "Customer call"
    theme: NarrativeTheme
    text: str                      # Raw text from the source
    sentiment: float               # -1.0 (narrative dying) to +1.0 (narrative surging)
    timestamp: str                 # ISO date
    reach: Optional[str] = None   # e.g., "high", "medium", "low"


@dataclass
class NarrativeState:
    """Snapshot of a narrative theme's current state."""
    theme: NarrativeTheme
    share_of_voice: float          # Fraction of market conversation
    momentum: float               # -1.0 losing share, +1.0 gaining share
    buyer_sentiment: float        # -1.0 skeptical, +1.0 eager
    competitive_density: float    # 0.0 low competition, 1.0 saturated
    maturity: str                  # "emerging", "peak", "commoditizing", "niche"


@dataclass
class NarrativeMap:
    """Full map of the AI-native GTM narrative landscape."""
    timestamp: str
    states: list[NarrativeState]
    dominant_theme: Optional[NarrativeTheme] = None
    emerging_opportunities: list[str] = field(default_factory=list)
    threats: list[str] = field(default_factory=list)

    def get_state(self, theme: NarrativeTheme) -> Optional[NarrativeState]:
        for s in self.states:
            if s.theme == theme:
                return s
        return None


class MarketNarrativeTracker:
    """
    Tracks dominant narratives in the AI-native GTM space.

    Builds a narrative map over time by aggregating signals from:
    - Analyst reports (Gartner, Forrester, IDC)
    - VC funding announcements and theses
    - Product launch messaging from competitors
    - Customer conversation themes
    - Job posting trends (hiring for agentic vs copilot roles)
    """

    # Narrative arc: how themes typically evolve
    NARRATIVE_LIFECYCLE = {
        NarrativeTheme.AGENT_FIRST: {
            "2024_Q1": "emerging", "2024_Q2": "emerging", "2024_Q3": "peak",
            "2024_Q4": "peak", "2025_Q1": "commoditizing", "2025_Q2": "niche"
        },
        NarrativeTheme.COPILOT_FIRST: {
            "2023_Q3": "emerging", "2024_Q1": "peak", "2025_Q1": "commoditizing"
        },
    }

    # Theme co-occurrence: which themes tend to appear together vs oppose each other
    THEMATIC_ALLIANCES = {
        NarrativeTheme.AGENT_FIRST: [NarrativeTheme.OUTCOME_BASED],
        NarrativeTheme.COPILOT_FIRST: [NarrativeTheme.TRUST_ANXIOUS, NarrativeTheme.INTEGRATION_ANXIETY],
        NarrativeTheme.FULL_AUTO: [NarrativeTheme.RESISTANCE, NarrativeTheme.AI_WRASHED_SKEPTICISM],
    }

    THEMATIC_OPPOSITIONS = {
        NarrativeTheme.AGENT_FIRST: [NarrativeTheme.TRUST_ANXIOUS, NarrativeTheme.RESISTANCE],
        NarrativeTheme.COPILOT_FIRST: [NarrativeTheme.FULL_AUTO],
        NarrativeTheme.AI_WRASHED_SKEPTICISM: [NarrativeTheme.AGENT_FIRST, NarrativeTheme.FULL_AUTO],
    }

    def __init__(self):
        self.signals: list[NarrativeSignal] = []
        self.maps: list[NarrativeMap] = []

    def ingest_signal(self, signal: NarrativeSignal) -> None:
        """Ingest a new narrative signal."""
        self.signals.append(signal)

    def ingest_signals_bulk(self, signals: list[NarrativeSignal]) -> None:
        """Ingest multiple signals at once."""
        self.signals.extend(signals)

    def build_narrative_map(self, timestamp: Optional[str] = None) -> NarrativeMap:
        """
        Build the current narrative map by analyzing all signals.

        Returns a NarrativeMap showing:
        - Share of voice for each major theme
        - Momentum (gaining vs losing)
        - Buyer sentiment
        - Competitive density
        - Maturity stage
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()

        # Compute share of voice
        theme_counts: dict[NarrativeTheme, list[NarrativeSignal]] = {
            t: [] for t in NarrativeTheme
        }
        for sig in self.signals:
            theme_counts[sig.theme].append(sig)

        total_signals = len(self.signals) or 1
        share_of_voice = {
            theme: len(sigs) / total_signals
            for theme, sigs in theme_counts.items()
        }

        # Compute momentum from sentiment trajectory
        momentum = self._compute_momentum(theme_counts)

        # Compute buyer sentiment
        buyer_sentiment = self._compute_buyer_sentiment(theme_counts)

        # Compute competitive density
        competitive_density = self._compute_competitive_density(theme_counts)

        # Determine maturity
        maturity = self._determine_maturity(share_of_voice, momentum)

        states = []
        for theme in NarrativeTheme:
            state = NarrativeState(
                theme=theme,
                share_of_voice=share_of_voice.get(theme, 0.0),
                momentum=momentum.get(theme, 0.0),
                buyer_sentiment=buyer_sentiment.get(theme, 0.0),
                competitive_density=competitive_density.get(theme, 0.0),
                maturity=maturity.get(theme, "emerging"),
            )
            states.append(state)

        # Find dominant theme (highest share of voice)
        dominant = max(states, key=lambda s: s.share_of_voice)

        # Identify opportunities
        opportunities = self._find_opportunities(states)

        # Identify threats
        threats = self._find_threats(states)

        narrative_map = NarrativeMap(
            timestamp=timestamp,
            states=states,
            dominant_theme=dominant.theme if dominant.share_of_voice > 0.15 else None,
            emerging_opportunities=opportunities,
            threats=threats,
        )

        self.maps.append(narrative_map)
        return narrative_map

    def _compute_momentum(self,
                          theme_counts: dict[NarrativeTheme, list[NarrativeSignal]]) -> dict[NarrativeTheme, float]:
        """Compute momentum from recent sentiment trends."""
        momentum = {}

        # Sort signals by timestamp
        for theme in NarrativeTheme:
            sigs = sorted(theme_counts[theme], key=lambda s: s.timestamp)

            if len(sigs) < 2:
                momentum[theme] = 0.0
                continue

            # Compare first half vs second half sentiment
            mid = len(sigs) // 2
            first_half = sigs[:mid] if mid > 0 else sigs
            second_half = sigs[mid:]

            if not first_half or not second_half:
                momentum[theme] = 0.0
                continue

            first_avg = sum(s.sentiment for s in first_half) / len(first_half)
            second_avg = sum(s.sentiment for s in second_half) / len(second_half)

            momentum[theme] = round(second_avg - first_avg, 3)

        return momentum

    def _compute_buyer_sentiment(self,
                                 theme_counts: dict[NarrativeTheme, list[NarrativeSignal]]) -> dict[NarrativeTheme, float]:
        """Aggregate buyer sentiment per theme."""
        sentiment = {}

        for theme in NarrativeTheme:
            sigs = theme_counts[theme]
            if not sigs:
                sentiment[theme] = 0.0
            else:
                # Weight by reach if available
                total_weight = 0.0
                weighted_sum = 0.0
                for sig in sigs:
                    weight = 1.0 if not sig.reach else {"high": 3.0, "medium": 1.5, "low": 0.5}.get(sig.reach, 1.0)
                    weighted_sum += sig.sentiment * weight
                    total_weight += weight
                sentiment[theme] = round(weighted_sum / total_weight, 3) if total_weight else 0.0

        return sentiment

    def _compute_competitive_density(self,
                                     theme_counts: dict[NarrativeTheme, list[NarrativeSignal]]) -> dict[NarrativeTheme, float]:
        """Estimate competitive density from signal diversity."""
        density = {}

        for theme in NarrativeTheme:
            sigs = theme_counts[theme]
            if not sigs:
                density[theme] = 0.0
                continue

            # Count unique sources
            sources = set(s.source for s in sigs)
            # Also look for number of distinct competitors mentioned
            competitor_pattern = re.compile(r'\b(?:company|vendor|startup|tool)\s+([A-Z][a-z]+)', re.I)
            competitors = set()
            for sig in sigs:
                competitors.update(competitor_pattern.findall(sig.text))

            # Density: high if many sources and many competitors
            source_score = min(len(sources) / 5, 1.0)  # Normalize to 5 sources
            competitor_score = min(len(competitors) / 10, 1.0)  # Normalize to 10 competitors

            density[theme] = round((source_score + competitor_score) / 2, 3)

        return density

    def _determine_maturity(self,
                           share_of_voice: dict[NarrativeTheme, float],
                           momentum: dict[NarrativeTheme, float]) -> dict[NarrativeTheme, str]:
        """Determine lifecycle maturity for each theme."""
        maturity = {}

        for theme in NarrativeTheme:
            share = share_of_voice.get(theme, 0.0)
            mom = momentum.get(theme, 0.0)

            if share < 0.05:
                maturity[theme] = "emerging"
            elif share > 0.40 and mom < -0.1:
                maturity[theme] = "commoditizing"
            elif share > 0.30 and mom > 0.1:
                maturity[theme] = "peak"
            elif share > 0.20:
                maturity[theme] = "peak"
            elif mom > 0.2:
                maturity[theme] = "emerging"
            else:
                maturity[theme] = "niche"

        return maturity

    def _find_opportunities(self, states: list[NarrativeState]) -> list[str]:
        """Find narrative gaps where a company can own positioning."""
        opportunities = []

        for state in states:
            # Low share + positive buyer sentiment = opportunity
            if state.share_of_voice < 0.20 and state.buyer_sentiment > 0.2:
                opportunities.append(
                    f"Underserved narrative space: {state.theme.value}. "
                    f"Share={state.share_of_voice:.1%}, buyer sentiment={state.buyer_sentiment:+.2f}. "
                    f"Momentum is {state.momentum:+.2f}."
                )

            # Emerging + low competition = opportunity
            if state.maturity == "emerging" and state.competitive_density < 0.3:
                opportunities.append(
                    f"Emerging narrative with low competition: {state.theme.value}. "
                    f"Early mover advantage available."
                )

        return opportunities

    def _find_threats(self, states: list[NarrativeState]) -> list[str]:
        """Identify narrative-level threats."""
        threats = []

        for state in states:
            # Commodity threat: high share + negative momentum
            if state.share_of_voice > 0.30 and state.momentum < -0.1:
                threats.append(
                    f"Narrative commoditization: {state.theme.value} is becoming table stakes, "
                    f"reducing differentiation value. Consider pivot or differentiation."
                )

            # Saturation threat: high density
            if state.competitive_density > 0.7 and state.share_of_voice > 0.20:
                threats.append(
                    f"Narrative saturation: {state.theme.value} has too many competitors. "
                    f"Differentiate by substantiating with concrete outcomes."
                )

        return threats

    def compare_maps(self, earlier: NarrativeMap, later: NarrativeMap) -> dict:
        """
        Compare two narrative maps to extract delta.

        Useful for weekly/monthly reporting on narrative shifts.
        """
        deltas = {
            "themes_gained": [],
            "themes_lost": [],
            "opportunities_opened": [],
            "opportunities_closed": [],
        }

        earlier_states = {s.theme: s for s in earlier.states}
        later_states = {s.theme: s for s in later.states}

        for theme in NarrativeTheme:
            e = earlier_states.get(theme)
            l = later_states.get(theme)

            if e and l:
                share_delta = l.share_of_voice - e.share_of_voice
                if share_delta > 0.05:
                    deltas["themes_gained"].append({
                        "theme": theme.value,
                        "share_delta": round(share_delta, 3),
                        "momentum_delta": round(l.momentum - e.momentum, 3),
                    })
                elif share_delta < -0.05:
                    deltas["themes_lost"].append({
                        "theme": theme.value,
                        "share_delta": round(share_delta, 3),
                        "momentum_delta": round(l.momentum - e.momentum, 3),
                    })

        for opp in later.emerging_opportunities:
            if opp not in earlier.emerging_opportunities:
                deltas["opportunities_opened"].append(opp)

        for opp in earlier.emerging_opportunities:
            if opp not in later.emerging_opportunities:
                deltas["opportunities_closed"].append(opp)

        return deltas

    def generate_positioning_recommendation(self) -> str:
        """
        Generate a narrative positioning recommendation based on current map.

        Returns a narrative recommendation suitable for executive audiences.
        """
        if not self.maps:
            return "Insufficient data. Build narrative map first via build_narrative_map()."

        current = self.maps[-1]

        # Rule-based recommendation engine
        agent_state = current.get_state(NarrativeTheme.AGENT_FIRST)
        copilot_state = current.get_state(NarrativeTheme.COPILOT_FIRST)
        skepticism_state = current.get_state(NarrativeTheme.AI_WRASHED_SKEPTICISM)

        recommendations = []

        if agent_state and agent_state.share_of_voice > 0.30:
            if agent_state.momentum > 0.1:
                recommendations.append(
                    "Agent-first narrative is peaking. Move to substantiate with outcome data "
                    "before commoditization sets in."
                )
            elif agent_state.competitive_density > 0.6:
                recommendations.append(
                    "Agent-first is saturated. Differentiate through trust and integration depth, "
                    "not just autonomous capability claims."
                )

        if skepticism_state and skepticism_state.buyer_sentiment < -0.2:
            recommendations.append(
                "AI-washed skepticism is high. Position on verifiability and auditability — "
                "'prove it' is a competitive advantage."
            )

        if copilot_state and copilot_state.maturity == "commoditizing":
            recommendations.append(
                "Copilot-first is commoditizing. Pivot messaging from 'AI assists' to "
                "'AI amplifies outcome velocity' to maintain premium."
            )

        # Find low-density high-sentiment opportunities
        for state in current.states:
            if (state.share_of_voice < 0.15 and
                state.buyer_sentiment > 0.3 and
                state.competitive_density < 0.3):
                recommendations.append(
                    f"Unclaimed narrative space: {state.theme.value}. "
                    f"Low competition, high buyer appetite. Consider early ownership."
                )

        if not recommendations:
            recommendations.append(
                "No clear narrative gap identified. Focus on differentiation through "
                "specific outcome claims and proof points over generic AI-native branding."
            )

        return "\n".join(f"- {r}" for r in recommendations)


# ---------------------------------------------------------------------------
# NarrativeGapFinder: Identify owned positioning space
# ---------------------------------------------------------------------------

@dataclass
class PositioningGap:
    """An unclaimed or underserved positioning space."""
    gap_name: str                      # e.g., "AI-native trust infrastructure"
    current_narratives: list[str]      # What's currently claiming this space
    buyer_intent_signal: float         # How much buyer demand exists (0-1)
    competitive_presence: float        # How contested this space is (0-1)
    recommended_play: str             # What narrative to run to own this space


class NarrativeGapFinder:
    """
    Identifies narrative gaps where a company can own a positioning space.

    Uses a buyer-intent signal vs competitive-presence matrix to find
    underserved areas in the narrative landscape.
    """

    # Predefined narrative space templates based on common AI-native GTM plays
    NARRATIVE_SPACES = [
        ("agent_first_revenue", "Agent-first for revenue teams", ["agent_first", "revenue"]),
        ("copilot_outcome_verification", "Copilot with verifiable outcomes", ["copilot_first", "outcome_based"]),
        ("autonomous_integration", "Autonomous integration without ops overhead", ["full_auto", "integration_anxiety"]),
        ("trust_auditability", "AI-native trust and auditability", ["ai_washed_skepticism", "trust_anxious"]),
        ("resistance_handling", "AI that earns buy-in from skeptical teams", ["resistance", "trust_anxious"]),
    ]

    def __init__(self, tracker: MarketNarrativeTracker):
        self.tracker = tracker

    def find_gaps(self) -> list[PositioningGap]:
        """
        Analyze the current narrative map and identify gaps.

        Returns gaps ranked by opportunity score (buyer_intent - competitive_presence).
        """
        if not self.tracker.maps:
            return []

        current_map = self.tracker.maps[-1]

        # Map NarrativeThemes to NARRATIVE_SPACES identifiers
        space_scores = self._score_narrative_spaces(current_map)

        gaps = []
        for (space_name, description, theme_tags), scores in space_scores.items():
            buyer_intent = scores["buyer_sentiment_avg"]
            competitive = scores["competitive_density_avg"]
            share = scores["share_of_voice_avg"]

            # Gap criteria: low share + high buyer intent + manageable competition
            if share < 0.25 and buyer_intent > 0.0 and competitive < 0.5:
                opportunity_score = buyer_intent - (competitive * 0.5)

                if opportunity_score > 0.2:
                    recommended_play = self._generate_recommended_play(
                        space_name, theme_tags, buyer_intent, competitive
                    )

                    gaps.append(PositioningGap(
                        gap_name=description,
                        current_narratives=self._get_current_claimants(theme_tags, current_map),
                        buyer_intent_signal=round(buyer_intent, 3),
                        competitive_presence=round(competitive, 3),
                        recommended_play=recommended_play,
                    ))

        # Sort by opportunity score
        gaps.sort(key=lambda g: g.buyer_intent_signal - g.competitive_presence, reverse=True)
        return gaps

    def _score_narrative_spaces(self, narrative_map: NarrativeMap) -> dict:
        """Score each predefined narrative space against current map."""
        scores = {}

        for space_name, description, theme_tags in self.NARRATIVE_SPACES:
            matching_states = []
            for tag in theme_tags:
                try:
                    theme = NarrativeTheme(tag)
                    state = narrative_map.get_state(theme)
                    if state:
                        matching_states.append(state)
                except ValueError:
                    pass

            if matching_states:
                scores[space_name] = {
                    "buyer_sentiment_avg": sum(s.buyer_sentiment for s in matching_states) / len(matching_states),
                    "competitive_density_avg": sum(s.competitive_density for s in matching_states) / len(matching_states),
                    "share_of_voice_avg": sum(s.share_of_voice for s in matching_states) / len(matching_states),
                }
            else:
                scores[space_name] = {
                    "buyer_sentiment_avg": 0.0,
                    "competitive_density_avg": 0.5,
                    "share_of_voice_avg": 0.0,
                }

        return scores

    def _get_current_claimants(self, theme_tags: list[str],
                               narrative_map: NarrativeMap) -> list[str]:
        """Identify which narratives currently claim this space."""
        claimants = []
        for tag in theme_tags:
            state = narrative_map.get_state(NarrativeTheme(tag))
            if state and state.share_of_voice > 0.15:
                claimants.append(f"{tag} (share: {state.share_of_voice:.1%})")
        return claimants if claimants else ["Unclaimed"]

    def _generate_recommended_play(self, space_name: str,
                                   theme_tags: list[str],
                                   buyer_intent: float,
                                   competitive: float) -> str:
        """Generate a recommended narrative play for a gap."""
        plays = {
            "agent_first_revenue": (
                "Lead with 'Autonomous revenue intelligence' — position as the system that "
                "finds and acts on pipeline opportunities without human steering. "
                "Substantiate with revenue metrics, not productivity metrics."
            ),
            "copilot_outcome_verification": (
                "Lead with 'Outcomes you can verify' — position the copilot as the system "
                "that shows its work and measures impact rigorously. "
                "Counter AI-washed skepticism with transparent benchmarking."
            ),
            "autonomous_integration": (
                "Lead with 'Zero-integration-overhead automation' — position full-auto as "
                "something that actually works with existing stack without 6-month implementations. "
                "Substantiate with time-to-value benchmarks."
            ),
            "trust_auditability": (
                "Lead with 'AI you can audit' — position trust infrastructure as a first-class "
                "capability, not an afterthought. Counter AI-washed by providing model cards "
                "and decision logs."
            ),
            "resistance_handling": (
                "Lead with 'AI that your team will actually adopt' — position as the vendor "
                "that makes AI feel collaborative rather than threatening. "
                "Substantiate with change management metrics."
            ),
        }

        return plays.get(space_name, f"Own the {theme_tags[0]} narrative with concrete proof points.")