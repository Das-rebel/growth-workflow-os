#!/bin/bash
# Fusion Tasks Sync Script
# Syncs local ~/.fusion/fusion.db to cloud dashboard and GitHub Issues

set -euo pipefail

# Config
LOCAL_DB="$HOME/.fusion/fusion.db"
CLOUD_API="https://fusion-dashboard-338789220059.asia-south1.run.app/api/tasks"
GITHUB_API="https://api.github.com"
GITHUB_REPO="Das-rebel/growth-workflow-os"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
BEARER_TOKEN="fn_68fc5898c901a22af5fb52576b0dbf6e"
LOG_FILE="$HOME/growth-workflow-os/logs/sync_fusion.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_FILE" >&2
}

# Python script for sync logic
PYTHON_SYNC='
import subprocess
import json
import os
import sys
import re
from datetime import datetime

LOCAL_DB = os.environ.get("LOCAL_DB", "/Users/Subho/.fusion/fusion.db")
CLOUD_API = os.environ.get("CLOUD_API", "https://fusion-dashboard-338789220059.asia-south1.run.app/api/tasks")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "fn_68fc5898c901a22af5fb52576b0dbf6e")
GITHUB_API = os.environ.get("GITHUB_API", "https://api.github.com")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "Das-rebel/growth-workflow-os")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
LOG_FILE = os.environ.get("LOG_FILE", "/Users/Subho/growth-workflow-os/logs/sync_fusion.log")

def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def error(msg):
    log(f"ERROR: {msg}")

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def fetch_cloud_tasks():
    cmd = f"curl -s -X GET \"{CLOUD_API}\" -H \"Authorization: Bearer {BEARER_TOKEN}\" -H \"Content-Type: application/json\""
    out, _ = run_cmd(cmd)
    try:
        return json.loads(out) if out else []
    except:
        return []

def fetch_cloud_task(task_id):
    cmd = f"curl -s -X GET \"{CLOUD_API}/{task_id}\" -H \"Authorization: Bearer {BEARER_TOKEN}\" -H \"Content-Type: application/json\""
    out, _ = run_cmd(cmd)
    try:
        return json.loads(out) if out else {}
    except:
        return {}

def create_cloud_task(task_json):
    cmd = f"curl -s -X POST \"{CLOUD_API}\" -H \"Authorization: Bearer {BEARER_TOKEN}\" -H \"Content-Type: application/json\" -d {repr(task_json)}"
    out, _ = run_cmd(cmd)
    try:
        return json.loads(out) if out else {}
    except:
        return {}

def update_cloud_task(task_id, task_json):
    cmd = f"curl -s -X PATCH \"{CLOUD_API}/{task_id}\" -H \"Authorization: Bearer {BEARER_TOKEN}\" -H \"Content-Type: application/json\" -d {repr(task_json)}"
    out, _ = run_cmd(cmd)
    try:
        return json.loads(out) if out else {}
    except:
        return {}

def list_github_issues():
    if not GITHUB_TOKEN:
        return []
    cmd = f"curl -s -X GET \"{GITHUB_API}/repos/{GITHUB_REPO}/issues?state=all&per_page=100\" -H \"Authorization: token {GITHUB_TOKEN}\" -H \"Accept: application/vnd.github.v3+json\""
    out, _ = run_cmd(cmd)
    try:
        return json.loads(out) if out else []
    except:
        return []

def escape_json(s):
    if s is None:
        return "null"
    return json.dumps(str(s))

def map_column(col):
    valid_cols = ["backlog", "todo", "in-progress", "done", "triage"]
    return col if col in valid_cols else col

def map_priority_to_label(priority):
    mapping = {"critical": "priority: critical", "high": "priority: high", "normal": "priority: medium", "low": "priority: low"}
    return mapping.get(priority, "priority: medium")

def parse_local_tasks():
    cmd = f"sqlite3 {LOCAL_DB} \"SELECT * FROM tasks;\""
    out, _ = run_cmd(cmd)
    
    tasks = []
    if not out:
        return tasks
    
    for line in out.split("\n"):
        if not line or "|" not in line:
            continue
        fields = line.split("|")
        if len(fields) < 50:
            continue
        
        task_id = fields[0]
        if not task_id.startswith("FN-"):
            continue
        
        task = {
            "id": task_id,
            "title": fields[1] if len(fields) > 1 else "",
            "description": fields[2] if len(fields) > 2 else "",
            "priority": fields[3] if len(fields) > 3 else "normal",
            "column": fields[4] if len(fields) > 4 else "backlog",
            "status": fields[5] if len(fields) > 5 else "",
            "size": fields[6] if len(fields) > 6 else "",
            "assigneeUserId": fields[39] if len(fields) > 39 else "",
            "createdAt": fields[47] if len(fields) > 47 else "",
            "updatedAt": fields[48] if len(fields) > 48 else "",
            "sourceIssueUrl": fields[29] if len(fields) > 29 else "",
            "sourceIssueNumber": fields[28] if len(fields) > 28 else "",
        }
        tasks.append(task)
    
    return tasks

