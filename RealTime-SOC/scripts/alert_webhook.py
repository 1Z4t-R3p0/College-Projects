#!/usr/bin/env python3
"""
=============================================================================
Wazuh Custom Webhook Integration
File: /var/ossec/integrations/custom_webhook
Description: Sends Wazuh alerts to Telegram, Discord, and generates incident
             report JSON. Triggered by Wazuh via the <integration> config.
=============================================================================
Setup:
  - Set environment variables (or edit constants below):
      TELEGRAM_BOT_TOKEN  = your Telegram bot token
      TELEGRAM_CHAT_ID    = your Telegram chat ID
      DISCORD_WEBHOOK_URL = your Discord webhook URL
  - chmod +x /var/ossec/integrations/custom_webhook
  - Wazuh will call this script with 3 args: alert.json hook_url api_key
=============================================================================
"""

import sys
import json
import os
import datetime
import urllib.request
import urllib.parse
import logging

# ===========================================================================
# Configuration — override via environment variables
# ===========================================================================
TELEGRAM_BOT_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN",  "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID    = os.getenv("TELEGRAM_CHAT_ID",    "YOUR_CHAT_ID_HERE")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "YOUR_DISCORD_WEBHOOK_HERE")
REPORTS_DIR         = os.getenv("REPORTS_DIR",         "/var/ossec/logs/incident_reports")

# Minimum alert level to trigger notifications (0 = all)
MIN_LEVEL = int(os.getenv("MIN_ALERT_LEVEL", "7"))

# ===========================================================================
# Logging
# ===========================================================================
logging.basicConfig(
    filename="/var/ossec/logs/integrations.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ===========================================================================
# Helpers
# ===========================================================================
def http_post(url: str, data: dict, headers: dict = None):
    """Generic HTTP POST using stdlib only (no requests dependency)."""
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8")
    except Exception as exc:
        log.error(f"HTTP POST to {url} failed: {exc}")
        return None, str(exc)


def level_emoji(level: int) -> str:
    if level >= 12: return "🔴"
    if level >= 9:  return "🟠"
    if level >= 7:  return "🟡"
    return "🟢"


def format_telegram(alert: dict) -> str:
    lvl  = alert.get("rule", {}).get("level", 0)
    desc = alert.get("rule", {}).get("description", "N/A")
    rid  = alert.get("rule", {}).get("id", "N/A")
    src  = alert.get("data", {}).get("srcip", alert.get("agent", {}).get("ip", "N/A"))
    host = alert.get("agent", {}).get("name", "Unknown")
    ts   = alert.get("timestamp", datetime.datetime.utcnow().isoformat())

    return (
        f"{level_emoji(lvl)} *Wazuh SOC Alert*\n\n"
        f"📋 *Rule:* `{rid}` — Level *{lvl}*\n"
        f"📝 *Description:* {desc}\n"
        f"🖥️ *Agent:* `{host}`\n"
        f"🌐 *Source IP:* `{src}`\n"
        f"🕒 *Time:* `{ts}`"
    )


def format_discord(alert: dict) -> dict:
    lvl  = alert.get("rule", {}).get("level", 0)
    desc = alert.get("rule", {}).get("description", "N/A")
    rid  = alert.get("rule", {}).get("id", "N/A")
    src  = alert.get("data", {}).get("srcip", alert.get("agent", {}).get("ip", "N/A"))
    host = alert.get("agent", {}).get("name", "Unknown")
    ts   = alert.get("timestamp", datetime.datetime.utcnow().isoformat())
    color = 0xFF0000 if lvl >= 12 else (0xFF8C00 if lvl >= 9 else 0xFFFF00)

    return {
        "username": "Wazuh SOC Bot",
        "avatar_url": "https://wazuh.com/wp-content/uploads/2022/03/wazuh-logo.svg",
        "embeds": [{
            "title": f"{level_emoji(lvl)} Wazuh Alert — Level {lvl}",
            "description": desc,
            "color": color,
            "fields": [
                {"name": "Rule ID",   "value": str(rid),  "inline": True},
                {"name": "Agent",     "value": host,      "inline": True},
                {"name": "Source IP", "value": src,       "inline": True},
                {"name": "Timestamp", "value": ts,        "inline": False},
            ],
            "footer": {"text": "Wazuh SOC Monitoring System"}
        }]
    }


def send_telegram(alert: dict):
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        log.warning("Telegram token not configured, skipping.")
        return
    url  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       format_telegram(alert),
        "parse_mode": "Markdown"
    }
    status, body = http_post(url, data)
    log.info(f"Telegram: HTTP {status}")


def send_discord(alert: dict):
    if DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_HERE":
        log.warning("Discord webhook not configured, skipping.")
        return
    status, body = http_post(DISCORD_WEBHOOK_URL, format_discord(alert))
    log.info(f"Discord: HTTP {status}")


def save_incident_report(alert: dict):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    ts   = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    lvl  = alert.get("rule", {}).get("level", 0)
    rid  = alert.get("rule", {}).get("id", "unknown")
    fname = f"{REPORTS_DIR}/incident_{ts}_rule{rid}.json"

    report = {
        "report_meta": {
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "tool": "Wazuh Custom Webhook",
            "version": "1.0"
        },
        "severity": "CRITICAL" if lvl >= 12 else ("HIGH" if lvl >= 9 else ("MEDIUM" if lvl >= 7 else "LOW")),
        "alert": alert
    }

    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    log.info(f"Incident report saved: {fname}")


# ===========================================================================
# Main entrypoint
# ===========================================================================
def main():
    # Wazuh passes: <alert_file> <hook_url> <api_key>
    if len(sys.argv) < 2:
        log.error("No alert file provided by Wazuh.")
        sys.exit(1)

    alert_file = sys.argv[1]

    try:
        with open(alert_file, "r") as f:
            alert = json.load(f)
    except Exception as exc:
        log.error(f"Failed to read alert file {alert_file}: {exc}")
        sys.exit(1)

    level = alert.get("rule", {}).get("level", 0)

    if level < MIN_LEVEL:
        log.info(f"Alert level {level} below threshold {MIN_LEVEL}, skipping.")
        sys.exit(0)

    log.info(f"Processing alert: rule={alert.get('rule',{}).get('id','?')} level={level}")

    save_incident_report(alert)
    send_telegram(alert)
    send_discord(alert)


if __name__ == "__main__":
    main()
