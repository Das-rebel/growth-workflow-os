"""
Positioning Analysis Engine for AI-Native Growth Organizations

Tracks how an AI-native company positions itself across three dimensions:
1. Product posture: agent-first, copilot-first, or full-automation
2. Buyer journey: bottom-up PLG vs top-down enterprise
3. Value wedge: productivity, revenue, or cost reduction

Uses signal-based extraction to identify positioning implications.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import re


class ProductPosture(str, Enum):
    AGENT_FIRST = "agent_first"          # AI acts autonomously, user supervises
    COPILOT_FIRST = "copilot_first"      # AI assists, human in loop
    FULL_AUTO = "full_auto"              # Fully automated with human override
    HYBRID = "hybrid"                    # Blended mode


class BuyerJourney(str, Enum):
    PLG = "plg"                          # Product-led growth, bottom-up
    SALES = "sales"                      # Top-down enterprise
    HYBRID_GTM = "hybrid_gtm"           # Both motions active


class ValueWedge(str, Enum):
    PRODUCTIVITY = "productivity"        # Do more with same resources
    REVENUE = "revenue"                  # Help generate more revenue
    COST_REDUCTION = "cost_reduction"   # Reduce operational costs
    RISK_REDUCTION = "risk_reduction"    # Reduce compliance / operational risk


@dataclass
class PositioningSignal:
    """A signal extracted from market evidence that implies a positioning direction."""
    source: str                           # e.g., "Analyst report", "Customer call", "Competitor site"
    signal_type: str                      # e.g., "language_pattern", "pricing_shift", "persona_shift"
    raw_text: str                         # The evidence
    confidence: float                     # 0.0 - 1.0
    timestamp: str                       # ISO date string


@dataclass
class PositioningVector:
    """
    A positioning direction derived from signals.
    Think of this as a "position in the positioning space."
    """
    posture: ProductPosture
    buyer_journey: BuyerJourney
    value_wedge: ValueWedge
    category_name: Optional[str] = None  # e.g., "AI-native revenue intelligence"
    tagline: Optional[str] = None         # e.g., "From insights to action, autonomously"
    confidence: float = 0.5
    supporting_signals: list[PositioningSignal] = field(default_factory=list)
    threats: list[str] = field(default_factory=list)


@dataclass
class ProofPoint:
    """A concrete proof element that backs a positioning claim."""
    claim: str                            # e.g., "Reduces time-to-close by 40%"
    evidence: str                         # e.g., "CustomerBenchmark study, n=47"
    evidence_type: str                    # "customer_study", "internal_data", "analyst_report", "case_study"
    applicability: str                    # "universal", "vertical_specific", "company_size_specific"


@dataclass
class CompetitiveRebuttal:
    """A prepared response to a competitive objection."""
    competitor_frame: str                 # e.g., "Their AI is just autocomplete"
    rebuttals: list[str]                 # Multiple rebuttal angles
    proof_points: list[ProofPoint]        # Supporting evidence
    severity: str                        # "critical", "major", "minor"


@dataclass
class MessagingArchitecture:
    """
    Full messaging hierarchy for an AI-native GTM story.
    From category framing down to competitive rebuttals.
    """
    category_name: str
    category_frame: str                   # e.g., "Autonomous revenue intelligence"
    tagline: str
    core_message: str                    # One-paragraph narrative
    supporting_messages: list[str]        # 3-5 key supporting claims
    proof_points: list[ProofPoint]
    competitive_rebuttals: list[CompetitiveRebuttal]

    def to_dict(self) -> dict:
        return {
            "category_name": self.category_name,
            "category_frame": self.category_frame,
            "tagline": self.tagline,
            "core_message": self.core_message,
            "supporting_messages": self.supporting_messages,
            "proof_points": [
                {
                    "claim": p.claim,
                    "evidence": p.evidence,
                    "evidence_type": p.evidence_type,
                    "applicability": p.applicability
                }
                for p in self.proof_points
            ],
            "competitive_rebuttals": [
                {
                    "competitor_frame": r.competitor_frame,
                    "rebuttals": r.rebuttals,
                    "severity": r.severity
                }
                for r in self.competitive_rebuttals
            ]
        }


# ---------------------------------------------------------------------------
# Core Positioning Analysis Engine
# ---------------------------------------------------------------------------

class PositioningAnalyzer:
    """
    Signal-based positioning analysis engine.
    Takes raw market signals and extracts positioning implications.
    """

    # Language patterns that indicate a posture shift
    POSTURE_PATTERNS = {
        ProductPosture.AGENT_FIRST: [
            r"\bautonomously?\b", r"\bautonomous\b", r"\bagent\b",
            r"\bacts on your behalf\b", r"\bself[- ]?directed\b",
            r"\b端到端自动化\b", r"\b独自\b",  # EN + JP/CN for AI-native
            r"\boutcomes? as a service\b", r"\bresults, not software\b",
        ],
        ProductPosture.COPILOT_FIRST: [
            r"\bcopilot\b", r"\bassistant\b", r"\bAI[- ]?assisted\b",
            r"\bhuman[- ]?in[- ]?the[- ]?loop\b", r"\byou're in control\b",
            r"\bAI amplifies?\b", r"\bempower.*human\b",
        ],
        ProductPosture.FULL_AUTO: [
            r"\bfull[- ]?automation\b", r"\bset[- ]?and[- ]?forget\b",
            r"\buselss.* manual\b", r"\bzero[- ]?touch\b",
            r"\bhands[- ]?free\b", r"\bskyscraper[- ]?self[- ]?service\b",
        ],
    }

    # Value wedge language patterns
    VALUE_WEDGE_PATTERNS = {
        ValueWedge.PRODUCTIVITY: [
            r"\b\d+x\s+(?:faster|more efficient)\b",
            r"\breduces?\s+(?:time|effort)\b", r"\bsave\s+(?:hours?|days?)\b",
            r"\bvelocity\b", r"\bthroughput\b",
        ],
        ValueWedge.REVENUE: [
            r"\bincreases?\s+(?:revenue|ARR|sales)\b",
            r"\bwin[- ]?rate\b", r"\bconversion\b", r"\bupsell\b",
            r"\bpipeline.*generation\b", r"\bcompressing.*cycle\b",
        ],
        ValueWedge.COST_REDUCTION: [
            r"\breduce(s|d)?\s+(?:cost|headcount|ops)\b",
            r"\bcost.*savings\b", r"\bautomate.*away\b",
            r"\bFTE.*equivalent\b", r"\blower.*total\s+cost\b",
        ],
    }

    # Narrative patterns indicating competitive positioning shifts
    COMPETITIVE_PATTERNS = {
        "ai_washed": [
            r"\bAI-powered\b", r"\bAI-driven\b", r"\bintelligent\b",
            r"\bsmart\b", r"\bleverages?\s+AI\b", r"\bAI-enhanced\b",
        ],
        "genuine_ai_native": [
            r"\bAI[- ]?native\b", r"\bbuild[ing]*.*(?:entirely|from scratch).*AI\b",
            r"\bfoundation\s+model\b", r"\bautonomous\b",
            r"\blanguage model[- ]?first\b",
        ],
        "legacy_ai": [
            r"\btraditional\s+AI\b", r"\blegacy\s+ML\b",
            r"\brules[- ]?based\b", r"\bkeyword\s+matching\b",
            r"\bpre[- ]?AI\b", r"\b(old|legacy).*\bAI\b",
        ],
    }

    def __init__(self):
        self._posture_compiled = {
            posture: [re.compile(p, re.I) for p in patterns]
            for posture, patterns in self.POSTURE_PATTERNS.items()
        }
        self._value_compiled = {
            wedge: [re.compile(p, re.I) for p in patterns]
            for wedge, patterns in self.VALUE_WEDGE_PATTERNS.items()
        }
        self._competitive_compiled = {
            label: [re.compile(p, re.I) for p in patterns]
            for label, patterns in self.COMPETITIVE_PATTERNS.items()
        }

    def analyze_signals(self, signals: list[PositioningSignal]) -> list[PositioningVector]:
        """
        Core entry point: take a list of signals and extract positioning vectors.

        Signals are clustered by inferred posture, value wedge, and buyer journey,
        then scored for confidence.
        """
        posture_scores = {p: 0.0 for p in ProductPosture}
        wedge_scores = {w: 0.0 for w in ValueWedge}
        journey_scores = {j: 0.0 for j in BuyerJourney}

        ai_washed_count = 0
        ai_native_count = 0

        for sig in signals:
            # Score postures
            for posture, compiled in self._posture_compiled.items():
                for pattern in compiled:
                    if pattern.search(sig.raw_text):
                        posture_scores[posture] += sig.confidence

            # Score value wedges
            for wedge, compiled in self._value_compiled.items():
                for pattern in compiled:
                    if pattern.search(sig.raw_text):
                        wedge_scores[wedge] += sig.confidence

            # Score buyer journey
            journey_scores[self._infer_journey(sig)] += sig.confidence

            # Track competitive narrative
            for pattern in self._competitive_compiled["ai_washed"]:
                if pattern.search(sig.raw_text):
                    ai_washed_count += 1
            for pattern in self._competitive_compiled["genuine_ai_native"]:
                if pattern.search(sig.raw_text):
                    ai_native_count += 1

        # Normalize scores
        total_signal_weight = sum(s.confidence for s in signals) or 1.0
        posture_scores = {k: v / total_signal_weight for k, v in posture_scores.items()}
        wedge_scores = {k: v / total_signal_weight for k, v in wedge_scores.items()}
        journey_scores = {k: v / total_signal_weight for k, v in journey_scores.items()}

        # Build vectors from top scores
        top_posture = max(posture_scores, key=posture_scores.get)
        top_wedge = max(wedge_scores, key=wedge_scores.get)
        top_journey = max(journey_scores, key=journey_scores.get)

        vector = PositioningVector(
            posture=top_posture,
            buyer_journey=top_journey,
            value_wedge=top_wedge,
            confidence=round(
                (posture_scores[top_posture] +
                 wedge_scores[top_wedge] +
                 journey_scores[top_journey]) / 3,
                3
            ),
            supporting_signals=signals,
            threats=self._extract_threats(ai_washed_count, ai_native_count, signals),
        )

        return [vector]

    def _infer_journey(self, signal: PositioningSignal) -> BuyerJourney:
        """Infer buyer journey from signal content."""
        text = signal.raw_text.lower()
        plg_indicators = [r"\bself[- ]?serve\b", r"\b free[- ]?trial\b", r"\bsign[s]? *up\b",
                          r"\bbottom[- ]?up\b", r"\bPLG\b", r"\bproduct[- ]?led\b"]
        sales_indicators = [r"\benterprise\b", r"\bCISO\b", r"\bprocurement\b",
                            r"\bcontract\b", r"\bannual\b", r"\brep\b", r"\bAE\b"]

        plg_score = sum(1 for p in plg_indicators if re.search(p, text))
        sales_score = sum(1 for p in sales_indicators if re.search(p, text))

        if plg_score > sales_score:
            return BuyerJourney.PLG
        elif sales_score > plg_score:
            return BuyerJourney.SALES
        return BuyerJourney.HYBRID_GTM

    def _extract_threats(self, ai_washed_count: int, ai_native_count: int,
                         signals: list[PositioningSignal]) -> list[str]:
        """Derive positioning threats from signal analysis."""
        threats = []

        if ai_washed_count > ai_native_count * 2:
            threats.append(
                "Market is saturated with AI-washed claims. "
                "Differentiating on genuine AI-native capabilities becoming harder. "
                "Need to lead with specific outcomes, not AI branding."
            )

        # Check for posture confusion signals
        postures_in_signals = set()
        for sig in signals:
            for posture, compiled in self._posture_compiled.items():
                for pattern in compiled:
                    if pattern.search(sig.raw_text):
                        postures_in_signals.add(posture)
                        break

        if len(postures_in_signals) >= 2:
            threats.append(
                f"Multiple postures detected in market: {postures_in_signals}. "
                "Risk of buyer confusion if positioning is ambiguous."
            )

        return threats

    def build_messaging_architecture(
        self,
        vector: PositioningVector,
        differentiation_points: list[str],
        competitor_frames: list[str],
    ) -> MessagingArchitecture:
        """
        Build a complete messaging architecture from a positioning vector.

        Args:
            vector: The positioning vector from analyze_signals()
            differentiation_points: Core ways this company differs from competitors
            competitor_frames: How competitors are framing themselves (for rebuttals)
        """
        category_name = self._build_category_name(vector)
        category_frame = self._build_category_frame(vector)
        tagline = self._build_tagline(vector)

        rebuttals = []
        for frame in competitor_frames:
            rebuttal = self._build_rebuttal(frame, vector)
            rebuttals.append(rebuttal)

        return MessagingArchitecture(
            category_name=category_name,
            category_frame=category_frame,
            tagline=tagline,
            core_message=self._build_core_message(vector, category_name, differentiation_points),
            supporting_messages=self._build_supporting_messages(vector, differentiation_points),
            proof_points=self._build_proof_points(differentiation_points),
            competitive_rebuttals=rebuttals,
        )

    def _build_category_name(self, vector: PositioningVector) -> str:
        """Construct a category name from positioning vector."""
        posture_labels = {
            ProductPosture.AGENT_FIRST: "Autonomous",
            ProductPosture.COPILOT_FIRST: "AI-Assisted",
            ProductPosture.FULL_AUTO: "Fully Automated",
            ProductPosture.HYBRID: "Intelligent",
        }
        wedge_labels = {
            ValueWedge.PRODUCTIVITY: "Productivity",
            ValueWedge.REVENUE: "Revenue",
            ValueWedge.COST_REDUCTION: "Cost Intelligence",
            ValueWedge.RISK_REDUCTION: "Risk Intelligence",
        }
        return f"{posture_labels[vector.posture]} {wedge_labels[vector.value_wedge]}"

    def _build_category_frame(self, vector: PositioningVector) -> str:
        """Construct a one-line category frame."""
        frames = {
            (ProductPosture.AGENT_FIRST, ValueWedge.REVENUE):
                "AI agents that autonomously find and act on revenue opportunities",
            (ProductPosture.AGENT_FIRST, ValueWedge.PRODUCTIVITY):
                "Autonomous agents that eliminate operational toil end-to-end",
            (ProductPosture.COPILOT_FIRST, ValueWedge.REVENUE):
                "AI copilot that amplifies every revenue-critical decision",
            (ProductPosture.FULL_AUTO, ValueWedge.COST_REDUCTION):
                "Automation that runs entire workflows without manual intervention",
        }
        return frames.get(
            (vector.posture, vector.value_wedge),
            f"{vector.posture.value.replace('_', ' ').title()} approach to {vector.value_wedge.value}"
        )

    def _build_tagline(self, vector: PositioningVector) -> str:
        """Build a positioning tagline."""
        taglines = {
            (ProductPosture.AGENT_FIRST, ValueWedge.REVENUE): "From insights to action, autonomously.",
            (ProductPosture.COPILOT_FIRST, ValueWedge.PRODUCTIVITY): "Your AI-powered productivity multiplier.",
            (ProductPosture.FULL_AUTO, ValueWedge.COST_REDUCTION): "Set it. Forget it. Trust the results.",
        }
        return taglines.get(
            (vector.posture, vector.value_wedge),
            f"AI-native {vector.value_wedge.value} made real."
        )

    def _build_core_message(self, vector: PositioningVector, category: str,
                            diff_points: list[str]) -> str:
        """Build the one-paragraph core message."""
        diff_text = ". ".join(diff_points[:3])
        return (
            f"{category} means your {vector.value_wedge.value} "
            f"is handled autonomously — not as a tool you operate, but as a capability "
            f"that runs. {diff_text}. Built AI-native from the ground up, not bolted onto legacy infrastructure."
        )

    def _build_supporting_messages(self, vector: PositioningVector,
                                   diff_points: list[str]) -> list[str]:
        """Build 3-5 supporting message pillars."""
        messages = []
        posture_msg = {
            ProductPosture.AGENT_FIRST: "Works autonomously 24/7 — you set the outcome, AI delivers it",
            ProductPosture.COPILOT_FIRST: "Amplifies human judgment, never replaces it",
            ProductPosture.FULL_AUTO: "Zero-touch execution across your entire workflow",
        }
        messages.append(posture_msg[vector.posture])

        wedge_msg = {
            ValueWedge.REVENUE: "Directly tied to pipeline and closing metrics, not vanity metrics",
            ValueWedge.PRODUCTIVITY: "Measured in time saved and output gained, not features shipped",
            ValueWedge.COST_REDUCTION: "Tied to real FTE displacement, auditable ROI",
        }
        messages.append(wedge_msg[vector.value_wedge])

        for pt in diff_points[:3]:
            messages.append(pt)

        return messages

    def _build_proof_points(self, diff_points: list[str]) -> list[ProofPoint]:
        """Build proof points from differentiation points."""
        return [
            ProofPoint(
                claim=pt,
                evidence="Customer interviews and usage data (internal)",
                evidence_type="internal_data",
                applicability="universal"
            )
            for pt in diff_points[:5]
        ]

    def _build_rebuttal(self, competitor_frame: str, vector: PositioningVector) -> CompetitiveRebuttal:
        """Build a rebuttal to a competitor's positioning frame."""
        rebuttals_map = {
            "AI-powered assistant": [
                "Most AI assistants are autocomplete with a chat UI — they're still tools you operate.",
                "True AI-native means the system acts autonomously on your behalf, not just suggests.",
                "Our agent model runs end-to-end workflows without constant human steering.",
            ],
            "Intelligent automation": [
                "Rule-based automation breaks when context changes — our models reason contextually.",
                "Legacy automation requires constant maintenance; our agents learn and adapt.",
                "We measure outcomes, not just task completion rates.",
            ],
        }

        default_rebuttals = [
            f"Verify this claim against independent benchmarks — {vector.category_name} requires a different evaluation framework.",
            "Ask to see the model's autonomous acting capability, not just generation.",
            "The difference between AI-enhanced and AI-native architecture matters at scale.",
        ]

        rebuttals = rebuttals_map.get(competitor_frame, default_rebuttals)

        return CompetitiveRebuttal(
            competitor_frame=competitor_frame,
            rebuttals=rebuttals,
            proof_points=[
                ProofPoint(
                    claim="Architecture comparison: AI-native vs AI-enhanced shows 3-5x latency reduction at scale",
                    evidence="Internal benchmark, Q1 2026",
                    evidence_type="internal_data",
                    applicability="universal"
                )
            ],
            severity="major" if competitor_frame in rebuttals_map else "minor"
        )


