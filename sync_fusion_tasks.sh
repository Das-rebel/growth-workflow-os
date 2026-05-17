#!/bin/bash
# Fusion Tasks Sync Script - runs hourly
# Syncs local ~/.fusion/fusion.db to cloud dashboard

set -euo pipefail

LOCAL_DB="$HOME/.fusion/fusion.db"
CLOUD_API="https://fusion-dashboard-338789220059.asia-south1.run.app/api/tasks"
BEARER_TOKEN="${FUSION_BEARER_TOKEN:-fn_68fc5898c901a22af5fb52576b0dbf6e}"
LOG_FILE="$HOME/growth-workflow-os/logs/sync_fusion.log"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

python3 -c "
import subprocess, json, os, sys
from datetime import datetime

LOCAL_DB = os.environ.get('LOCAL_DB', '$HOME/.fusion/fusion.db')
CLOUD_API = os.environ.get('CLOUD_API', 'https://fusion-dashboard-338789220059.asia-south1.run.app/api/tasks')
BEARER_TOKEN = os.environ.get('BEARER_TOKEN', '$BEARER_TOKEN')
LOG_FILE = os.environ.get('LOG_FILE', '$LOG_FILE')

def log(msg):
    ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(line + '\n')
    except: pass

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def fetch_cloud_tasks():
    out, _ = run_cmd(f'curl -s -X GET \"{CLOUD_API}\" -H \"Authorization: Bearer {BEARER_TOKEN}\" -H \"Content-Type: application/json\"')
    try:
        data = json.loads(out) if out else []
        return data if isinstance(data, list) else []
    except:
        return []

def create_cloud_task(task_json):
    escaped = task_json.replace('\"', '\\\\\"')
    out, _ = run_cmd(f'curl -s -X POST \"{CLOUD_API}\" -H \"Authorization: Bearer {BEARER_TOKEN}\" -H \"Content-Type: application/json\" -d \"{escaped}\"')
    try:
        return json.loads(out) if out else {}
    except:
        return {}

def update_cloud_task(task_id, task_json):
    escaped = task_json.replace('\"', '\\\\\"')
    out, _ = run_cmd(f'curl -s -X PATCH \"{CLOUD_API}/{task_id}\" -H \"Authorization: Bearer {BEARER_TOKEN}\" -H \"Content-Type: application/json\" -d \"{escaped}\"')
    try:
        return json.loads(out) if out else {}
    except:
        return {}

def parse_local_tasks():
    cmd = f'sqlite3 {LOCAL_DB} \"SELECT * FROM tasks;\"'
    out, _ = run_cmd(cmd)
    tasks = []
    if not out:
        return tasks
    for line in out.split('\n'):
        if not line or '|' not in line:
            continue
        fields = line.split('|')
        if len(fields) < 50 or not fields[0].startswith('FN-'):
            continue
        tasks.append({
            'id': fields[0],
            'title': fields[1] if len(fields) > 1 else '',
            'description': fields[2] if len(fields) > 2 else '',
            'priority': fields[3] if len(fields) > 3 else 'normal',
            'column': fields[4] if len(fields) > 4 else 'backlog',
            'status': fields[5] if len(fields) > 5 else '',
            'size': fields[6] if len(fields) > 6 else '',
            'assigneeUserId': fields[39] if len(fields) > 39 else '',
            'createdAt': fields[47] if len(fields) > 47 else '',
            'updatedAt': fields[48] if len(fields) > 48 else '',
            'sourceIssueUrl': fields[29] if len(fields) > 29 else '',
            'sourceIssueNumber': fields[28] if len(fields) > 28 else '',
        })
    return tasks

log('=== Starting Fusion Task Sync ===')

if not os.path.exists(LOCAL_DB):
    log(f'Local DB not found at {LOCAL_DB}')
    sys.exit(1)

local_tasks = parse_local_tasks()
cloud_tasks_list = fetch_cloud_tasks()
cloud_tasks = {t.get('id', ''): t for t in cloud_tasks_list if t.get('id')}

created = updated = errors = 0

for task in local_tasks:
    task_id = task['id']
    cloud_json = json.dumps({
        'id': task_id,
        'title': task['title'] or 'Untitled',
        'description': task['description'],
        'priority': task['priority'],
        'column': task['column'],
        'status': task['status'],
        'sourceIssueUrl': task['sourceIssueUrl'] or None,
        'sourceIssueNumber': int(task['sourceIssueNumber']) if task['sourceIssueNumber'] else None,
        'createdAt': task['createdAt'],
        'updatedAt': task['updatedAt'],
    })
    if task_id in cloud_tasks:
        if cloud_tasks[task_id].get('updatedAt', '') != task['updatedAt']:
            result = update_cloud_task(task_id, cloud_json)
            if result.get('id'):
                updated += 1
                log(f'Updated {task_id}')
            else:
                errors += 1
    else:
        result = create_cloud_task(cloud_json)
        if result.get('id'):
            created += 1
            log(f'Created {task_id}')
        else:
            errors += 1

log(f'=== Sync Complete: created={created} updated={updated} errors={errors} ===')
"