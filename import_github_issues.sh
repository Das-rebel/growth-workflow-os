#!/bin/bash
# Import GitHub issues as Fusion tasks
# Usage: ./import_github_issues.sh
# Token: stored in GITHUB_TOKEN env var or ~/.bashrc

set -e

DASHBOARD_URL="${DASHBOARD_URL:-https://fusion-dashboard-338789220059.asia-south1.run.app}"
REPO="${REPO:-Das-rebel/growth-workflow-os}"
LABELS="${LABELS:-phase-7}"
PROJECT_ID="${PROJECT_ID:-proj_78438ccef36d4d5d}"

# Load token from ~/.bashrc if not set
if [[ -z "$GITHUB_TOKEN" ]]; then
  if [[ -f ~/.bashrc ]]; then
    export $(grep -v '^#' ~/.bashrc | grep 'GITHUB_TOKEN' | xargs | sed 's/ /\n/g' | grep 'GITHUB_TOKEN' | sed 's/=/ /' | awk '{print $2}') 2>/dev/null || true
  fi
fi

if [[ -z "$GITHUB_TOKEN" ]]; then
  echo "Error: GITHUB_TOKEN not set. Add 'export GITHUB_TOKEN=your_token' to ~/.bashrc"
  exit 1
fi

echo "Fetching issues from $REPO with label '$LABELS'..."

ISSUES=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$REPO/issues?labels=$LABELS&state=open&per_page=100")

if echo "$ISSUES" | grep -q '"message"'; then
  echo "GitHub API error:"
  echo "$ISSUES" | head -20
  exit 1
fi

ISSUE_COUNT=$(echo "$ISSUES" | grep -c '"id":' || echo "0")
echo "Found $ISSUE_COUNT open issues"

if [[ "$ISSUE_COUNT" == "0" ]]; then
  echo "No issues found. Exiting."
  exit 0
fi

echo "$ISSUES" | grep -o '"number":[0-9]*' | cut -d: -f2 | while read -r num; do
  echo "Fetching details for issue #$num..."
  ISSUE=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$REPO/issues/$num")

  TITLE=$(echo "$ISSUE" | grep -o '"title":"[^"]*"' | head -1 | sed 's/"title":"//;s/"$//')
  BODY=$(echo "$ISSUE" | grep -o '"body":"[^"]*"' | head -1 | sed 's/"body":"//;s/"$//' | cut -c1-2000)
  BODY="${BODY:-Issue #$num from $REPO}"
  URL=$(echo "$ISSUE" | grep -o '"html_url":"[^"]*"' | head -1 | sed 's/"html_url":"//;s/"$//')

  echo "Creating task: $TITLE"

  RESPONSE=$(curl -s -X POST "$DASHBOARD_URL/api/tasks" \
    -H "Content-Type: application/json" \
    -d "{
      \"title\": \"$TITLE\",
      \"description\": \"$BODY\n\nGitHub: $URL\",
      \"column\": \"triage\",
      \"priority\": \"normal\",
      \"sourceType\": \"github-import\",
      \"labels\": [\"$LABELS\"],
      \"projectId\": \"$PROJECT_ID\"
    }")

  if echo "$RESPONSE" | grep -q '"id"'; then
    TASK_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | sed 's/"id":"//;s/"$//')
    echo "  Created task $TASK_ID"
  else
    echo "  Error: $RESPONSE"
  fi
done

echo "Done. $ISSUE_COUNT issues processed."