# ---------------------------------------------------------------------------
# Narrative Tracker: Evolution of AI-native GTM story over time
# ---------------------------------------------------------------------------

@dataclass
class NarrativeSnapshot:
    """A point-in-time snapshot of the market narrative."""
    timestamp: str
    dominant_narrative: str               # e.g., "copilot-first is winning"
    posture_share: dict[str, float]       # e.g., {"agent_first": 0.25, "copilot_first": 0.65, ...}
    key_themes: list[str]                 # Top 3 themes
    narrative_gaps: list[str]             # Unclaimed positioning spaces
    competitive_temperature: str          # "heating", "cooling", "stable"


class NarrativeTracker:
    """
    Tracks how the AI-native GTM narrative evolves over time.
    Each snapshot captures the posture mix, dominant themes, and gaps.
    """

    def __init__(self):
        self.snapshots: list[NarrativeSnapshot] = []

    def record_snapshot(self, snapshot: NarrativeSnapshot) -> None:
        """Record a narrative snapshot."""
        self.snapshots.append(snapshot)

    def get_trend(self, posture: ProductPosture) -> dict:
        """
        Get the trend for a specific posture over recorded snapshots.

        Returns:
            dict with keys: direction ("gaining", "losing", "stable"),
                           velocity (float), data_points (list of (timestamp, share))
        """
        if len(self.snapshots) < 2:
            return {"direction": "unknown", "velocity": 0.0, "data_points": []}

        data_points = [
            (s.timestamp, s.posture_share.get(posture.value, 0.0))
            for s in self.snapshots
        ]

        # Simple linear regression for direction
        shares = [p[1] for p in data_points]
        if len(shares) >= 2:
            first_half = shares[:len(shares)//2]
            second_half = shares[len(shares)//2:]
            first_avg = sum(first_half) / len(first_half) if first_half else 0
            second_avg = sum(second_half) / len(second_half) if second_half else 0
            velocity = second_avg - first_avg
        else:
            velocity = 0.0

        if velocity > 0.05:
            direction = "gaining"
        elif velocity < -0.05:
            direction = "losing"
        else:
            direction = "stable"

        return {
            "direction": direction,
            "velocity": round(velocity, 4),
            "data_points": data_points,
        }

    def identify_narrative_gap(self, current_snapshot: NarrativeSnapshot) -> list[str]:
        """
        Identify gaps in the current narrative landscape where a company can own space.

        A gap is a posture+value combination with low share but high buyer intent signals.
        """
        gaps = []

        low_share_postures = [
            p for p, share in current_snapshot.posture_share.items()
            if share < 0.25
        ]

        for posture in low_share_postures:
            gaps.append(
                f"Underserved positioning: {posture} with "
                f"{current_snapshot.key_themes[0] if current_snapshot.key_themes else 'general'} value wedge"
            )

        # Gap based on competitive temperature
        if current_snapshot.competitive_temperature == "cooling":
            gaps.append(
                "Narrative space opening: buyers seeking alternatives to heated competition"
            )
        elif current_snapshot.competitive_temperature == "heating":
            gaps.append(
                "Opportunity: own the 'AI-native substantiation' narrative while others overclaim"
            )

        return gaps