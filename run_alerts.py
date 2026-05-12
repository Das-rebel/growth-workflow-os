#!/usr/bin/env python3
"""Alerts for high-priority signals.

Reads signals from last 24h, filters for high-priority, and sends
alerts via Telegram (OmniClaw bot) or WhatsApp (Baileys). Falls back to stdout.

Usage:
    python run_alerts.py              # Check DB and send alert
    python run_alerts.py --test        # Send a test alert
    python run_alerts.py --telegram    # Force Telegram (skip WhatsApp)
    python run_alerts.py --whatsapp    # Force WhatsApp (skip Telegram)
    python run_alerts.py --stdout      # Print to stdout only
"""

import sys
import os
import json
import subprocess
import argparse
import tempfile
import requests
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from config import get_db_path
from strategic_memory.store import SignalStore


# ── OmniClaw Telegram config ──────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = "8674030733:AAGr-eG-56VC0R-5yQ7ViCfc2NT4vy66TzM"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ── WhatsApp config ────────────────────────────────────────────────────────
GROUP_JID = "120363141914506124@g.us"
AUTH_DIR = os.path.expanduser("~/.omniclaw_auth")

HIGH_PRIORITY_KEYWORDS = [
    "launch", "acquisition", "regulation", "policy", "ban",
    "partnership", "shutdown", "ipo", "fundraise", "series ",
    "regulatory", "rbi", "sec ", "antitrust", "lawsuit",
    "merger", "acquire", "invested", "valuation",
]

BAILEYS_SENDER_JS = """
const { default: makeWASocket, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const pino = require('pino');

const authDir = process.argv[2];
const targetJid = process.argv[3];
const messageFile = process.argv[4];

async function send() {
    const { state, saveCreds } = await useMultiFileAuthState(authDir);
    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: false,
        logger: pino({ level: 'silent' }),
        browser: ['GrowthOS', 'Chrome', '1.0'],
    });
    sock.ev.on('creds.update', saveCreds);
    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect } = update;
        if (connection === 'open') {
            const msgText = require('fs').readFileSync(messageFile, 'utf8');
            await sock.sendMessage(targetJid, { text: msgText });
            console.log('SENT_OK');
            process.exit(0);
        }
        if (connection === 'close') {
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            console.error('CONNECTION_CLOSED code=' + statusCode);
            process.exit(1);
        }
    });
    setTimeout(() => { console.error('TIMEOUT'); process.exit(2); }, 30000);
}
send().catch(e => { console.error('FATAL:', e.message); process.exit(1); });
"""


# ── Telegram helpers ───────────────────────────────────────────────────────

def get_telegram_updates() -> list[dict]:
    """Get recent Telegram updates to find chat IDs."""
    try:
        resp = requests.get(f"{TELEGRAM_API}/getUpdates", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok"):
                return data.get("result", [])
    except Exception as e:
        print(f"Telegram getUpdates failed: {e}")
    return []


def send_telegram_message(chat_id: str, text: str) -> bool:
    """Send message via Telegram Bot API."""
    try:
        resp = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=15,
        )
        if resp.status_code == 200 and resp.json().get("ok"):
            print(f"Telegram message sent to {chat_id}")
            return True
        else:
            print(f"Telegram send failed: {resp.status_code} — {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"Telegram API error: {e}")
        return False


# ── WhatsApp helpers ───────────────────────────────────────────────────────

def send_whatsapp_message(message: str) -> bool:
    """Send WhatsApp message via Baileys one-shot script."""
    msg_file = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    msg_file.write(message)
    msg_file.close()

    script_file = tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False)
    script_file.write(BAILEYS_SENDER_JS)
    script_file.close()

    try:
        env = os.environ.copy()
        env["NODE_PATH"] = "/Users/Subho/node_modules"
        result = subprocess.run(
            ["node", script_file.name, AUTH_DIR, GROUP_JID, msg_file.name],
            capture_output=True, text=True, timeout=45, env=env,
        )
        if result.returncode == 0 and "SENT_OK" in result.stdout:
            print("WhatsApp alert sent successfully")
            return True
        else:
            print(f"WhatsApp send failed: rc={result.returncode}")
            if result.stderr:
                print(f"  stderr: {result.stderr[:300]}")
            return False
    except subprocess.TimeoutExpired:
        print("WhatsApp send timed out (30s)")
        return False
    except FileNotFoundError:
        print("Node.js not found — cannot send WhatsApp alert")
        return False
    finally:
        os.unlink(msg_file.name)
        os.unlink(script_file.name)


