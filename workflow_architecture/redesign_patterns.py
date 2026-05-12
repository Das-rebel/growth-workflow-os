"""AI-native workflow redesign patterns catalog.

Each pattern specifies:
    - name: Unique identifier
    - before_state: What the workflow looks like without AI
    - after_state: What the AI-native workflow looks like
    - automation_score: 0.0-1.0, how automatable is the after-state
    - implementation_effort: low | medium | high
    - gtm_applicability: Which GTM functions this applies to
    - examples: Real-world manifestations of this pattern
    - key_AI_capabilities: The core AI abilities that enable this redesign

Pattern List:
    1. autonomous_outbound          — AI-driven outbound that replaces manual sequencing
    2. ai_cs_triage                 — AI-powered ticket triage and routing
    3. predictive_churn             — ML models identifying at-risk accounts before signals surface
    4. real_time_lead_scoring       — Dynamic ICP scoring that updates with every interaction
    5. dynamic_territory_management — AI-optimized territory assignment that adapts to signal
    6. automated_proposal_generation — AI-generated proposals from CRM context
    7. ai_assisted_negotiation      — AI coaching and template generation during deal negotiation
    8. outcome_based_renewal_automation — Trigger-based renewal workflows from health signals
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RedesignPattern:
    """A single workflow redesign pattern."""

    name: str
    category: str  # e.g., "outbound", "cs", "renewal"
    before_state: str  # Markdown description of current state
    after_state: str   # Markdown description of AI-native state
    automation_score: float  # 0.0-1.0
    implementation_effort: str  # low | medium | high
    gtm_applicability: list[str]  # e.g., ["sales", "marketing"]
    examples: list[str]  # Real-world examples or companies doing this
    key_ai_capabilities: list[str]  # e.g., ["LLM", "RAG", "fine-tuned classifier"]
    expected_impact: str  # One-liner on business impact
    transition_steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "automation_score": self.automation_score,
            "implementation_effort": self.implementation_effort,
            "gtm_applicability": self.gtm_applicability,
            "examples": self.examples,
            "key_ai_capabilities": self.key_ai_capabilities,
            "expected_impact": self.expected_impact,
            "transition_steps": self.transition_steps,
        }


PATTERNS = {


    "autonomous_outbound": RedesignPattern(
        name="autonomous_outbound",
        category="outbound",
        before_state="""## BEFORE: Manual Outbound Sequencing

**The Pain:**
1. SDRs spend 60% of day on manual research: LinkedIn, website, news, job postings
2. Email sequences are built from static templates, no personalization beyond name + company
3. Reps choose outreach order manually based on intuition or outdated CRM notes
4. Follow-up timing is arbitrary: rep decides when to retry based on gut feel
5. No real-time signal on which prospects are actively in-market
6. Sequence cadence is weekly/monthly, not responsive to buyer signals

**Time Sink:**
- SDR average: 4+ hrs/day on research + sequencing
- 12-18 touches over 8-12 weeks to generate 1 qualified meeting
- No feedback loop between engagement and subsequent touch strategy""",

        after_state="""## AFTER: AI-Driven Autonomous Outbound

**The Redesign:**
1. **Real-time research synthesis**: AI scrapes and summarizes a prospect's recent signals (news, social, job changes, funding, intent signals) within 30 seconds of entry
2. **Dynamic personalization at scale**: LLM generates tailored email per prospect using full context — not just name+company but recent activity, pain points inferred from their content, custom angle per ICP tier
3. **Signal-triggered sequencing**: If a prospect visits pricing page or clicks email, the system automatically advances them in sequence and triggers real-time follow-up (within 5 min)
4. **AI-determined optimal timing**: Model analyzes best send times per role/industry/persona and auto-schedules sends at statistically optimal moments
5. **Self-correcting sequences**: AI monitors engagement rates by variant (subject, body, CTA) and dynamically shifts copy to higher-performing angle
6. **Warm transfer orchestration**: When engagement score crosses threshold, AI books meeting directly (no human back-and-forth) or routes to rep with full context

