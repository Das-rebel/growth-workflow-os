"""
Narrative Analyzer for AI-Native GTM

Analyzes signals for narrative implications and extracts
positioning opportunities and threats from raw market evidence.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable
import re
from datetime import datetime
import json


class SignalSource(str, Enum):
    ANALYST_REPORT = "analyst_report"
    VC_PUBLICATION = "vc_publication"
    COMPETITOR_SITE = "competitor_site"
    CUSTOMER_CALL = "customer_call"
    JOB_POSTING = "job_posting"
    SOCIAL_MENTION = "social_mention"
    EARNINGS_CALL = "earnings_call"
    CONFERENCE_TALK = "conference_talk"


class NarrativeImplication(str, Enum):
    """What the signal implies for narrative strategy."""
    OPPORTUNITY = "opportunity"           # Positive narrative gap
    THREAT = "threat"                      # Competitive narrative threat
    SHIFT = "shift"                       # Market narrative is shifting
    VALIDATION = "validation"             # Existing narrative is validated
    Commoditization = "commoditization"   # Narrative becoming table stakes


@dataclass
class ProcessedSignal:
    """
    A signal that has been analyzed for narrative implications.
    """
    source_type: SignalSource
    raw_text: str
    extracted_claims: list[str]           # Key claims extracted from text
    narrative_implications: list[NarrativeImplication]
    implications_detail: list[str]        # Specific implications
    urgency: str                          # "critical", "major", "minor"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict = field(default_factory=dict)


@dataclass
class PositioningOpportunity:
    """
    An opportunity extracted from signal analysis.
    """
    title: str
    description: str
    confidence: float                     # 0-1
    evidence: list[str]                   # Source texts supporting this
    recommended_positioning: str
    estimated_timing: str                 # "now", "1-2 quarters", "longer"
    competitive_exposure: str             # "low", "medium", "high"


@dataclass
class PositioningThreat:
    """
    A threat extracted from signal analysis.
    """
    title: str
    description: str
    severity: str                         # "critical", "major", "minor"
    evidence: list[str]
    recommended_response: str
    timeline: str                         # "immediate", "near-term", "long-term"


@dataclass
class AnalysisReport:
    """
    Full signal analysis report with opportunities, threats, and recommendations.
    """
    timestamp: str
    signals_analyzed: int
    opportunities: list[PositioningOpportunity]
    threats: list[PositioningThreat]
    recommendations: list[str]
    narrative_health_score: float         # 0-1 overall positioning health


# ---------------------------------------------------------------------------
# Signal Processing Pipeline
# ---------------------------------------------------------------------------

class SignalProcessor:
    """
    Processes raw signals into analyzed implications.
    Each processor handles a specific signal source type.
    """

    def __init__(self):
        self._processors: dict[SignalSource, Callable[[str], ProcessedSignal]] = {
            SignalSource.ANALYST_REPORT: self._process_analyst_report,
            SignalSource.VC_PUBLICATION: self._process_vc_publication,
            SignalSource.COMPETITOR_SITE: self._process_competitor_site,
            SignalSource.CUSTOMER_CALL: self._process_customer_call,
            SignalSource.JOB_POSTING: self._process_job_posting,
            SignalSource.SOCIAL_MENTION: self._process_social,
            SignalSource.EARNINGS_CALL: self._process_earnings_call,
            SignalSource.CONFERENCE_TALK: self._process_conference_talk,
        }

    def process(self, source_type: SignalSource, raw_text: str) -> ProcessedSignal:
        """Process raw text from a given source type into a processed signal."""
        processor = self._processors.get(source_type, self._process_generic)
        return processor(raw_text)

    def _extract_claims(self, text: str) -> list[str]:
        """Extract key claims from raw text using heuristics."""
        claims = []

        # Extract sentences with strong claims
        # Pattern: strong assertion + quantitative or comparative language
        patterns = [
            r"([^.]+?(?:increased|decreased|grew|declined|improved|doubled|tripled)\s+(?:by\s+)?\d+%[^.]+)",
            r"([^.]+?(?:autonomous|AI-native|agentic|copilot)\s+(?:is|are|was|were)[^.]+)",
            r"([^.]*?(?:enterprise|company|team|organization)\s+(?:is|are|was|were)\s+(?:using|adopting|building)[^.]+)",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.I):
                claim = match.group(0).strip()
                if len(claim) > 20 and claim not in claims:
                    claims.append(claim)

        # Also grab short declarative statements
        declarative_pattern = r'\b(?:We|Our|AI|The system)\s+[^.]+\.'
        for match in re.finditer(declarative_pattern, text):
            stmt = match.group(0).strip()
            if len(stmt) > 15 and stmt not in claims:
                claims.append(stmt)

        return claims[:10]  # Cap at 10 claims

    def _detect_implications(self, text: str, claims: list[str]) -> tuple[list[NarrativeImplication], list[str]]:
        """Detect narrative implications from text and claims."""
        implications = []
        details = []

        text_lower = text.lower()
        combined = text_lower + " " + " ".join(claims).lower()

        # Opportunity signals
        if re.search(r'\b(gap|opportunity|unmet|underserved|unaddressed)\b', combined):
            implications.append(NarrativeImplication.OPPORTUNITY)
            details.append("Signal indicates an unmet need or market gap")

        if re.search(r'\b(new|category|creating|defining)\b', combined):
            implications.append(NarrativeImplication.SHIFT)
            details.append("Signal indicates a new category or narrative shift")

        # Threat signals
        if re.search(r'\b(competitive|competition|rivals|disruption)\b', combined):
            implications.append(NarrativeImplication.THREAT)
            details.append("Signal indicates rising competitive pressure")

        if re.search(r'\b(saturation|commodit|table.stakes|everyone.is.doing)\b', combined):
            implications.append(NarrativeImplication.CommoditIZATION)
            details.append("Signal indicates narrative commoditization")

        if re.search(r'\b(proven|validated|validated|customer.success|results)\b', combined):
            implications.append(NarrativeImplication.VALIDATION)
            details.append("Signal validates an existing narrative")

        # Default to shift if no clear implication
        if not implications:
            implications.append(NarrativeImplication.SHIFT)
            details.append("Signal suggests market is evolving")

        # Urgency detection
        urgency = "minor"
        if re.search(r'\b(urgent|critical|immediately|asap|now)\b', combined):
            urgency = "critical"
        elif re.search(r'\b(important|key|significant|major)\b', combined):
            urgency = "major"

        # Store urgency in details
        details.append(f"Urgency: {urgency}")

        return implications, details

    def _process_generic(self, raw_text: str) -> ProcessedSignal:
        """Generic signal processor for unrecognized sources."""
        claims = self._extract_claims(raw_text)
        implications, details = self._detect_implications(raw_text, claims)
        return ProcessedSignal(
            source_type=SignalSource.SOCIAL_MENTION,
            raw_text=raw_text[:500],
            extracted_claims=claims,
            narrative_implications=implications,
            implications_detail=details,
            urgency="minor",
        )

    def _process_analyst_report(self, raw_text: str) -> ProcessedSignal:
        """Process Gartner/Forrester/IDC analyst reports."""
        claims = self._extract_claims(raw_text)
        implications, details = self._detect_implications(raw_text, claims)

        # Analyst reports often validate or shift narratives
        if any(i in [NarrativeImplication.SHIFT, NarrativeImplication.VALIDATION] for i in implications):
            details.append("Analyst report may validate or shift market narrative significantly")

        return ProcessedSignal(
            source_type=SignalSource.ANALYST_REPORT,
            raw_text=raw_text[:500],
            extracted_claims=claims,
            narrative_implications=implications,
            implications_detail=details,
            urgency="major",
            metadata={"report_type": "analyst"},
        )

    def _process_vc_publication(self, raw_text: str) -> ProcessedSignal:
        """Process VC theses, blog posts, and funding announcements."""
        claims = self._extract_claims(raw_text)
        implications, details = self._detect_implications(raw_text, claims)

        # VC publications often indicate category creation or shifts
        if re.search(r'\b(funding|raised|investing|bet|thesis)\b', raw_text.lower()):
            implications.append(NarrativeImplication.SHIFT)
            details.append("VC activity indicates category investment is accelerating")

        return ProcessedSignal(
            source_type=SignalSource.VC_PUBLICATION,
            raw_text=raw_text[:500],
            extracted_claims=claims,
            narrative_implications=implications,
            implications_detail=details,
            urgency="major" if re.search(r'\b(funding|investing|backing)\b', raw_text.lower()) else "minor",
            metadata={"vc_signal": True},
        )

    def _process_competitor_site(self, raw_text: str) -> ProcessedSignal:
        """Process competitor marketing content."""
        claims = self._extract_claims(raw_text)
        implications, details = self._detect_implications(raw_text, claims)

        implications.append(NarrativeImplication.THREAT)
        details.append("Competitor messaging detected - assess positioning threat")

        return ProcessedSignal(
            source_type=SignalSource.COMPETITOR_SITE,
            raw_text=raw_text[:500],
            extracted_claims=claims,
            narrative_implications=implications,
            implications_detail=details,
            urgency="major",
            metadata={"competitive_content": True},
        )

    def _process_customer_call(self, raw_text: str) -> ProcessedSignal:
        """Process customer conversation notes."""
        claims = self._extract_claims(raw_text)
        implications, details = self._detect_implications(raw_text, claims)

        # Customer calls often reveal real pain vs hype
        if re.search(r'\b(frustrat|confus|skeptical|don\'t believe|doubt)\b', raw_text.lower()):
            details.append("Customer skepticism signal detected - validate messaging")

        return ProcessedSignal(
            source_type=SignalSource.CUSTOMER_CALL,
            raw_text=raw_text[:500],
            extracted_claims=claims,
            narrative_implications=implications,
            implications_detail=details,
            urgency="major",
            metadata={"customer_feedback": True},
        )

    def _process_job_posting(self, raw_text: str) -> ProcessedSignal:
        """Process job postings for signal on organizational priorities."""
        claims = self._extract_claims(raw_text)
        implications, details = self._detect_implications(raw_text, claims)

        # Job postings indicate where companies are investing
        if re.search(r'\b(agent|AI engineer|automation|autonomous)\b', raw_text.lower()):
            implications.append(NarrativeImplication.SHIFT)
            details.append("Hiring signal indicates agent/autonomous investment trend")

        return ProcessedSignal(
            source_type=SignalSource.JOB_POSTING,
            raw_text=raw_text[:500],
            extracted_claims=claims,
            narrative_implications=implications,
            implications_detail=details,
            urgency="minor",
            metadata={"hiring_signal": True},
        )

    def _process_social(self, raw_text: str) -> ProcessedSignal:
        """Process social media mentions."""
        claims = self._extract_claims(raw_text)
        implications, details = self._detect_implications(raw_text, claims)

        return ProcessedSignal(
            source_type=SignalSource.SOCIAL_MENTION,
            raw_text=raw_text[:300],
            extracted_claims=claims[:5],  # Fewer claims from social
            narrative_implications=implications,
            implications_detail=details,
            urgency="minor",
        )

    def _process_earnings_call(self, raw_text: str) -> ProcessedSignal:
        """Process earnings call transcripts."""
        claims = self._extract_claims(raw_text)
        implications, details = self._detect_implications(raw_text, claims)

        # Earnings calls indicate strategic narrative at scale
        if re.search(r'\b(AI|agent|automation)\b', raw_text.lower()):
            implications.append(NarrativeImplication.VALIDATION)
            details.append("Enterprise AI narrative validated by public market signals")

        return ProcessedSignal(
            source_type=SignalSource.EARNINGS_CALL,
            raw_text=raw_text[:500],
            extracted_claims=claims,
            narrative_implications=implications,
            implications_detail=details,
            urgency="major",
            metadata={"public_market_signal": True},
        )

    def _process_conference_talk(self, raw_text: str) -> ProcessedSignal:
        """Process conference keynote and talk content."""
        claims = self._extract_claims(raw_text)
        implications, details = self._detect_implications(raw_text, claims)

        # Conference talks often set narrative direction
        if re.search(r'\b(introducing|launching|unveiling|announcing)\b', raw_text.lower()):
            implications.append(NarrativeImplication.SHIFT)
            details.append("Product/narrative launch detected at conference")

        return ProcessedSignal(
            source_type=SignalSource.CONFERENCE_TALK,
            raw_text=raw_text[:500],
            extracted_claims=claims,
            narrative_implications=implications,
            implications_detail=details,
            urgency="major",
            metadata={"conference_signal": True},
        )


# ---------------------------------------------------------------------------
# Narrative Analyzer: Orchestrates signal analysis and report generation
# ---------------------------------------------------------------------------

class NarrativeAnalyzer:
    """
    Main analyzer that:
    1. Ingests raw signals from various sources
    2. Processes them through signal-specific pipelines
    3. Extracts positioning opportunities and threats
    4. Generates an AnalysisReport
    """

    def __init__(self):
        self.processor = SignalProcessor()
        self.processed_signals: list[ProcessedSignal] = []

    def ingest_raw_signal(self, source_type: SignalSource, raw_text: str) -> ProcessedSignal:
        """Ingest and process a raw signal."""
        processed = self.processor.process(source_type, raw_text)
        self.processed_signals.append(processed)
        return processed

    def ingest_bulk(self, signals: list[tuple[SignalSource, str]]) -> list[ProcessedSignal]:
        """Ingest multiple signals at once."""
        results = []
        for source_type, raw_text in signals:
            processed = self.ingest_raw_signal(source_type, raw_text)
            results.append(processed)
        return results

    def extract_opportunities(self) -> list[PositioningOpportunity]:
        """Extract positioning opportunities from processed signals."""
        opportunities = []

        # Group by narrative implication
        opportunity_signals = [
            s for s in self.processed_signals
            if NarrativeImplication.OPPORTUNITY in s.narrative_implications
        ]

        # Also look at shift signals for emerging opportunities
        shift_signals = [
            s for s in self.processed_signals
            if NarrativeImplication.SHIFT in s.narrative_implications
        ]

        for sig in opportunity_signals:
            for claim in sig.extracted_claims:
                if any(kw in claim.lower() for kw in ["gap", "unmet", "need", "demand", "opportunity"]):
                    opportunities.append(PositioningOpportunity(
                        title=f"Market gap: {claim[:80]}",
                        description=claim,
                        confidence=sig.urgency_score() if hasattr(sig, 'urgency_score') else 0.7,
                        evidence=[sig.raw_text],
                        recommended_positioning=self._infer_positioning_from_claim(claim),
                        estimated_timing="now" if sig.urgency == "critical" else "1-2 quarters",
                        competitive_exposure="low",
                    ))

        # From shift signals, extract emerging opportunities
        for sig in shift_signals:
            for claim in sig.extracted_claims:
                if any(kw in claim.lower() for kw in ["new", "emerging", "growing", "adopting", "investing"]):
                    opportunities.append(PositioningOpportunity(
                        title=f"Emerging narrative: {claim[:80]}",
                        description=claim,
                        confidence=0.5,
                        evidence=[sig.raw_text],
                        recommended_positioning=self._infer_positioning_from_claim(claim),
                        estimated_timing="1-2 quarters",
                        competitive_exposure="medium",
                    ))

        # Deduplicate by title
        seen_titles = set()
        deduped = []
        for opp in opportunities:
            if opp.title not in seen_titles:
                seen_titles.add(opp.title)
                deduped.append(opp)

        return deduped

    def extract_threats(self) -> list[PositioningThreat]:
        """Extract positioning threats from processed signals."""
        threats = []

        threat_signals = [
            s for s in self.processed_signals
            if NarrativeImplication.THREAT in s.narrative_implications
        ]

        commoditization_signals = [
            s for s in self.processed_signals
            if NarrativeImplication.CommoditIZATION in s.narrative_implications
        ]

        for sig in threat_signals:
            severity = sig.urgency  # "critical", "major", "minor"

            for claim in sig.extracted_claims:
                threats.append(PositioningThreat(
                    title=f"Competitive threat: {claim[:80]}",
                    description=claim,
                    severity=severity,
                    evidence=[sig.raw_text],
                    recommended_response=self._build_rebuttal_from_claim(claim),
                    timeline="immediate" if severity == "critical" else "near-term",
                ))

        for sig in commoditization_signals:
            for claim in sig.extracted_claims:
                threats.append(PositioningThreat(
                    title=f"Commoditization risk: {claim[:80]}",
                    description=claim,
                    severity="major",
                    evidence=[sig.raw_text],
                    recommended_response="Differentiate with specific outcomes and proof points, not AI branding",
                    timeline="near-term",
                ))

        # Deduplicate
        seen_titles = set()
        deduped = []
        for t in threats:
            if t.title not in seen_titles:
                seen_titles.add(t.title)
                deduped.append(t)

        return deduped

    def generate_report(self) -> AnalysisReport:
        """Generate a full analysis report."""
        opportunities = self.extract_opportunities()
        threats = self.extract_threats()

        # Generate recommendations
        recommendations = self._build_recommendations(opportunities, threats)

        # Compute narrative health score
        health = self._compute_health_score(opportunities, threats)

        return AnalysisReport(
            timestamp=datetime.utcnow().isoformat(),
            signals_analyzed=len(self.processed_signals),
            opportunities=opportunities,
            threats=threats,
            recommendations=recommendations,
            narrative_health_score=health,
        )

    def _infer_positioning_from_claim(self, claim: str) -> str:
        """Infer recommended positioning from a claim."""
        claim_lower = claim.lower()

        if "agent" in claim_lower:
            return "Agent-native positioning: autonomous action framing"
        elif "autonomous" in claim_lower or "automation" in claim_lower:
            return "Autonomous automation framing with outcome verification"
        elif "copilot" in claim_lower or "assistant" in claim_lower:
            return "Copilot amplification framing with productivity metrics"
        elif "revenue" in claim_lower or "sales" in claim_lower:
            return "Revenue-linked outcomes framing"
        else:
            return "Validate with buyer intent research before committing"

    def _build_rebuttal_from_claim(self, claim: str) -> str:
        """Build a recommended rebuttal from a competitive claim."""
        claim_lower = claim.lower()

        rebuttals = {
            "agent": "Differentiate by showing real autonomous outcomes, not just agent branding. Prove with customer case studies.",
            "autonomous": "Counter with trust and auditability — show the autonomous decisions your system makes.",
            "copilot": "Position as amplification of human capability, not replacement. Show productivity multiplier effect.",
            "automation": "Differentiate by outcome measurement — show the business impact, not just task completion.",
        }

        for keyword, rebuttal in rebuttals.items():
            if keyword in claim_lower:
                return rebuttal

        return "Validate claims against independent benchmarks before responding."

    def _build_recommendations(self, opportunities: list[PositioningOpportunity],
                               threats: list[PositioningThreat]) -> list[str]:
        """Build prioritized recommendations from opportunities and threats."""
        recommendations = []

        # Critical opportunities
        critical_opps = [o for o in opportunities if o.estimated_timing == "now"]
        if critical_opps:
            recommendations.append(
                f"IMMEDIATE: Act on {len(critical_opps)} critical opportunities identified. "
                f"Top: {critical_opps[0].title}"
            )

        # Critical threats
        critical_threats = [t for t in threats if t.severity == "critical"]
        if critical_threats:
            recommendations.append(
                f"CRITICAL THREAT: Address {len(critical_threats)} critical threats. "
                f"Top: {critical_threats[0].title}"
            )

        # Near-term opportunities
        near_opps = [o for o in opportunities if o.estimated_timing == "1-2 quarters"]
        if near_opps:
            recommendations.append(
                f"NEAR-TERM: Build positioning for {len(near_opps)} emerging opportunities in next quarter."
            )

        # Narrative health warning
        if len(threats) > len(opportunities) * 2:
            recommendations.append(
                "WARNING: Threats significantly outnumber opportunities. "
                "Consider defensive positioning while seeking new narrative territory."
            )

        if not recommendations:
            recommendations.append("Continue current narrative strategy while monitoring for shifts.")

        return recommendations

    def _compute_health_score(self, opportunities: list[PositioningOpportunity],
                              threats: list[PositioningThreat]) -> float:
        """
        Compute a narrative health score from 0-1.

        Factors:
        - Opportunity count vs threat count (positive = healthy)
        - Signal diversity (more sources = healthier signal base)
        - Urgency balance (critical threats need to be matched by opportunities)
        """
        if not self.processed_signals:
            return 0.0

        # Base score from opportunity/threat ratio
        opp_count = len(opportunities)
        threat_count = len(threats)

        if threat_count == 0:
            ratio_score = min(opp_count / 5, 1.0) * 0.5 + 0.5
        else:
            ratio = opp_count / (opp_count + threat_count)
            ratio_score = ratio * 0.5 + 0.25  # Max 0.75 from ratio

        # Signal diversity bonus
        source_types = set(s.source_type for s in self.processed_signals)
        diversity_score = min(len(source_types) / 5, 1.0) * 0.25  # Max 0.25 from diversity

        # Urgency balance
        critical_threats = sum(1 for t in threats if t.severity == "critical")
        critical_opps = sum(1 for o in opportunities if o.estimated_timing == "now")
        urgency_balance = 0.0
        if critical_threats > 0:
            urgency_balance = min(critical_opps / critical_threats, 1.0) * 0.25

        health = ratio_score + diversity_score + urgency_balance
        return round(min(health, 1.0), 3)


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

def analyze_signals(signals: list[tuple[SignalSource, str]]) -> AnalysisReport:
    """
    Quick analysis of multiple signals.

    Usage:
        signals = [
            (SignalSource.ANALYST_REPORT, "Gartner says agent-first is peaking..."),
            (SignalSource.COMPETITOR_SITE, "Competitor claims autonomous revenue..."),
        ]
        report = analyze_signals(signals)
    """
    analyzer = NarrativeAnalyzer()
    analyzer.ingest_bulk(signals)
    return analyzer.generate_report()


def to_json(report: AnalysisReport) -> str:
    """Serialize an analysis report to JSON."""
    def _serialize_opp(o: PositioningOpportunity) -> dict:
        return {
            "title": o.title,
            "description": o.description,
            "confidence": o.confidence,
            "evidence": o.evidence,
            "recommended_positioning": o.recommended_positioning,
            "estimated_timing": o.estimated_timing,
            "competitive_exposure": o.competitive_exposure,
        }

    def _serialize_threat(t: PositioningThreat) -> dict:
        return {
            "title": t.title,
            "description": t.description,
            "severity": t.severity,
            "evidence": t.evidence,
            "recommended_response": t.recommended_response,
            "timeline": t.timeline,
        }

    return json.dumps({
        "timestamp": report.timestamp,
        "signals_analyzed": report.signals_analyzed,
        "opportunities": [_serialize_opp(o) for o in report.opportunities],
        "threats": [_serialize_threat(t) for t in report.threats],
        "recommendations": report.recommendations,
        "narrative_health_score": report.narrative_health_score,
    }, indent=2)