def main():
    log("=== Starting Fusion Task Sync ===")
    
    if not os.path.exists(LOCAL_DB):
        error(f"Local DB not found at {LOCAL_DB}")
        sys.exit(1)
    
    # Get local tasks
    log("Fetching local tasks from SQLite...")
    local_tasks = parse_local_tasks()
    local_count = len(local_tasks)
    log(f"Found {local_count} local tasks")
    
    # Get cloud tasks
    log("Fetching cloud tasks...")
    cloud_tasks_list = fetch_cloud_tasks()
    cloud_tasks = {t.get("id", ""): t for t in cloud_tasks_list if t.get("id")}
    cloud_count = len(cloud_tasks)
    log(f"Found {cloud_count} cloud tasks")
    
    # Get GitHub issues for mapping
    log("Fetching GitHub issues...")
    github_issues = list_github_issues()
    issue_map = {}  # Maps issue number to URL
    for issue in github_issues:
        if isinstance(issue, dict):
            num = issue.get("number")
            url = issue.get("html_url")
            if num and url:
                issue_map[num] = url
    
    created = 0
    updated = 0
    errors = 0
    
    for task in local_tasks:
        task_id = task["id"]
        
        # Build task JSON for cloud API
        cloud_task_json = {
            "id": task_id,
            "title": task["title"] if task["title"] else "Untitled",
            "description": task["description"],
            "priority": task["priority"],
            "column": task["column"],
            "status": task["status"],
            "sourceIssueUrl": task["sourceIssueUrl"] if task["sourceIssueUrl"] else None,
            "sourceIssueNumber": int(task["sourceIssueNumber"]) if task["sourceIssueNumber"] else None,
            "createdAt": task["createdAt"],
            "updatedAt": task["updatedAt"],
        }
        
        cloud_json_str = json.dumps(cloud_task_json)
        
        if task_id in cloud_tasks:
            # Check if update needed
            cloud_task = cloud_tasks[task_id]
            cloud_updated = cloud_task.get("updatedAt", "")
            
            if task["updatedAt"] != cloud_updated:
                log(f"Updating cloud task {task_id}...")
                result = update_cloud_task(task_id, cloud_json_str)
                if result.get("id"):
                    updated += 1
                    log(f"Updated cloud task {task_id}")
                else:
                    errors += 1
                    error(f"Failed to update cloud task {task_id}: {result}")
        else:
            # Create new task
            log(f"Creating cloud task {task_id}...")
            result = create_cloud_task(cloud_json_str)
            if result.get("id"):
                created += 1
                log(f"Created cloud task {task_id}")
            else:
                errors += 1
                error(f"Failed to create cloud task {task_id}: {result}")
        
        # Handle GitHub Issue tracking
        issue_num = task.get("sourceIssueNumber")
        issue_url = task.get("sourceIssueUrl")
        
        if issue_num and str(issue_num) in issue_map:
            # Issue exists, would update here
            log(f"Task {task_id} linked to GitHub issue #{issue_num}")
        elif task["title"] and issue_url and "github.com" in str(issue_url):
            log(f"Task {task_id} needs GitHub issue created")
    
    log("=== Sync Complete ===")
    log(f"Created: {created}, Updated: {updated}, Errors: {errors}")
    
    # Save sync history
    history_file = os.path.join(os.path.dirname(LOG_FILE), "sync_history.jsonl")
    summary = {
        "syncTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "localCount": local_count,
        "cloudCount": cloud_count,
        "created": created,
        "updated": updated,
        "errors": errors
    }
    with open(history_file, "a") as f:
        f.write(json.dumps(summary) + "\n")

if __name__ == "__main__":
    main()
'

# Export config as environment variables
export LOCAL_DB
export CLOUD_API
export BEARER_TOKEN
export GITHUB_API
export GITHUB_REPO
export GITHUB_TOKEN
export LOG_FILE

# Run sync via Python
python3 -c "$PYTHON_SYNC"