**Key Metrics:**
- Time from lead entry → personalized outreach: < 2 minutes (vs. same-day manual)
- Personalization: 100% of outreach is contextually unique (vs. 5% manual)
- Sequence response rate: +40-80% improvement from baseline
- SDR capacity: 3-5x more prospects touched per day""",

        automation_score=0.85,
        implementation_effort="high",
        gtm_applicability=["sales", "marketing"],
        examples=[
            "Regie.ai — autonomous sales sequencing with AI content generation",
            "11x.ai — AI digital worker that researches + outreach autonomously",
            "Clay — combines 40+ data enrichment sources with AI personalization at scale",
            "Gong's 'Revenue Intelligence' — uses conversation intelligence to update ICP",
        ],
        key_ai_capabilities=["LLM for personalized copy generation", "Web scraping + data enrichment APIs", "Intent signal integration (Bombora, BuiltWith)", "CRM writeback automation", "A/B testing + reinforcement learning on copy variants"],
        expected_impact="3-5x SDR output, 40-80% lift in response rates, 50% reduction in research time per prospect",
        transition_steps=[
            "1. Connect enrichment stack (Clearbit, Apollo, or Clay) to CRM",
            "2. Deploy LLM-based email generation with templates per ICP segment",
            "3. Integrate intent signals (Bombora or G2 intent) to trigger sequence advancement",
            "4. Add AI-driven send-time optimization using historical engagement data",
            "5. Build warm-meeting-booking flow: AI schedules directly when engagement threshold hit",
        ],
    ),


    "ai_cs_triage": RedesignPattern(
        name="ai_cs_triage",
        category="customer_success",
        before_state="""## BEFORE: Manual CS Triage

**The Pain:**
1. Every inbound ticket lands in a shared queue — CSMs manually prioritize
2. CSMs spend 20-30 min per ticket reading context before responding
3. Routing is based on arbitrary round-robin or product category, not account health or issue complexity
4. High-value accounts wait in same queue as low-value, causing response time SLA violations for strategic customers
5. No auto-classification: CSMs read and tag tickets manually (95% of tickets mislabeled initially)
6. No pattern recognition: same issue handled differently by different CSMs
7. Frustrated CSMs: 40-60% of their time on tickets that could be self-resolved

**Time Sink:**
- Average CSM: 5-7 hours/day on triage + context-switching
- Mean time to first response (TTFR): 8-24 hours for standard accounts
- CSM burnout: 35% annual attrition in high-growth cos""",

        after_state="""## AFTER: AI-Powered CS Triage + Routing

**The Redesign:**
1. **AI ticket classification**: Incoming tickets auto-classified by issue type, complexity (Tier 1/2/3), and expected resolution path — 3-5 seconds per ticket, 94%+ accuracy
2. **Dynamic priority scoring**: Each ticket scored by: account_value × issue_urgency × health_trend. High-value + deteriorating accounts jump to front of queue automatically
3. **Auto-context assembly**: Before CSM touches ticket, AI surfaces: account history, related open tickets, recent product usage anomalies, last 3 interactions summary, relevant KB articles — all in one view
4. **Smart routing**: Tickets routed not just by category but by: CSM capacity + skill match + account relationship continuity. Never assign to CSM already at capacity
5. **Auto-response for Tier-1**: Common questions (password resets, feature how-tos, billing FAQs) answered automatically with AI-generated response, CSM reviews only
6. **Resolution pattern learning**: When a ticket type consistently requires specific info, AI prompts CSM for missing data before they even open the ticket

**Key Metrics:**
- TTFR: < 30 min for Tier-1, < 2 hours for Tier-2 (vs. 8-24h today)
- CSM context-switching: reduced 60% via auto-context
- Misclassification rate: < 5% (vs. 40%+ manual)
- Tier-1 volume handled by AI: 35-50% without human involvement
- CSM capacity freed: 4-6 hrs/day per CSM""",

        automation_score=0.78,
        implementation_effort="high",
        gtm_applicability=["customer_success", "operations"],
        examples=[
            "Zendesk AI — automatically categorizes + suggests replies",
            "Gorgias — AI triage for e-commerce support, auto-resolves 40%+ tickets",
            "Intercom Fin — AI resolution for common questions, 50%+ resolution rate",
            "Forethought — AI-powered ticket routing + auto-tagging for enterprise",
        ],
        key_ai_capabilities=["LLM for classification + response generation", "RAG over support KB + past resolutions", "CRM context injection (Health Score, MRR, tier)", "Ticket metadata extraction + intent detection", "Integration with support platform (Zendesk, Freshdesk, Intercom)"],
        expected_impact="50-70% reduction in CSM triage time, TTFR cut by 60-80%, 35-50% Tier-1 tickets auto-resolved",
        transition_steps=[
            "1. Ingest historical tickets to fine-tune classifier on issue types",
            "2. Build RAG pipeline: KB articles + past resolved tickets → LLM context",
            "3. Deploy ticket classifier + priority scorer between support platform and CRM",
            "4. Create Tier-1 auto-response flow with CSM review gate",
            "5. Connect CSM capacity model for smart routing",
        ],
    ),


    "predictive_churn": RedesignPattern(
        name="predictive_churn",
        category="renewal",
        before_state="""## BEFORE: Reactive Churn Identification

