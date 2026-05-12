"""Organizational design patterns for AI-native growth teams.

Growth workflow improved: Team structure and decision rights for AI-assisted growth operations.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OrgPattern:
    """Definition of an organizational design pattern for growth teams."""

    name: str
    aliases: list[str]
    description: str
    when_to_use: str
    team_structure: str
    decision_rights: str
    coordination_topology: str
    hiring_implications: list[str]
    automation_ceiling: float
    examples: list[str]
    risk: str


ORG_PATTERNS: dict[str, OrgPattern] = {

    "agent_first_gtm": OrgPattern(
        name="Agent-First GTM",
        aliases=["ai-native sales", "agent-led outbound"],
        description="AI agents handle initial outreach, qualification, and follow-up. Human sales team focuses exclusively on demo, negotiation, and close. Agents are first contact, humans are closers.",
        when_to_use="High-volume outbound motion, product-led growth, SMB segment. When reply rates from human SDRs are below 5%.",
        team_structure="Large agent fleet + small closing team. 1 AE per 10-15 agents. No traditional SDR role. Prompt engineers / agent trainers as first-class function.",
        decision_rights="Agents decide: qualify/disqualify, outreach sequence, follow-up timing. Humans decide: pricing, contract terms, demo approach. Escalation triggers at disqualified_threshold or deal_size_above_threshold.",
        coordination_topology="星形 / hub-spoke: agents radiate outward to prospects, hub is the AE who receives qualified leads. Coordination via shared lead queue, not sequential handoffs.",
        hiring_implications=["Agent prompt engineer / trainer (critical hire)", "AI-literate closing AEs (can optimize agent outputs)", "No traditional SDR/BDR needed", "Operations person to monitor agent fleet health"],
        automation_ceiling=0.75,
        examples=["Regie.ai", "11x.ai", "Clay Integration ecosystem"],
        risk="Brand risk if agents send poor quality outreach. Requires constant prompt refinement.",
    ),

    "ai_augmented_cs": OrgPattern(
        name="AI-Augmented Customer Success",
        aliases=["agent-native CS", "QBee pattern"],
        description="AI agents handle 70%+ of routine CS interactions. Human CSMs manage escalations, own relationships with enterprise accounts, and handle complex renewals. CS becomes a strategic retention function, not reactive support.",
        when_to_use="Scale-up phase where CS headcount is bottlenecking growth. NRR below 110% due to reactive support. Product has high touch but predictable issue patterns.",
        team_structure="1 CSM per 200-300 accounts (vs traditional 1 per 50-100). CS agents handle tier 1-2. CSM role shifts to relationship owner and escalation handler.",
        decision_rights="Agents decide: routine issue resolution, onboarding workflow triggers, churn risk flagging, health score calculation. Humans decide: renewal terms, escalation acceptance, product exception requests.",
        coordination_topology="扁平 / flat: agents operate in parallel across all accounts. CSM acts as exception handler, not coordinator. No formal escalation chain, just priority queue.",
        hiring_implications=["AI CS agent trainer (critical)", "CSMs with enterprise relationship skills, not technical troubleshooting", "Data analyst to monitor agent performance and CS metrics", "Shift hiring budget from tier-1 support to agent engineering"],
        automation_ceiling=0.80,
        examples=["QBee (SaaStr case study)", "Forethought.ai", "Intercom Fin"],
        risk="Enterprise customers may resist agent-only interactions. Requires human-in-the-loop for high-value accounts.",
    ),

    "full_autonomous_revenue": OrgPattern(
        name="Full Autonomous Revenue",
        aliases=["agent-owned revenue", "lights out sales"],
        description="AI agents own entire revenue motion from awareness to close for certain product lines. No human in the loop for deals under threshold. Humans only involved for enterprise or complex sales.",
        when_to_use="Products with clear ROI, short cycle (< 30 days), self-serve onboarding. When product-led growth is primary motion. When human sales cost > 20% of ACV.",
        team_structure="Zero traditional sales org. Agent fleet owns full lifecycle. Small team of 'revenue architects' who design agent behavior, not execute it. Exception team handles human-required deals.",
        decision_rights="Agents own: prospection → qualification → demo scheduling → proposal generation → pricing (within bounds) → close. Humans own: contracts above threshold, custom pricing, executive sponsorship.",
        coordination_topology="Autonomous agents with shared CRM state. No sequential handoff, all parallel execution. Humans observe via dashboards and intervene only on exceptions.",
        hiring_implications=["Revenue architect (designs agent playbooks)", "Agent prompt / behavior engineer", "Revenue operations for AI-fleet monitoring", "No traditional SDR, AE, or sales engineer roles"],
        automation_ceiling=0.90,
        examples=["Drift's early agent experiments", "AutoGPT sales demos (not production-ready)"],
        risk="May violate enterprise procurement policies that require human sales contact. Regulatory risk in some industries.",
    ),

    "ai_hybrid_product": OrgPattern(
        name="AI-Hybrid Product Teams",
        aliases=["agent-augmented product", "ai-native product squads"],
        description="Product teams have AI agents as first-class members. Agents handle user research synthesis, spec drafting, release notes, analytics reporting. Humans focus on strategy and ambiguous problem solving.",
        when_to_use="Product org scaling past 20 people. When PMs are drowning in coordination work. When user research data is underutilized.",
        team_structure="PM + designer + 2-3 engineers + 1 AI agent per squad. Agent has access to analytics, user research DB, specs. Agent participates in standups via async updates.",
        decision_rights="Agents decide: release note content, user research synthesis, analytics dashboards, spec drafting (first pass). Humans decide: prioritization, roadmap, go/no-go, major design decisions.",
        coordination_topology="Squad-based with agents as async participants. No agent representation in standup, but agent outputs flow into all discussions.",
        hiring_implications=["PMs who can effectively delegate to and critique AI outputs", "No change to engineering or design roles, but they interact with agent outputs", "Optional: AI product manager / prompt specialist role"],
        automation_ceiling=0.55,
        examples=["Notion AI features", "Linear's AI roadmap"],
        risk="Agent outputs may have subtle errors that go unnoticed. Risk of over-reliance on AI-generated user insights.",
    ),

    "hub_and_spoke_ops": OrgPattern(
        name="Hub-and-Spoke Operations",
        aliases=["ops hub model", "centralized ai ops"],
        description="Central AI ops team (hub) provides agent capabilities to all revenue teams (spokes). Each revenue function (sales, CS, marketing) has agents customized for their workflow but shares underlying infrastructure.",
        when_to_use="Mid-market companies with multiple revenue functions. When individual teams are each building their own agents (duplication). When AI ops capability should be centralized but execution is distributed.",
        team_structure="Central AI ops team (2-4 people) owns agent infrastructure, prompt libraries, and agent evaluation. Revenue teams (sales, CS, marketing) have agent liaisons who customize agents for their domain.",
        decision_rights="Hub decides: agent infrastructure, shared prompt libraries, evaluation metrics, integration standards. Spokes decide: domain-specific prompts, workflow customization, prioritization. Conflict resolution via AI ops lead.",
        coordination_topology="Hub-and-spoke: hub provides shared resources, spokes consume and customize. Regular syncs between hub and spokes to share prompt improvements.",
        hiring_implications=["AI ops lead (central, critical hire)", "Agent liaison in each revenue team (not dedicated, added to existing role)", "Shared agent engineering resource across teams"],
        automation_ceiling=0.70,
        examples=["HubSpot's AI platform team", "Salesforce's Einstein team"],
        risk="Hub can become bottleneck if central team is understaffed. Risk of inconsistent agent quality across spokes.",
    ),

    "flat_agent_collective": OrgPattern(
        name="Flat Agent Collective",
        aliases=["autonomous agent teams", "minimal hierarchy"],
        description="Many autonomous AI agents operate in parallel with minimal human oversight. Humans are orchestrators who set objectives, not managers who approve decisions. Flat hierarchy where agents coordinate peer-to-peer.",
        when_to_use="Early-stage startups where velocity is critical. When founder has clear vision that agents can execute against. When traditional management structure would slow execution.",
        team_structure="1-2 founders + agent fleet. No middle management. Agents assigned to domains (prospecting, CS, analytics) with clear objectives. Humans monitor outputs and redirect objectives, not tasks.",
        decision_rights="Agents decide: execution within assigned objective. Humans decide: objectives, strategy, priority. Agent-to-agent coordination via shared state, no human approval needed between agents.",
        coordination_topology="Flat peer network. No hierarchical coordination. Shared task board where agents self-assign. Human sets priorities, agents execute.",
        hiring_implications=["Founder who can set clear agent objectives (critical)", "No traditional roles — mostly contractors or agencies for non-core functions", "Agent fleet manager (1 person manages multiple agent domains)"],
        automation_ceiling=0.85,
        examples=["Early experiments by small startups, not widely documented as successes"],
        risk="High risk of misalignment if founder's objectives aren't clear. No safety net if agents make poor decisions. Most successful at seed stage, breaks down at Series A.",
    ),

    "human_in_the_loop_enterprise": OrgPattern(
        name="Human-in-the-Loop Enterprise",
        aliases=["enterprise ai hybrid", "ai-assisted enterprise"],
        description="AI agents assist human decision-makers but never replace them for significant decisions. Agents handle data gathering, analysis, and option generation. Humans make final decisions and own the relationship.",
        when_to_use="Enterprise sales cycles > 6 months. Complex procurement. Relationship-driven sales where human connection is the moat. Highly regulated industries.",
        team_structure="Traditional SDR/AE/BDR structure preserved but augmented by AI agents. Each human has an AI agent assistant. Agents do research, drafting, scheduling. Humans do talking, negotiating, relationship building.",
        decision_rights="Agents decide: research synthesis, email drafting, meeting scheduling, CRM updates. Humans decide: all significant decisions — pricing, contract terms, relationship direction. No autonomous agent decisions above small threshold.",
        coordination_topology="Human-centric with AI as amplifier. Sequential handoff: agent prepares → human reviews → human executes → agent follows up.",
        hiring_implications=["AE who uses AI as force multiplier, not replacement", "SDR who leverages agents for research and personalization", "No elimination of traditional roles, but redefined as AI-augmented"],
        automation_ceiling=0.45,
        examples=["Most enterprise SaaS companies in 2025-2026 transition state"],
        risk="Slowest to achieve AI efficiency gains. Competitors using full autonomy may move faster. Risk of 'AI washing' — humans doing all the work and calling it AI-augmented.",
    ),

    "outcome_based_ops": OrgPattern(
        name="Outcome-Based Operations",
        aliases=["ai roi ops", "outcome-driven org"],
        description="Org structure defined by outcomes, not functions. AI agents are assigned to outcome targets (e.g., reduce churn by 15%) not task lists. Teams are outcome teams, not department teams. Compensation tied to outcome metrics.",
        when_to_use="Companies with clear outcome metrics. When siloed functional org is causing coordination overhead. When AI capabilities are mature enough to own end-to-end outcomes.",
        team_structure="Cross-functional outcome teams (3-7 people) with AI agent capabilities embedded. Each team has: outcome owner, AI agent(s), supporting humans. No traditional departments — only outcome squads.",
        decision_rights="Outcome team decides: how to achieve target within bounds. AI agents decide: within-task execution, data-driven micro-decisions. No centralized decision making — teams own their outcomes.",
        coordination_topology="Flat outcome squads coordinating via shared OKR system. Cross-squad coordination only when outcomes conflict. AI agents provide transparency into each team's progress.",
        hiring_implications=["Outcome owners who can decompose targets into AI-executable plans", "AI agent specialists embedded in each outcome team", "OKR system owner to manage cross-team alignment"],
        automation_ceiling=0.65,
        examples=["Most progressive SaaS companies experimenting with OKR-based AI teams"],
        risk="Outcome metrics can be gamed. Risk of narrow optimization. Requires mature OKR culture to work.",
    ),

    "ai_embedded_lending_ops": OrgPattern(
        name="AI-Native Embedded Lending Operations",
        aliases=["partner ops automation", "embedded lending ai", "nbfc partner ai"],
        description="Partner onboarding and activation automated via AI agents — reduces 50% onboarding time (NIRO playbook). AI handles KYC routing, eligibility pre-check, partner dashboard updates, and disbursement reconciliation. Human ops team focuses on exception handling and partner relationship escalation.",
        when_to_use="NBFCs and fintech with D2C embedded lending products. When partner onboarding is a bottleneck for ToFu. When 30%+ of ops time goes to manual KYC verification and partner status tracking.",
        team_structure="1 partner ops lead + AI agent fleet (KYC router, eligibility checker, disbursement reconciliation). 1 ops human per 20 partners vs traditional 1 per 5. Escalations go to human only for exceptions beyond defined rules.",
        decision_rights="Agents decide: KYC routing, eligibility pre-check triggers, disbursement timing, partner status updates. Humans decide: new partner contract terms, exception overrides, credit policy changes.",
        coordination_topology="Parallel agent execution per partner — no sequential queues. Human ops acts as exception handler layer above agents. Coordination via shared partner state DB.",
        hiring_implications=["Partner AI ops engineer (configures and monitors AI agent fleet)", "Reduce pure KYC verification headcount — shift to exception handling roles", "Add partner success manager for relationship overlay on AI ops"],
        automation_ceiling=0.78,
        examples=["NIRO: reduced partner onboarding 50% via cross-functional redesign (internal)", "Groww partner dashboard (internal reference)"],
        risk="KYC errors in thin-file users (NIRO lesson: <50ms approval causes +40% loss). Must have 120-150ms latency floor. Risk of partner non-compliance if AI routing not monitored.",
    ),

    "vernacular_ai_growth": OrgPattern(
        name="Vernacular-First AI Growth Stack",
        aliases=["whatsapp ai", "regional language ai", "vernacular gtm"],
        description="WhatsApp + voice AI in Hindi/Bengali/Hinglish for tier-2/3 customer acquisition and retention. LLM routing handles regional language variation without separate model per language. Fallback to English for tier-1.",
        when_to_use="Expanding to tier-2/3 India. When English-only digital channels are hitting CAC ceiling. When vernacular speakers represent >40% of target market but <15% of current users.",
        team_structure="Growth ops + AI agent (WhatsApp flow orchestrator) + voice AI integration. 1 vernacular content specialist to train agent tone for regional variation. No separate language team needed.",
        decision_rights="Agents decide: language routing, message template selection by segment, follow-up timing. Humans decide: campaign-level targeting, budget allocation, brand voice guardrails.",
        coordination_topology="LLM routes between Hindi/Hinglish/English without pre-classification. Voice AI handles audio. Human ops monitors and adjusts routing rules weekly.",
        hiring_implications=["Vernacular content/copy specialist (1-2 for Hindi + regional)", "Shift budget from English performance marketing to vernacular WhatsApp/audio", "No dedicated regional language engineering needed — LLM handles variation"],
        automation_ceiling=0.72,
        examples=["OmniClaw multi-language TTS/STT (internal reference)", "Bharti Airtel WhatsApp bot (public)"],
        risk="Hinglish tokenization quality varies by model. Test on 100-sample set before full rollout. Risk of tone mismatch if not calibrated to regional cultural context.",
    ),
}


def get_pattern(identifier: str) -> Optional[OrgPattern]:
    """Find a pattern by name or alias."""
    identifier = identifier.lower().replace(" ", "_")
    if identifier in ORG_PATTERNS:
        return ORG_PATTERNS[identifier]
    for key, pattern in ORG_PATTERNS.items():
        if identifier in pattern.aliases or identifier in pattern.name.lower().replace(" ", "_"):
            return pattern
    return None


def list_patterns() -> list[str]:
    """Return summary of all pattern names."""
    return [f"{p.name} ({p.automation_ceiling:.0%} automation)" for p in ORG_PATTERNS.values()]


class OrgPatternAnalyzer:
    """Analyze signals and text for organizational design implications."""

    def __init__(self):
        self.patterns = ORG_PATTERNS

    def analyze_signal(self, text: str, source: str = "") -> list[dict]:
        """Analyze a signal and return matching org patterns with rationale."""
        text_lower = text.lower()
        matches = []

        keywords_map = {
            "agent_first_gtm": ["agent-first", "ai outbound", "llm agent", "autonomous sales", "sdr replacement", "agent fleet"],
            "ai_augmented_cs": ["customer success", "cs automation", "support agent", "churn prediction", "qbee", "tier 1 support"],
            "full_autonomous_revenue": ["full autonomy", "lights out", "agent closes", "autonomous close", "no human sales"],
            "ai_hybrid_product": ["product team", "pm augmented", "ai design", "squad ai", "agent product"],
            "hub_and_spoke_ops": ["centralized ai ops", "ai ops team", "hub and spoke", "shared agent infra"],
            "flat_agent_collective": ["flat org", "minimal hierarchy", "autonomous teams", "founder + agents"],
            "human_in_the_loop_enterprise": ["human in the loop", "enterprise ai", "ai assisted", "human approval", "human decision"],
            "outcome_based_ops": ["outcome based", "okr team", "outcome squad", "cross functional", "roi driven"],
            "ai_embedded_lending_ops": ["partner onboarding", "kyc", "eligibility", "disbursement", "embedded lending", "nbfc", "partner ops", "tofu"],
            "vernacular_ai_growth": ["whatsapp", "vernacular", "regional language", "hindi", "hinglish", "tier-2", "tier-3", "non-metro", "vernacular acquisition"],
        }

        for pattern_key, keywords in keywords_map.items():
            score = 0
            matches_found = []
            for kw in keywords:
                if kw in text_lower:
                    score += 0.3
                    matches_found.append(kw)

            if score >= 0.3:
                pattern = self.patterns[pattern_key]
                matches.append({
                    "pattern": pattern_key,
                    "name": pattern.name,
                    "match_score": min(score, 1.0),
                    "matched_keywords": matches_found,
                    "rationale": self._generate_rationale(pattern_key, matches_found),
                })

        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches

    def _generate_rationale(self, pattern_key: str, matched: list[str]) -> str:
        rationale_map = {
            "agent_first_gtm": f"Signal discusses AI agents in sales/outbound motion with keywords: {', '.join(matched)}",
            "ai_augmented_cs": f"Signal relates to customer success automation with indicators: {', '.join(matched)}",
            "full_autonomous_revenue": f"Signal describes autonomous revenue operation: {', '.join(matched)}",
            "ai_hybrid_product": f"Signal involves AI augmentation of product teams: {', '.join(matched)}",
            "hub_and_spoke_ops": f"Signal involves centralized AI ops with distributed execution: {', '.join(matched)}",
            "flat_agent_collective": f"Signal implies flat organizational structure with AI agents: {', '.join(matched)}",
            "human_in_the_loop_enterprise": f"Signal maintains human decision authority with AI assistance: {', '.join(matched)}",
            "outcome_based_ops": f"Signal emphasizes outcome-based organizational structure: {', '.join(matched)}",
            "ai_embedded_lending_ops": f"Signal relates to embedded lending partner ops automation (NIRO playbook): {', '.join(matched)}",
            "vernacular_ai_growth": f"Signal relates to vernacular-first India acquisition (WhatsApp/voice AI): {', '.join(matched)}",
        }
        return rationale_map.get(pattern_key, f"Matched on: {', '.join(matched)}")

    def get_implications(self, text: str, source: str = "") -> dict:
        """Get organizational implications from a signal."""
        matches = self.analyze_signal(text, source)

        implications = {
            "matched_patterns": [m["name"] for m in matches],
            "obsolete_patterns": [],
            "emerging_patterns": [],
            "coordination_shift": "unknown",
            "leverage_shift": "unknown",
            "hiring_implications": [],
            "decision_velocity_impact": "unknown",
        }

        if not matches:
            return implications

        for match in matches:
            pattern = self.patterns.get(match["pattern"])
            if not pattern or match["match_score"] < 0.4:
                continue

            implications["emerging_patterns"].append(pattern.name)

            if match["pattern"] == "agent_first_gtm":
                implications["obsolete_patterns"].extend(["Traditional SDR/BDR", "Human-led initial outreach"])
            elif match["pattern"] == "ai_augmented_cs":
                implications["obsolete_patterns"].extend(["Reactive tier-1 support", "High-touch CSM per small account"])
            elif match["pattern"] == "full_autonomous_revenue":
                implications["obsolete_patterns"].extend(["Sequential sales process", "Human-led full cycle"])
            elif match["pattern"] == "human_in_the_loop_enterprise":
                implications["obsolete_patterns"].append("Pure human-only workflow")

            if match["pattern"] in ["flat_agent_collective", "hub_and_spoke_ops"]:
                implications["coordination_shift"] = "decreases"
            elif match["pattern"] in ["full_autonomous_revenue"]:
                implications["coordination_shift"] = "redistributes"

            if match["pattern"] in ["agent_first_gtm", "ai_augmented_cs"]:
                implications["leverage_shift"] = "AI agents gain operational leverage, humans focus on judgment"
            elif match["pattern"] in ["human_in_the_loop_enterprise"]:
                implications["leverage_shift"] = "Humans retain decision leverage, AI amplifies execution"

            implications["hiring_implications"].extend(pattern.hiring_implications[:2])

            if match["pattern"] in ["agent_first_gtm", "full_autonomous_revenue", "ai_augmented_cs"]:
                implications["decision_velocity_impact"] = "increases"
            elif match["pattern"] == "human_in_the_loop_enterprise":
                implications["decision_velocity_impact"] = "slight_increase"

        implications["emerging_patterns"] = list(set(implications["emerging_patterns"]))
        implications["obsolete_patterns"] = list(set(implications["obsolete_patterns"]))
        implications["hiring_implications"] = list(set(implications["hiring_implications"]))[:4]

        return implications