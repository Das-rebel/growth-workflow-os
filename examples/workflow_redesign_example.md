# Workflow Redesign Example: CRM Segmentation Automation

## Workflow: CRM Segmentation Redesign

**GROWTH_WORKFLOW_EXAMPLES["crm_segmentation_redesign"]**

---

## Before
Growth analyst spends 4 hours/week manually segmenting users by LTV band in Salesforce.
Manually tagging cohorts. Static rules. Segments update monthly.

**Subhajit reference:** Groww — risk-aware lifecycle targeting improved 30-day DAU 80%

---

## After
Signal detects cohort shift → inference routes to optimal next action → CRM updated automatically.
AI monitors engagement patterns across 5 LTV bands, triggers next-action workflows per segment.

**Subhajit reference:** Groww: 80% DAU improvement via lifecycle-aware segmentation

---

## Decision Routing
- AI handles standard cohort moves (LTV band transitions, engagement score updates)
- Human reviews >20% week-on-week LTV band shifts (anomaly detection)

---

## Implementation

### Step 1: Define LTV bands
```
Tier 1: LTV > ₹50,000   → premium nurture, dedicated CSM
Tier 2: LTV ₹15,000-50,000 → cross-sell trigger, standard cadence
Tier 3: LTV ₹5,000-15,000 → onboarding completion focus
Tier 4: LTV ₹1,000-5,000 → activation campaign
Tier 5: LTV < ₹1,000     → at-risk, churn prevention
```

### Step 2: Trigger events per band
```
Tier 4 → 3rd transaction not completed → trigger activation flow
Tier 3 → 30-day DAU drop >20% → trigger engagement campaign
Tier 2 → expansion signal → trigger cross-sell
Tier 1 → NPS <30 → escalate to CSM
```

### Step 3: AI monitoring rules
```
AI monitors daily:
  - Transaction frequency vs cohort median
  - DAU/WAU/MAU ratio
  - Feature adoption vs onboarding milestones
  - Support ticket sentiment trend

AI routes to:
  - Automated workflow (tag CRM, send sequence, update score)
  - Human review queue (if delta > 20% from cohort baseline)
```

### Step 4: Before vs After metrics
| Metric | Before | After |
|--------|--------|--------|
| Segmentation update frequency | Monthly | Daily |
| Time spent per week | 4 hrs | 20 min |
| Cohort accuracy | 60% | 95% |
| 30-day DAU improvement | Baseline | +80% (Groww) |
| At-risk detection | Weekly report | Real-time |

---

## Subhajit Das context

At Groww, this workflow was the highest-leverage growth intervention.
The 80% DAU improvement came from lifecycle-aware segmentation,
not from adding new features. Risk-aware targeting (not generic NPS)
was the mechanism.

Key insight: segment by engagement velocity, not just tenure.
Users who reach key activation milestones in 7 days vs 30 days
have 3x different LTV trajectories.