**The Pain:**
1. Churn is identified when customer says "we're leaving" or submits cancellation request — 30-60 days too late
2. Health scores are based on lagging indicators: login frequency, support tickets, renewal date proximity
3. No early warning on product-usage decline: CSMs notice when usage drops 60%, not when it drops 10-15%
4. Every CSM has 80-150 accounts — impossible to manually monitor usage patterns
5. Churn risk is discussed only at quarterly business reviews, not continuously
6. Intervention is always reactive: save plays after the customer has already mentally left

**Time Sink:**
- Average save attempt: 2-3 weeks of intensive CSM effort, 30-50% success rate
- Lost revenue identified too late for effective mitigation
- CSM bandwidth consumed by accounts that won't churn, under-monitoring accounts that will""",

        after_state="""## AFTER: ML-Driven Predictive Churn with Continuous Monitoring

**The Redesign:**
1. **Feature engineering from behavioral data**: Build churn predictors from product usage signals: feature adoption velocity, depth of usage over time, collaboration patterns (internal users), anomaly detection on usage baselines, NPS response patterns, support ticket sentiment trend
2. **Continuous risk scoring**: Account health score updates daily (not monthly/quarterly) using multivariate model — not a single score but a decomposition: product risk, relationship risk, competitive risk, financial risk
3. **Early warning triggers at 30/60/90 days**: When risk score crosses threshold, system triggers: CSM alert + recommended play + auto-creation of success plan in CRM
4. **Segment-specific models**: Different models for different customer segments (enterprise vs. SMB, product-led vs. sales-led, annual vs. monthly). Generic churn models perform poorly across segments
5. **AI-generated save playbooks**: Based on why this specific account is at risk (not generic), AI generates account-specific intervention: which champion to engage, what content to share, what executive to loop in, what offer to make
6. **Closed-loop learning**: When save attempt succeeds/fails, model updates — learns which interventions work for which churn patterns

**Key Metrics:**
- Churn prediction lead time: 30-60 days before cancellation intent (vs. current reactive)
- Prediction accuracy: 75-85% precision at 60% recall (industry benchmarks vary widely)
- Reduction in surprise churn: 50%+ of at-risk accounts identified proactively
- Save attempt efficiency: AI playbook guidance increases save rate by 20-40%""",

        automation_score=0.72,
        implementation_effort="high",
        gtm_applicability=["customer_success", "sales"],
        examples=[
            "Gainsight PX — product usage intelligence + health scoring for enterprise",
            "Totango — ML-based health scoring with automated customer journey orchestration",
            "ChurnZero — real-time customer health + automated engagement triggers",
            "Gong CS — conversation intelligence for relationship risk detection in post-sale",
        ],
        key_ai_capabilities=["Feature store / behavioral data pipeline", "ML classifier (gradient boosting or survival analysis)", "Time-series anomaly detection on usage baselines", "CRM writeback + CSM alert system", "RAG-based playbook generator from past save attempts"],
        expected_impact="30-50% reduction in surprise churn, 20-40% improvement in save rates, CSMs focus effort on accounts that need them",
        transition_steps=[
            "1. Build behavioral feature pipeline: product usage events → feature store",
            "2. Label historical churn data (churned vs. retained at 30/60/90 days)",
            "3. Train churn classifier per segment with time-to-event model",
            "4. Deploy risk scoring job that runs daily, writes to CRM custom field",
            "5. Build threshold-based alert system for CSMs + auto-create success plans",
            "6. Integrate playbook generator: trigger on risk score threshold → LLM generates save play",
        ],
    ),


    "real_time_lead_scoring": RedesignPattern(
        name="real_time_lead_scoring",
        category="lead_management",
        before_state="""## BEFORE: Static Lead Scoring + Lagging MQL Definition

**The Pain:**
1. Lead scoring is based on static demographic firmographics (company size, industry, title) — no behavioral signal
2. Score is recalculated nightly at best, often weekly — by the time rep calls, lead's intent may have changed
3. MQL definition is generic (visited homepage + filled form) — marketing decides, sales ignores
4. No ICP clarity: every rep interprets 'good lead' differently
5. Sales ignores 60% of marketing-generated leads because scoring doesn't match real conversion probability
6. Lead-to-rep assignment is round-robin, not based on account fit or rep specialty
7. No real-time enrichment: reps work with stale data from time of form submission

**Time Sink:**
- Reps waste 2-4 hrs/week calling leads that are no longer in-market
- Marketing generates MQLs that sales rejects, creating friction and misaligned incentives
- Nurture cadences run regardless of buyer's current intent signal""",

        after_state="""## AFTER: AI-Driven Real-Time Lead Scoring with Intent Signals

**The Redesign:**
1. **Behavioral intent scoring**: Composite score updated in real-time as prospect interacts with content, visits pricing, downloads whitepapers, attends webinars, engages with email. Score = frequency × recency × intent depth × content quality
2. **Firmographic + technographic enrichment**: Real-time data append (Clearbit, Apollo, or Crunchbase) on company funding, hiring trends, tech stack (indicator of growth or decline), news events
3. **Dynamic ICP matching**: AI compares every inbound lead against actual closed-won pattern (not assumed ideal customer profile) — what does the real customer look like? Updates as deal outcomes come in
4. **Predictive conversion probability**: Model trained on historical lead-to-close data predicts: this lead → X% probability of becoming an opportunity → Y% probability of closing. Score not binary (MQL/not-MQL) but continuous + segmented by rep/territory fit
5. **AI-driven lead routing**: When high-intent lead appears, system routes to rep with: lowest current capacity + highest historical conversion on this lead type + account familiarity
6. **Real-time engagement triggers**: When intent score spikes (prospect visited pricing 3x in one day), AI triggers: alert to assigned rep + auto-enroll in high-urgency sequence + Slack notification with context

**Key Metrics:**
- Lead response time: < 5 min for high-intent (vs. hours/days)
- Sales-accepted rate: 75%+ (vs. current 40-50%)
- Lead-to-opportunity conversion: +30-60% improvement
- Rep time on dead leads: -50% (fewer low-intent calls)""",

        automation_score=0.80,
        implementation_effort="medium",
        gtm_applicability=["sales", "marketing"],
        examples=[
            "6sense — account-based intent detection + real-time scoring for ABM",
            "MadKudu — predictive lead scoring using behavioral + firmographic data",
            "LeanData — real-time lead routing matched to buying stage + rep capacity",
            "RollWorks — intent signal aggregation + dynamic lead scoring",
        ],
        key_ai_capabilities=["Intent data integration (Bombora, G2, BuiltWith)", "LLM for dynamic ICP recalibration from closed-won data", "CRM writeback + rep notification pipeline", "Lead routing optimization model", "Real-time enrichment APIs (Clearbit, Apollo)"],
        expected_impact="+30-60% lead-to-opportunity conversion, < 5 min response time for high-intent, 50% reduction in time wasted on cold leads",
        transition_steps=[
            "1. Integrate intent data provider (Bombora or G2) with CRM",
            "2. Train conversion probability model on historical lead→close data",
            "3. Deploy real-time scoring job: triggered on behavioral events",
            "4. Build dynamic routing logic: intent + capacity + rep fit",
            "5. Create alert + auto-sequence triggers for spike events",
        ],
    ),


    "dynamic_territory_management": RedesignPattern(
        name="dynamic_territory_management",
        category="territory_planning",
        before_state="""## BEFORE: Static Annual Territory Planning

**The Pain:**
1. Territories are set annually (Q4 planning) and rarely adjusted mid-year
2. Reps inherit territories based on historical account assignments, not optimal coverage
3. No real-time rebalancing: when a rep leaves, accounts go dark for weeks
4. 'White space' (prospects not assigned to anyone) accumulates all year
5. Account assignment is manual — managers spend 10-20 hrs per quarter on territory math
6. No algorithmic optimization: coverage based on geography + intuition, not account density or rep capacity
7. New reps wait months for territory assignments while ramp is slow

**Time Sink:**
- Territory planning consumes 40-80 hrs/quarter of manager time
- 20-30% of accounts unassigned or under-covered at any given time
- Quota attainment varies wildly due to uneven territory quality, not rep ability
- Reps in poor territories underperform regardless of skill""",

        after_state="""## AFTER: AI-Optimized Dynamic Territory Rebalancing

**The Redesign:**
1. **Algorithmic territory optimization**: Model considers: account potential score, coverage density, rep capacity, travel time / time zones, account-to-rep relationship continuity, quota attainment equity. Runs optimization quarterly or on-demand
2. **Continuous rebalancing triggers**: When specific signals fire (rep leaves, new logo acquired, account migrates to enterprise tier), system triggers territory rebalancing — not annual, event-driven
3. **White space detection**: AI continuously monitors for accounts that fall between assigned reps, surface white space immediately, and triggers assignment
4. **Scenario planning for managers**: Before finalizing rebalancing, AI simulates 3-5 scenarios showing: coverage impact, quota distribution, at-risk accounts from relationship change, estimated revenue impact
5. **Rep-to-account affinity scoring**: AI calculates relationship strength per rep-account pair (past engagement depth, number of contacts, deal history). Territory changes minimize relationship disruption
6. **Automatic account handoff playbooks**: When territory changes trigger account migration, AI generates handoff memo for outgoing and incoming rep — account context, relationship notes, deal status

**Key Metrics:**
- Time spent on territory planning: -70% (from 40-80 hrs to < 15 hrs/quarter)
- Coverage gaps (unassigned white space): -50% reduction
- Quota attainment variance between territories: -30%
- Time from rep departure to full coverage: days vs. weeks""",

        automation_score=0.75,
        implementation_effort="high",
        gtm_applicability=["sales", "operations"],
        examples=[
            "Clari — automated territory suggestions based on deal flow analysis",
            "Salesforce Revenue Cloud — AI-powered territory management for enterprises",
            "Xactly — territory modeling with quota attainment optimization",
            "Varicent — incentive compensation + territory planning combined",
        ],
        key_ai_capabilities=["Optimization solver (linear programming or genetic algorithm)", "CRM integration for account history + contact relationships", "Rep capacity model", "Scenario simulation engine", "Handoff memo generation via LLM"],
        expected_impact="-70% manager time on territory planning, -50% coverage gaps, -30% quota attainment variance between territories",
        transition_steps=[
            "1. Build account potential scoring model from historical data (ACV, growth rate, engagement)",
            "2. Create rep capacity model: max accounts, travel time, current quota load",
            "3. Deploy optimization solver for territory rebalancing",
            "4. Build scenario simulation tool for managers to compare options",
            "5. Implement automatic handoff playbook generation on territory changes",
        ],
    ),


    "automated_proposal_generation": RedesignPattern(
        name="automated_proposal_generation",
        category="sales",
        before_state="""## BEFORE: Manual Proposal Creation (5-7 Day Cycle)

**The Pain:**
1. Sales reps spend 4-8 hours building proposals: copy pricing from CRM, format in Word/PDF, assemble case studies, verify legal terms, get manager approval
2. Each proposal is manually assembled, so quality varies dramatically by rep skill
3. Pricing is often static — no automatic discounting logic based on deal characteristics
4. Revisions are slow: if customer wants changes, rep manually updates and waits for re-approval
5. No real-time context: proposal doesn't reflect customer's specific use case or prior conversations
6. Legal review adds 1-3 days per proposal version
7. Sales team creates 50-200 proposals/month manually — significant capacity drain

**Time Sink:**
- 4-8 hours per proposal × 50-200 proposals/month = 200-1,600 hours/month of rep time
- 5-7 day proposal cycle time includes 1-2 days of waiting on formatting/assembly
- Revision cycles add 1-3 days each""",

        after_state="""## AFTER: AI-Generated Proposals from CRM Context (< 2 Hours)

**The Redesign:**
1. **Template engine with dynamic content injection**: Proposals use structured templates that auto-fill from CRM: customer name, contacts, company context, deal specifics, usage terms, pricing — no manual copy-paste
2. **LLM-generated customization**: AI reads CRM notes from discovery calls + prior emails + public company info → generates personalized value prop sections, relevant case studies, ROI models specific to their industry
3. **Automated pricing logic**: Pricing module applies discount rules automatically based on: deal size, term length, customer segment, competitive situation, capacity. AI proposes optimal price, rep approves or adjusts
4. **Legal clause library**: Approved legal language stored in structured library, auto-populated based on contract type. Deviations from standard terms flagged for review — reducing legal review time by 70%+
5. **Revision in minutes, not days**: When customer requests changes, AI regenerates specific sections in < 30 minutes. Rep reviews, sends — no re-formatting, no re-approval loops for minor changes
6. **AI-powered negotiation support**: During negotiation, rep can ask: 'What discount should I offer given this context?' AI analyzes competitive pressure, relationship value, remaining budget → recommends specific concession + explains rationale

**Key Metrics:**
- Proposal cycle time: < 2 hours (vs. 5-7 days today)
- Revision cycles: 1-2 (vs. 3-5 today)
- Legal review time: -70% (most proposals auto-approved from clause library)
- Sales rep time per proposal: -80% (4-8 hrs → 45-60 min)
- Win rate improvement: +10-20% (more personalized, consistent quality)""",

        automation_score=0.82,
        implementation_effort="medium",
        gtm_applicability=["sales"],
        examples=[
            "Qvidian — automated proposal generation with workflow approval",
            "Mediafly — AI-driven sales content + proposal automation",
            "Showpad — proposal generation tied to deal stage + CRM context",
            "DocuSign Agreement Cloud — contract automation with AI clauses",
        ],
        key_ai_capabilities=["LLM for section generation + customization", "CRM data integration (deal context, contacts, notes)", "Legal clause library with structured approval rules", "Pricing rule engine with discount logic", "RAG over past proposals + win/loss analysis"],
        expected_impact="Proposal cycle: 5-7 days → < 2 hours, -80% rep time per proposal, legal review -70%, +10-20% win rate",
        transition_steps=[
            "1. Build proposal template library with dynamic variable injection points",
            "2. Deploy CRM-to-template data pipeline (deal fields → proposal sections)",
            "3. Create legal clause library with approval rules per clause type",
            "4. Build LLM customization layer: uses CRM notes + company context → personalized sections",
            "5. Add pricing rule engine with discount logic per deal characteristics",
            "6. Integrate AI negotiation assistant: contextual discount recommendation",
        ],
    ),


    "ai_assisted_negotiation": RedesignPattern(
        name="ai_assisted_negotiation",
        category="sales",
        before_state="""## BEFORE: Negotiation Without Real-Time Intelligence

**The Pain:**
1. Reps negotiate blind: no insight into counterpart's likely walk-away price, alternatives, authority level, or priorities
2. Negotiation prep is manual: rep reads past email threads, hopes to remember key points, has no systematic framework
3. During live negotiation, rep can't process multiple variables fast enough: price, term, scope, support level, references
4. Management has no visibility into deal risks until late — deals slip or discount excessively
5. No learning loop: same mistakes repeated across deals because there's no systematic capture
6. Counterparties who are more sophisticated (enterprise buyers with procurement teams) exploit reps who lack negotiation intelligence

**Time Sink:**
- Average discount given in first counter-offer exceeds what's necessary 40% of the time
- Deals that go to second/third approval cycle: 20-30% could have closed at first with better negotiation
- Reps report 'giving away too much' as their #1 negotiation frustration""",

        after_state="""## AFTER: AI Negotiation Intelligence in Real-Time

**The Redesign:**
1. **Pre-negotiation briefing**: Before any negotiation, AI generates a briefing: counterparty's likely priorities (from public info + CRM), historical patterns with similar companies, what concessions are likely low-cost vs. high-cost to give, BATNA indicators (do they have alternatives?), recommended approach
2. **Live deal intelligence dashboard**: During negotiation, AI tracks deal variables: price, term, volume, support tier, SLA, references, payment terms. Shows real-time: deal risk score, discount depth vs. baseline, what this deal looks like vs. similar closed-won
3. **Counter-offer analyzer**: When counterparty makes offer, AI instantly analyzes: how does this compare to best alternative scenario? What is their likely walk-away? Which terms are they likely flexible on? Recommends counter-strategy
4. **Concession guidance in real-time**: Rep sees: 'If you reduce price 10%, increase term to 2 years to protect NRR' or 'They're likely to accept 7% discount if you add Q1 onboarding support — low cost to you, high value to them'
5. **Manager oversight without intrusion**: Managers see deal health + risk scores in real-time without being in the room. Alerts fire when deal risk exceeds threshold or rep is about to exceed discount authority
6. **Post-negotiation learning capture**: After each negotiation, AI generates summary: what was conceded, what was held, what signals predicted behavior, what to do differently next time — feeds into next prep briefing

**Key Metrics:**
- Average discount depth: -15-25% reduction (negotiate to better outcome without losing deal)
- Deals requiring second approval cycle: -40%
- Rep confidence score: +35% (measured via survey)
- Manager deal visibility: 100% (vs. current < 30% mid-stage visibility)""",

        automation_score=0.70,
        implementation_effort="high",
        gtm_applicability=["sales"],
        examples=[
            "Gong's deal risk scores — real-time negotiation intelligence during calls",
            "Microsoft Dynamics 365 Sales Insights — deal health scoring + conversation intelligence",
            "Clari — deal risk tracking + executive sponsor detection",
            "ScrivenAI — negotiation intelligence for sales teams",
        ],
        key_ai_capabilities=["RAG over deal history + past negotiation outcomes", "Real-time deal variable tracking", "Comparative analysis vs. similar closed-won patterns", "LLM concession strategy generation", "Manager alert system for deal risk threshold breach"],
        expected_impact="-15-25% discount depth, -40% second approval cycles, +35% rep negotiation confidence",
        transition_steps=[
            "1. Build deal variable tracking model from CRM deal fields",
            "2. Train concession strategy model on historical negotiation outcomes",
            "3. Create pre-negotiation briefing generator: CRM + public data → rep briefing",
            "4. Deploy live deal dashboard with risk scoring",
            "5. Add counter-offer analyzer: incoming offer → recommended response",
            "6. Build manager alert system for deal risk threshold breaches",
        ],
    ),


    "outcome_based_renewal_automation": RedesignPattern(
        name="outcome_based_renewal_automation",
        category="renewal",
        before_state="""## BEFORE: Renewal Driven by Contract Date, Not Customer Outcomes

**The Pain:**
1. Renewal is triggered by contract end date — not by whether customer achieved value
2. CSMs run renewal plays at 90/60/30 day marks regardless of account health: healthy accounts get over-touch, unhealthy accounts get last-minute save attempts
3. No link between product usage and renewal likelihood: if customer never adopted core features, renewal conversation is a shock
4. Renewal conversations are generic: 'time to renew' without evidence of ROI
5. Expansion opportunities at renewal are missed because no one has visibility into growth signals
6. Finance sees revenue 'cliff' at renewal but can't predict reliably which will convert
7. CSM bandwidth consumed by low-risk renewals that don't need intensive touch

**Time Sink:**
- CSMs spend 30-40% of renewal cycle on accounts that would auto-renew
- Renewal preparation (data gathering, ROI report building) takes 3-5 hours per account per CSM
- Revenue forecast uncertainty: ±20% on renewal cohort due to poor predictability""",

        after_state="""## AFTER: Outcome-Linked Renewal Orchestration

**The Redesign:**
1. **Outcome tracking continuous**: System tracks product adoption milestones vs. customer's stated success metrics (from onboarding). Each customer has a success plan: key features they should use, business outcomes they want. Progress fed to AI continuously
2. **Renewal likelihood scoring by outcome achievement**: Instead of contract-date-triggered renewal, AI scores renewal probability based on: outcome completion % + support sentiment trend + competitive signals. Renewal readiness = 0-100% updated weekly
3. **Trigger-based renewal cadence**: Renewal touch timing is driven by outcome score, not contract date. Healthy accounts: auto-renew with notification at 30 days. At-risk accounts: CSM intervention at 90+ days. Champions are engaged early with evidence of ROI
4. **AI-generated renewal evidence package**: When renewal is approaching, AI assembles: adoption timeline, feature usage vs. similar cohorts, ROI estimate based on their usage patterns, benchmark vs. their industry. CSM reviews, sends — 15 min vs. 3-5 hrs
5. **Expansion identification at renewal**: AI scans for growth signals: full usage of current tier, new use cases in usage data, budget increase signals, hiring trends (more users). Flags expansion opportunity before renewal conversation
6. **Revenue forecasting from outcome model**: Renewal predictability: which accounts will renew, which will expand, which will churn — predicted 90 days out with ±5% accuracy vs. current ±20%

**Key Metrics:**
- Renewal rate: +10-20% (outcome conversations vs. date-driven conversations)
- CSM time on renewal: -60% (auto-renewal for healthy, focused intervention for at-risk)
- Renewal prep time: 3-5 hrs → 15-30 min per account
- Revenue forecast accuracy: ±5-8% (vs. ±20% today)
- Expansion revenue at renewal: +25-40% (better identification of expansion candidates)""",

        automation_score=0.76,
        implementation_effort="medium",
        gtm_applicability=["customer_success", "sales", "finance"],
        examples=[
            "Gainsight — outcome-driven customer success with renewal automation",
            "Catalyst (by Salesforce) — outcome-based success with renewal scoring",
            "Vitally — product-led CS with renewal risk scoring",
            "Netsuite Customer Central — financial outcome tracking for renewal",
        ],
        key_ai_capabilities=["Outcome milestone tracking from product events", "Renewal probability model (survival analysis)", "RAG for ROI evidence assembly", "Expansion signal detection from usage + firmographic data", "Revenue forecasting model for renewal cohort"],
        expected_impact="+10-20% renewal rate, -60% CSM renewal time, ±5% forecast accuracy vs. ±20% today, +25-40% expansion identification",
        transition_steps=[
            "1. Define outcome milestones per customer segment (from onboarding success plans)",
            "2. Build product adoption tracking pipeline (events → outcome score)",
            "3. Train renewal probability model on historical renewal + outcome data",
            "4. Create renewal trigger logic: outcome score + contract proximity → cadence",
            "5. Deploy AI-generated ROI evidence package (RAG over usage + benchmarks)",
            "6. Build expansion signal detection: usage saturation + firmographic triggers",
        ],
    ),


}


