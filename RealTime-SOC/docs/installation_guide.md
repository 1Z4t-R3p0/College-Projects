# 📋 Installation Guide
## RealTime-SOC — Wazuh Docker SOC Stack

---

## System Requirements

| Component     | Minimum       | Recommended     |
|--------------|---------------|-----------------|
| OS           | Ubuntu 22.04  | Ubuntu 22.04 LTS|
| RAM          | 8 GB          | 16 GB           |
| CPU          | 4 cores       | 8 cores         |
| Disk         | 50 GB         | 200 GB SSD      |
| Docker       | 24.0+         | Latest          |
| Compose      | v2.20+        | Latest          |

---

## Step 1: Install Docker

```bash
# Remove old Docker versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt-get update && sudo apt-get install -y \
  ca-certificates curl gnupg lsb-release

# Add Docker GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update && sudo apt-get install -y \
  docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable and start Docker
sudo systemctl enable docker && sudo systemctl start docker

# Add your user to the docker group (re-login required after)
sudo usermod -aG docker $USER
```

---

## Step 2: Set Kernel Parameters for OpenSearch

Wazuh Indexer (OpenSearch) requires elevated `vm.max_map_count`:

```bash
# Apply immediately
sudo sysctl -w vm.max_map_count=262144

# Make permanent
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

---

## Step 3: Clone the Project

```bash
git clone <your-repo-url>
cd RealTime-SOC
```

---

## Step 4: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```ini
INDEXER_PASSWORD=YourStrongPassword      # ← CHANGE THIS
TELEGRAM_BOT_TOKEN=<your_bot_token>
TELEGRAM_CHAT_ID=<your_chat_id>
DISCORD_WEBHOOK_URL=<your_webhook_url>
```

> **How to get a Telegram Bot Token:**
> 1. Open Telegram → search `@BotFather`
> 2. Send `/newbot` and follow the prompts
> 3. Copy the generated token into `.env`
> 4. To get your chat ID: send a message to your bot, then visit:
>    `https://api.telegram.org/bot<token>/getUpdates`

---

## Step 5: Set Script Permissions

```bash
chmod +x active-response/block-ip.sh
chmod +x scripts/alert_webhook.py
chmod +x scripts/simulate_attack.sh
```

---

## Step 6: Deploy the Stack

```bash
docker compose up -d
```

Expected startup order (allow 3–5 minutes for full initialization):
1. `wazuh.indexer` — OpenSearch bootstraps and becomes healthy
2. `wazuh.manager` — Filebeat connects to indexer, API starts
3. `wazuh.dashboard` — Web UI loads
4. `wazuh.agent` — Registers with manager
5. `suricata` — Begins packet capture

---

## Step 7: Verify Deployment

### Check all containers are running:
```bash
docker compose ps
```

All services should show status `Up` (not `Exiting`).

### Check Wazuh Manager API:
```bash
curl -k -u admin:SecretPassword https://localhost:55000/
```

### Check Indexer health:
```bash
curl -k -u admin:SecretPassword https://localhost:9200/_cluster/health?pretty
```

### Verify Agent registration:
```bash
docker exec wazuh.manager /var/ossec/bin/agent_control -la
```

### Check active alerts:
```bash
docker exec wazuh.manager tail -f /var/ossec/logs/alerts/alerts.json
```

---

## Step 8: Access the Dashboard

1. Browse to: **https://localhost**
2. Accept the self-signed certificate warning
3. Login with:
   - Username: `admin`
   - Password: `SecretPassword` (or what you set in `.env`)

---

## Troubleshooting

### Problem: wazuh.indexer exits immediately
**Cause:** `vm.max_map_count` is too low.
```bash
sudo sysctl -w vm.max_map_count=262144
```

### Problem: Agent not appearing in dashboard
**Cause:** Registration password mismatch.
```bash
docker compose restart wazuh.agent
docker exec wazuh.manager tail -f /var/ossec/logs/ossec.log
```

### Problem: Suricata not capturing packets
**Cause:** Wrong default interface.
```bash
ip link show   # Find your interface name (e.g., eth0, ens33)
```
Edit `config/suricata/suricata.yaml` → change `interface: default` to your interface.

### Problem: Dashboard shows "No data"
**Cause:** Indexer not yet ready when manager started.
```bash
docker compose restart wazuh.manager
```

---

## Uninstall

```bash
# Stop and remove containers + volumes (full wipe)
docker compose down -v

# Remove images (optional)
docker rmi wazuh/wazuh-manager:4.9.0 wazuh/wazuh-indexer:4.9.0 \
           wazuh/wazuh-dashboard:4.9.0 wazuh/wazuh-agent:4.9.0 \
           jasonish/suricata:latest
```
