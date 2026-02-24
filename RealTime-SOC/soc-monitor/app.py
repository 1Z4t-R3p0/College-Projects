from flask import Flask, render_template, jsonify
import json
import os
import time

app = Flask(__name__)

LOG_FILE = '/app/logs/alerts/alerts.json'

def classify_alert(alert):
    rule = alert.get("rule", {})
    rule_id = int(rule.get("id", 0))
    description = rule.get("description", "").lower()
    groups = rule.get("groups", [])
    
    # Classification Logic
    if any(id in [5710, 5711, 5712, 5715, 5716, 5720, 5760, 5763] for id in [rule_id]) or "brute force" in description or "authentication failed" in description:
        return "SSH Brute Force"
    elif any(id in [5401, 5402, 5501] for id in [rule_id]) or "sudo" in description or "privilege escalation" in description or "root executed" in description:
        return "Privilege Escalation"
    elif "shell" in description or "reverse" in description:
        return "Reverse Shell"
    elif "docker" in groups or "docker" in description:
        return "Docker Security"
    elif any(id in [550, 554] for id in [rule_id]) or "syscheck" in groups or "integrity" in description:
        return "File Integrity"
    
    return "Detection Event"

def get_alerts():
    alerts = []
    if not os.path.exists(LOG_FILE):
        return []
    
    try:
        with open(LOG_FILE, 'r') as f:
            # Read last 100 lines
            lines = f.readlines()[-100:]
            for line in lines:
                try:
                    alert = json.loads(line)
                    # Filter out level 0 or 2 (too noisy)
                    if alert.get("rule", {}).get("level", 0) <= 2:
                        continue
                        
                    simplified = {
                        "timestamp": alert.get("timestamp"),
                        "level": alert.get("rule", {}).get("level"),
                        "description": alert.get("rule", {}).get("description"),
                        "attack_type": classify_alert(alert),
                        "agent": alert.get("agent", {}).get("name", "Unknown"),
                        "srcip": alert.get("data", {}).get("srcip", "internal"),
                        "id": alert.get("id")
                    }
                    alerts.append(simplified)
                except:
                    continue
    except Exception as e:
        print(f"Error reading alerts: {e}")
    
    return alerts[::-1] # Newest first

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/alerts')
def api_alerts():
    return jsonify(get_alerts())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