def get_pattern(name: str) -> Optional[RedesignPattern]:
    """Get a pattern by name."""
    return PATTERNS.get(name)


def get_patterns_by_gtm(gtm_function: str) -> list[RedesignPattern]:
    """Get all patterns applicable to a GTM function."""
    return [p for p in PATTERNS.values() if gtm_function in p.gtm_applicability]


def get_patterns_by_automation_threshold(min_score: float) -> list[RedesignPattern]:
    """Get patterns with automation_score >= threshold."""
    return [p for p in PATTERNS.values() if p.automation_score >= min_score]


def get_all_patterns() -> list[RedesignPattern]:
    """Return all patterns sorted by automation_score descending."""
    return sorted(PATTERNS.values(), key=lambda p: -p.automation_score)


# ---------------------------------------------------------------------------
# GROWTH_WORKFLOW_EXAMPLES — 6 concrete Subhajit Das examples
# Each example grounded in real fintech metrics from Axis, Groww, NIRO, ABC
# ---------------------------------------------------------------------------

GROWTH_WORKFLOW_EXAMPLES: dict = {

    "crm_segmentation_redesign": {
        "workflow": "Weekly manual CRM cohort review → AI-assisted next-action routing",
        "before": "Growth analyst spends 4hrs/week segmenting users by LTV band, manually tagging CRM",
        "after": "Signal detects cohort shift → inference routes to optimal next action → CRM updated",
        "decision_routing": "AI handles standard cohort moves; human reviews >20% week-on-week shifts",
        "subhajit_reference": "Groww: risk-aware lifecycle targeting improved 30-day DAU 80%",
    },

    "retention_escalation": {
        "workflow": "At-risk user detection → tiered intervention → human escalation for edge cases",
        "before": "Weekly churn report → ad hoc campaigns → low personalization",
        "after": "Engagement drop signal → churn probability inference → automated offer or human queue",
        "decision_routing": "AI confidence >0.8: automated. <0.8: human review queue",
        "subhajit_reference": "Groww: campaign lead conversion interventions boosted revenue 60%",
    },

    "lead_qualification_routing": {
        "workflow": "Inbound lead → AI qualification → human/AI/hybrid routing",
        "decision_routing": "AI handles <₹1L ticket, human reviews >₹5L, hybrid for mid-range",
        "subhajit_reference": "NIRO: structured routing reduced partner onboarding 50%",
    },

    "campaign_prioritisation": {
        "workflow": "Weekly planning → AI-ranked priority queue → budget allocation recommendation",
        "decision_routing": "AI recommends; human approves if reallocation >20% of total budget",
        "subhajit_reference": "Axis Bank: ₹1,500Cr portfolio — 120% secured loan growth via data-led channel strategy",
    },

    "embedded_lending_activation": {
        "workflow": "New D2C partner signal → eligibility inference → KYC routing → activation memo",
        "decision_routing": "AI handles standard partners; human reviews non-standard FLDG structures",
        "subhajit_reference": "NIRO: Mygate/Snapdeal/Nobroker → ₹70Cr/month disbursals in 6 months",
    },

    "lifecycle_automation": {
        "workflow": "Lifecycle event → trigger → workflow → operator memo",
        "decision_routing": "AI owns standard moves; human reviews value destruction signals",
        "subhajit_reference": "Groww: LTV and retention-focused growth across app + web",
    },

}


def patterns_summary() -> dict:
    """Return a summary dict of all patterns."""
    return {name: {"automation_score": p.automation_score, "implementation_effort": p.implementation_effort, "gtm_applicability": p.gtm_applicability, "expected_impact": p.expected_impact} for name, p in PATTERNS.items()}


def demo():
    """Print pattern catalog summary."""
    print("=" * 80)
    print("AI-NATIVE WORKFLOW REDESIGN PATTERNS")
    print("=" * 80)
    print(f"\nTotal patterns: {len(PATTERNS)}\n")
    print(f"{'Pattern':<35} {'Score':<7} {'Effort':<8} {'GTM Functions'}")
    print("-" * 90)
    for p in get_all_patterns():
        print(f"{p.name:<35} {p.automation_score:<7.2f} {p.implementation_effort:<8} {', '.join(p.gtm_applicability)}")
    print("\n")


if __name__ == "__main__":
    demo()