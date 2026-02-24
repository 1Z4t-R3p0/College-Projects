# 🏗️ SOC Architecture & Network Flow

## System Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Host (Linux)                        │
│                                                                   │
│  ┌─── soc_net (bridge) ─────────────────────────────────────┐   │
│  │                                                           │   │
│  │  ┌────────────────┐        ┌────────────────────────┐    │   │
│  │  │ wazuh.indexer  │◄──────►│    wazuh.manager       │    │   │
│  │  │ (OpenSearch)   │  9200  │  (SIEM Engine)         │    │   │
│  │  │ Port: 9200     │        │  Ports: 1514,1515,55000│    │   │
│  │  └────────────────┘        └──────────┬─────────────┘    │   │
│  │                                       │                   │   │
│  │                              Rules/Active Response        │   │
│  │                                       │                   │   │
│  │  ┌────────────────┐        ┌──────────▼─────────────┐    │   │
│  │  │ wazuh.dashboard│◄──────►│    wazuh.agent         │    │   │
│  │  │ (Web UI HTTPS) │  55000 │  (Endpoint Monitor)    │    │   │
│  │  │ Port: 443→5601 │        │  Monitors host logs    │    │   │
│  │  └────────────────┘        └────────────────────────┘    │   │
│  │                                                           │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌── host network ───────────────────────────────────────────┐   │
│  │  suricata (network IDS)                                   │   │
│  │  Captures all packets → /var/log/suricata/eve.json        │   │
│  │  Mounted into wazuh.agent via shared volume               │   │
│  └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    browser / API clients
```

---

## 🔗 Communication Flows

### 1. Agent → Manager (Log Forwarding)
- **Protocol:** TCP port 1514 (encrypted with TLS)
- **Data:** Syslog events, FIM changes, Docker events, Suricata EVE JSON
- **Flow:**
  ```
  wazuh.agent → (1514/TCP TLS) → wazuh.manager
  ```

### 2. Agent Registration
- **Protocol:** TCP port 1515
- **Method:** Password-based auto-registration (`WAZUH_REGISTRATION_PASSWORD`)
- **Flow:**
  ```
  wazuh.agent → (1515/TCP) → wazuh.manager
  ```

### 3. Manager → Indexer (Alert Storage)
- **Protocol:** HTTPS port 9200 (OpenSearch API)
- **Filebeat** ships alerts from Manager into the Indexer
- **Flow:**
  ```
  wazuh.manager (filebeat) → (9200/HTTPS) → wazuh.indexer
  ```

### 4. Dashboard → Manager API
- **Protocol:** HTTPS port 55000
- Agent/rule management calls from UI
- **Flow:**
  ```
  wazuh.dashboard → (55000/HTTPS) → wazuh.manager
  ```

### 5. Dashboard → Indexer
- **Protocol:** HTTPS port 9200
- Reads alert indices for visualization
- **Flow:**
  ```
  wazuh.dashboard → (9200/HTTPS) → wazuh.indexer
  ```

### 6. Suricata → Agent (Log Sharing)
- **Mechanism:** Named Docker volume `suricata-logs`
- Suricata writes `/var/log/suricata/eve.json`
- Wazuh Agent reads the same volume and ships events to Manager
- **Flow:**
  ```
  suricata → [volume: suricata-logs] → wazuh.agent → wazuh.manager
  ```

### 7. Active Response: IP Blocking
- Manager triggers `custom-block-ip.sh` on the agent upon rule match
- **Flow:**
  ```
  wazuh.manager → (active response) → wazuh.agent → iptables DROP <src_ip>
  ```

### 8. Alert Integrations: Telegram / Discord
- Manager calls `custom_webhook` Python script when alert level ≥ 7
- **Flow:**
  ```
  wazuh.manager → custom_webhook.py → Telegram API / Discord Webhook
                                    → incident_report JSON (local)
  ```

---

## 🌐 Network Isolation

| Service         | Network Mode    | Exposed Ports       |
|----------------|----------------|---------------------|
| wazuh.indexer  | `soc_net`       | `9200` (internal)   |
| wazuh.manager  | `soc_net`       | `1514`, `1515`, `55000`, `514/udp` |
| wazuh.dashboard| `soc_net`       | `443 → 5601`        |
| wazuh.agent    | `soc_net`       | None (outbound only)|
| suricata       | `host`          | None (packet cap)   |

> Suricata uses `network_mode: host` to access the physical NIC for full-packet capture. All other services are isolated in the `soc_net` bridge network.

---

## 📁 Volume Mapping

| Volume                        | Mount Path              | Service          |
|------------------------------|------------------------|------------------|
| `wazuh-indexer-data`         | `/usr/share/wazuh-indexer/data` | Indexer |
| `wazuh-manager-logs`         | `/var/ossec/logs`      | Manager          |
| `wazuh-manager-etc`          | `/var/ossec/etc`       | Manager          |
| `suricata-logs`              | `/var/log/suricata`    | Suricata + Agent |
| `./rules/local_rules.xml`    | `/var/ossec/etc/rules/local_rules.xml` | Manager (bind mount) |
| `./active-response/block-ip.sh` | `/var/ossec/active-response/bin/custom-block-ip.sh` | Manager (bind mount) |