# ── Signal filtering ───────────────────────────────────────────────────────

def get_high_priority_signals(hours: int = 24) -> list[dict]:
    """Read signals from last N hours and filter for high priority."""
    import sqlite3
    db_path = get_db_path()
    if not db_path.exists():
        print(f"No DB found at {db_path}")
        return []

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rows = conn.execute(
        "SELECT * FROM signals WHERE collected_at >= ? ORDER BY collected_at DESC",
        (cutoff,),
    ).fetchall()
    conn.close()

    signals = [dict(r) for r in rows]
    print(f"Found {len(signals)} signals in last {hours}h")

    high_priority = []
    for s in signals:
        weight = s.get("strategic_weight")
        if weight is not None and weight >= 0.7:
            high_priority.append(s)
            continue
        text = (s.get("text") or "").lower()
        if any(kw in text for kw in HIGH_PRIORITY_KEYWORDS):
            high_priority.append(s)

    return high_priority


# ── Alert formatting ──────────────────────────────────────────────────────

def format_alert(signals: list[dict]) -> str:
    """Build alert message from signal list."""
    if not signals:
        return "✅ *Growth OS* — No high-priority signals in last 24h"

    header = f"🚨 *Growth OS Alert* — {len(signals)} high-priority signal(s)\n\n"
    items = []
    for i, s in enumerate(signals[:10], 1):
        weight_str = f" (weight: {s['strategic_weight']:.2f})" if s.get("strategic_weight") else ""
        items.append(f"*{i}.* {s['text'][:120]}...{weight_str}\n   📍 {s.get('source', 'unknown')}")

    footer = f"\n_More at http://localhost:8501_"
    return header + "\n".join(items) + footer


# ── Main alert dispatcher ─────────────────────────────────────────────────

def send_alert(message: str, mode: str = "auto") -> bool:
    """Send alert via Telegram or WhatsApp, falling back to stdout."""
    print("\n" + "=" * 50)
    print("Growth OS Alert Runner")
    print("=" * 50)
    print(f"Message preview: {message[:100]}...")

    # Find Telegram chat IDs from recent messages
    chat_ids = []
    updates = get_telegram_updates()
    for u in updates:
        msg = u.get("message") or u.get("edited_message")
        if msg:
            cid = str(msg["chat"]["id"])
            if cid not in chat_ids:
                chat_ids.append(cid)

    print(f"Found {len(chat_ids)} Telegram chat ID(s): {chat_ids}")

    # Try Telegram
    if mode in ("auto", "telegram") and chat_ids:
        for cid in chat_ids:
            ok = send_telegram_message(cid, message)
            if ok:
                return True

    # Try WhatsApp
    if mode in ("auto", "whatsapp"):
        ok = send_whatsapp_message(message)
        if ok:
            return True

    # Fallback to stdout
    print("\n--- Alert Message ---")
    print(message)
    print("--- End ---\n")
    print("Falling back to stdout (all channels unavailable)")
    return False


# ── CLI ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Growth OS Alert Runner")
    parser.add_argument("--test", action="store_true", help="Send a test alert")
    parser.add_argument("--telegram", action="store_true", help="Use Telegram only")
    parser.add_argument("--whatsapp", action="store_true", help="Use WhatsApp only")
    parser.add_argument("--stdout", action="store_true", help="Print to stdout only")
    args = parser.parse_args()

    if args.stdout:
        signals = get_high_priority_signals()
        print(format_alert(signals))
        return

    mode = "auto"
    if args.telegram:
        mode = "telegram"
    if args.whatsapp:
        mode = "whatsapp"

    if args.test:
        message = (
            "✅ *Growth OS Test Alert*\n\n"
            "WhatsApp integration working.\n"
            f"DB: {get_db_path()}\n"
            f"Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        )
    else:
        signals = get_high_priority_signals(hours=24)
        message = format_alert(signals)

    send_alert(message, mode=mode)


if __name__ == "__main__":
    main()